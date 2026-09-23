# 12교시 · 관측성과 비용 (SQLite 트레이스)

날짜: 2026-09-23 · Step 9 · 상태: 구현 완료 · 테스트 71 passed · ruff clean

## 목표
화면에 찍히고 사라지는 시간·토큰을 저장한다. "어느 담당이 제일 비싼가", "턴당 평균 몇 초인가" 에 숫자로 답한다.

## 만든 파일
- `mini_mas/trace.py`
  - `ContextVar` 2개(`_trace_id`, `_seq`). `new_trace()` 가 턴마다 새 id 발급 + seq 리셋.
  - `PRICES` 단가표, `compute_cost(model, in, out)`.
  - `record(...)` — 행을 만들어 **큐에 던지고 즉시 반환**.
  - `_worker(q)` — 데몬 스레드가 큐에서 꺼내 SQLite 에 INSERT. `flush()` 는 큐가 빌 때까지 대기.
- `mini_mas/llm.py`: `OpenAILLM(model, agent="...")`, `invoke` 끝에서 `record(...)`.
- `mini_mas/rag.py`: `embed()` 에도 `record(agent="RAG")`. 임베딩도 비용이다.
- `mini_mas/orchestrator.py`: `astream` 시작에서 `new_trace(query)`, `status` 이벤트에 `trace_id` 포함.
- `mini_mas/ask.py`: 마지막에 `flush()`.
- `eval/trace_report.py`: 최근 N턴 합계 / 담당별 비용·지연 / p50·p95 / 오류·잘림 건수 / 최근 3턴 호출 순서.
- `tests/unit/test_trace.py` 5개, `tests/unit/conftest.py` 에 `no_network_embed` autouse 픽스처.

## 핵심 개념
- **ContextVar = 지금 실행 중인 작업에 붙는 메모지.** 인자로 넘기지 않아도 깊은 함수가 읽는다. 전역변수와 달리 동시 요청끼리 섞이지 않는다.
- **기록이 응답을 늦추면 안 된다.** 디스크 쓰기를 요청 경로에서 빼고 큐 + 워커 스레드로 미룬다. 큐에 `maxsize` 를 둬 메모리 폭주를 막는다.
- **`flush()` 가 필요한 이유**: 데몬 스레드는 프로그램 종료를 막지 않는다. CLI 가 그냥 끝나면 기록이 날아간다.
- **단가표에 없는 모델은 비용 0으로 집계된다.** 조용히 공짜가 되는 사고. 모델을 추가하면 단가도 같이 추가한다. (원본에서 실제로 난 사고 — 문서집 Doc 18)
- **지연은 평균이 아니라 p50·p95 로 본다.** 가끔 한 번 크게 느린 호출에 평균이 끌려간다.
- 질문에 따라 턴당 호출 수가 2회("안녕": 분류기+Chat)에서 5회("내 LDL 높은데 뭘 먹어야 돼?": 분류기+RAG 임베딩+Numbers+Knowledge+합성기)까지 벌어진다.

## 겪은 문제 (전부 타이핑 실수, 증상이 제각각)
- `_seq = ContextVar[int] = ContextVar(...)` — 콜론이 등호로. `TypeError: 'type' object does not support item assignment`.
  import 사슬 맨 아래가 깨져 **conftest 로딩부터 실패**, 테스트가 하나도 안 돌았다.
- `threading.Thread(args=(_queue))` — 쉼표 없는 괄호는 튜플이 아니다. 워커 스레드가 시작 즉시 죽고, 큐를 아무도 비우지 않아 **`flush()` 가 영원히 대기** → pytest 가 멈춤.
  메인 코드는 멀쩡히 돌아 화면에 아무 표시가 없었다. **백그라운드 작업은 조용히 죽는다.** 워커에 예외 로깅이 필요한 이유.
- SQL 문자열: `INTER INTO`, 컬럼 `" latency_ms"`(앞 공백), `"fininsh_reason"` → 기록이 조용히 실패(`[trace] 기록 실패: ' latency_ms'`).
- `while _lock:` — `with _lock:` 이어야 한다. 잠금이 아니라 무한 반복이 된다.
- 테스트가 **실제 임베딩 API 를 호출**해 느려짐 → `conftest.py` 에 `autouse=True` 픽스처로 `rag.embed` 를 가짜로 교체.
- `Retriever` 가 인덱스 파일 없으면 예외 → 빈 인덱스로 동작하고 안내 문구를 찍도록 수정(새 환경에서 바로 안 터지게).
- 내가 준 테스트 2개도 틀렸다: `[0.71, 0.71]` 은 두 문서와 cosine 0.707 이라 threshold 를 넘는다 → `[-1.0, -1.0]` 으로 교체. "가짜 LLM 은 기록 안 함" 은 **DB 파일이 안 생기는지**로 검사하는 게 정확하다.

## 남은 확인
```bash
python -m eval.trace_report      # 턴당 호출 수·비용·p50/p95
python -m eval.rag_eval          # 11교시 수락 기준 top-3 ≥ 90%
```

## 다음 교시
- 13교시 (Step 10): 평가. 같은 질문을 담당 1개(single)와 여러 개(multi)로 돌려 LLM judge 로 품질을 채점하고,
  12교시의 비용 데이터를 "품질 향상의 대가" 로 함께 놓는다 (CP3).
