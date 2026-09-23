# 8교시 · 합성기 (merge → refine → guard)

날짜: 2026-09-17 · Step 4 · 상태: 완료 · 커밋 `9671b62`, `4fb972e` · 테스트 33 passed

## 목표
7교시에서 답이 `── Numbers`, `── Knowledge` 두 덩어리로 따로 나왔다. 사용자가 읽는 하나의 답으로 합친다.

## 구조
| 단계 | 방식 | 하는 일 |
|---|---|---|
| merge | 규칙 | `block_type` 순서(personal_numbers → general → recommendations)로 이어 붙임 |
| refine | LLM | 하나의 글로 다듬음. **답이 2개 이상일 때만** |
| guard | 규칙 | 헤더 제거, 단위 띄우기(138mg/dL → 138 mg/dL), 단정 표현 완화, 빈 줄 정리. **항상** |

LLM 을 가운데에만 쓴다. 순서는 규칙이어야 예측 가능하고, 마지막 정리도 규칙이어야 LLM 이 무시할 수 없다.

## 만든 파일
- `mini_mas/prompts/refine.yaml`: 편집자 역할. 새 정보 금지, 수치 그대로, 중복 제거, 본인 수치 먼저, 3~5문장, **내부 용어("담당","에이전트") 금지**.
- `mini_mas/synthesizer.py`: `merge`, `guard`(+ `_strip_headers`, `_space_units`, `_soften_assertions`), `refine`, `synthesize(results, query, llm) -> (final_text, refined)`.
- `mini_mas/schemas.py`: `TurnResult` 에 `final_text`, `refined`, `synth_ms` 추가.
- `mini_mas/orchestrator.py`: `synth_llm` 파라미터, `await asyncio.to_thread(synthesize, ...)`.
- `mini_mas/ask.py`: 최종 답 출력, `--raw` 로 담당별 원문도 표시, `[합성] refine|fast-path` 표시.
- 테스트 10개: merge 순서/빈 텍스트 제외, guard 4종, fast-path(LLM 0회), 2개일 때 LLM 1회, refine 실패 시 merged 폴백, 결과 없음 안내 문구.

## 핵심 개념
- **fast-path**: `len(results) < 2` 면 refine 을 건너뛴다. 담당 1개인 질문이 대다수라 LLM 1회와 1~2초를 아낀다. 테스트 `len(llm.calls) == 0` 으로 고정.
- **폴백 3중**: refine 예외 → merged / LLM 빈 응답 → `or merged` / 결과 없음 → `guard` 의 `or EMPTY_ANSWER`. 사용자가 빈 화면을 보는 경우가 없다.
- refine 에 넘어가는 재료는 **merged 글자 하나뿐**. LLM 은 AgentResult 도 담당 이름도 못 본다. 그래서 "Numbers 담당에 따르면" 같은 문장이 나올 수 없다.
- merge 는 `text` 와 `metadata["block_type"]` 만 쓴다. 담당을 추가해도 합성기를 고칠 필요가 없다.
- 원본 대응: `chatbot/synthesizer/synthesizer.py` 의 merge 버킷 3종, refine, `guard_and_polish` 와 같은 구조.

## 겪은 문제
- `render("refiner")` 로 호출했는데 파일은 `refine.yaml` → `FileNotFoundError`. 오류 메시지 끝 경로와 `ls mini_mas/prompts/` 를 비교하면 즉시 보인다.
- 이때 `refine` 의 `try` 가 LLM 호출만 감싸고 `render` 는 밖에 있어서 폴백에 걸리지 않고 그대로 터졌다. **의도한 설계**: 프롬프트 파일 누락은 배포 실수라 드러나야 하고, LLM 장애는 흔한 일이라 폴백한다. 무엇을 감쌀지가 try 의 설계.

## 다음 교시
- 9교시: FastAPI + SSE. 진행 상황을 실시간으로 브라우저에 보낸다 (CP2).
