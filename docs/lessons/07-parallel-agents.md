# 7교시 · 담당 여러 개를 동시에 실행

날짜: 2026-09-16 · Step 4 · 상태: 완료 · 커밋 `08d6e3b`, `a48ba6b` · 테스트 21 passed

## 목표
6교시에서 #29("내 LDL 높은데 뭘 먹어야 돼?")가 실행마다 numbers ↔ knowledge 를 오갔다. 두 담당이 모두 필요한 질문이므로
(1) 분류기가 최대 2개를 고르고 (2) 동시에 실행하고 (3) 하나가 실패해도 나머지를 살린다.

## 파트 A · 분류기 다중 선택
- `mini_mas/prompts/classifier.yaml`: 출력이 `{"agent": "..."}` → `{"agents": [...]}`. 규칙 3줄 추가 (보통 1개 / 본인 기록+일반 지식이 둘 다 필요하면 2개 / chat 은 단독).
- `mini_mas/classifier.py`: `MAX_AGENTS = 2`, `normalize_agents(raw)` 추가.
  청소 4단계: 문자열이면 목록으로 감싸기(옛 형식 호환) → 미등록·중복 제거 → 다른 담당과 섞이면 chat 제거 → 상위 2개.
  반환에 `agent`(첫 담당)를 남겨 `eval/routing_eval.py` 를 고치지 않아도 되게 했다.
- 테스트 3개 추가: 두 담당 순서 유지 / chat 혼합 시 제거 / 중복·초과 제거.

## 파트 B · 동시 실행
- `tests/unit/conftest.py`: `FakeLLM(text, delay, error)` — 느린 LLM·고장 난 LLM 흉내.
- `mini_mas/schemas.py`: `TurnResult` 필드 변경. `agent→agents`, `result→results`, `errors` 추가, `agents_ms` 추가.
- `mini_mas/orchestrator.py`:
  - `run()` 은 `asyncio.run(self.arun(...))` 입구. 실제 로직은 `async def arun`.
  - 분류기도 `asyncio.to_thread` 로 호출 (나중에 웹 서버에서 다른 사용자를 막지 않게).
  - `asyncio.gather(*(self._run_one(key, query) for key in agents))` 로 동시 시작. 결과는 **시작한 순서**로 돌아온다.
  - `_run_one` 은 절대 예외를 밖으로 던지지 않고 `(결과, 오류메시지)` 를 돌려준다. 여기서 막지 않으면 gather 전체가 멈춰 성공한 담당의 답까지 버려진다. (원본 `_wrap_agent` 와 같은 역할)
  - `asyncio.wait_for(..., timeout=self.timeout_s)`, 기본 30초. `agent_llms` 로 담당별 LLM 주입(테스트용).
- `mini_mas/ask.py`: `--agent` 를 `action="append"` 로 여러 번 지정 가능. 담당별 답을 `──` 블록으로 출력, 실패는 사유 출력.
- 테스트 7개: 단일 라우팅 / 강제 지정 시 분류기 0회 / 분류 실패 → chat / **병렬(0.3초×2 인데 agents_ms < 500)** / 한쪽 예외 / 한쪽 타임아웃 / 전부 실패.

## 파트 C · 벤치마크
- `eval/parallel_bench.py`: 같은 질문을 담당 1개씩 두 번(차례로) vs 2개 한 번(동시에), 3회 반복 후 **중앙값** 비교.
  `force_agents` 로 분류기를 건너뛰어 담당 실행 시간만 잰다. 평균 대신 중앙값을 쓰는 이유는 API 지연의 이상치 때문.

## 핵심 개념
- 병렬이 이득인 이유는 계산이 아니라 **네트워크 대기**를 겹치기 때문. `to_thread` + `gather` 두 줄이 전부다.
- 속도는 2배가 아니라 1.7~1.9배 근처. 동시에 돌려도 **더 느린 쪽을 기다려야** 하기 때문.
- 타임아웃은 "응답을 포기"이지 "요청을 취소"가 아니다. 스레드는 계속 돌고 API 비용도 나간다. (타임아웃 테스트가 1초 걸리는 이유)
- 부분 실패 정책: 실패한 담당은 빼고 답하되 사유를 남긴다. 전부 실패면 안내 문구.
- 담당 수 상한을 코드에 박아 둔다. 늘어날수록 비용·지연이 선형으로 는다. (원본은 3개)

## 결과
- pytest 21 passed.
- 벤치마크: 학습자 실행 결과를 여기에 기록할 것 (차례로 중앙값 / 동시에 중앙값 / 단축률).

## 다음 교시
- 8교시: 합성기(Synthesizer). 지금은 답이 `── Numbers`, `── Knowledge` 두 덩어리로 따로 나온다.
  이를 사용자가 읽는 하나의 답으로 합친다. merge(규칙) → refine(LLM, 2개 이상일 때만) → guard(규칙).
