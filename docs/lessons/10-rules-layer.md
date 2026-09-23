# 10교시 · 규칙 계층 (연도 정규화 · 컨텍스트 필터 · 환각 가드)

날짜: 2026-09-18 · Step 6 · 상태: 완료 · 테스트 59 passed · ruff clean

## 목표
4교시에 프롬프트로 "없는 수치는 만들어 내지 않습니다" 라고 **부탁**했다. 코드로 강제한다.

## 흐름
```
질문 → ① resolve_years (규칙) → ② filter_checkups (규칙) → ③ build_checkup_context (규칙)
     → ④ render → ⑤ llm.invoke (LLM 1회) → ⑥ guard_years (규칙) → AgentResult
```
앞 세 단계가 **무엇을 보여줄지**, 마지막 단계가 **무엇을 말했는지**를 담당한다. LLM 은 한가운데 한 번뿐.

## 만든 파일
- `mini_mas/year.py`: `resolve_years(query, today) -> list[str]`. 순서 — ALL 패턴 즉시 반환 / 연-월 / 쉼표 나열 / 단일 연도 / 두 자리 / N년 전 / 상대 표현.
- `mini_mas/context.py`: `available_years`, `filter_checkups(data, years) -> (matched, missing)`, `build_checkup_context(data, years=None)`.
- `mini_mas/guard.py`: `find_unknown_years`, `guard_years(text, allowed) -> (text, unknown)`.
- `mini_mas/agents/numbers.py`: 연도 해석 → 필터 → 호출 → 가드. metadata 에 `years`, `hallucinated_years`.
- `mini_mas/prompts/numbers.yaml`: "보유 검진 연도에 없는 연도는 언급하지 않는다, [없음] 표시가 있으면 없다고 답한다" 규칙 추가.
- 테스트 21개 추가: `test_year.py`(parametrize 12), `test_numbers_agent.py`(필터·컨텍스트 5), `test_guard.py`(4).

## 핵심 개념
- **빈 목록 `[]` 과 `["ALL"]` 은 다르다.** 전자는 연도를 안 물은 것, 후자는 전부 달라는 것.
- **없는 연도를 버리지 않고 `missing` 으로 챙긴다.** 그냥 빼면 LLM 은 왜 없는지 모른 채 침묵하거나 지어낸다. `[없음]` 줄로 말해 준다.
- **보유 연도 목록을 항상 프롬프트에 넣는다.** LLM 이 울타리를 알아야 한다.
- **가드는 답변을 통째로 교체한다.** 지어낸 연도가 하나면 나머지도 믿을 수 없다. 의료 도메인은 "틀린 답보다 무응답".
- **프롬프트는 확률, 코드는 확실.** 프롬프트로 좋은 답을 유도하고 코드로 최악을 막는다. 둘 다 필요하다.
- 한계: 가드는 연도만 본다. "2025년 공복혈당 150" 처럼 수치를 틀리면 못 잡는다. 정상 범위·계산값과 구분이 어려워 오탐이 늘기 때문. 원본도 이 부분은 프롬프트와 평가로 관리한다.
- 원본 대응: `chatbot/policy/slot_postprocess.py`(SLT008 연도 정규화), `chatbot/orchestrator/context_extractor.py`(연도 스냅), `chatbot/orchestrator/grounding.py`(`guard_medical_answer` → `strict_no_data_answer`).

## 겪은 문제
- **연도 정규식끼리 잡아먹기.** "2024년 3월" 에서 연-월 패턴이 `2024-03` 을 넣은 뒤 단일 연도 패턴이 `2024` 를 또 넣음 → 단일 연도에 `(?!\s*\d{1,2}\s*월)` 부정 전방탐색 추가. "2023, 2024년" 은 앞 연도에 "년" 이 없어 누락 → 쉼표 나열 패턴 추가. **테스트 12개를 먼저 쓴 게 이번 교시 설계의 핵심.**
- `build_checkup_context` 의 `return` 과 `if missing:` 이 for 문 **안**에 들어감 → 첫 검진만 처리하고 반환, 검진이 0건이면 `None` 반환(`TypeError: argument of type 'NoneType' is not iterable`). 9교시 `arun` 과 같은 실수 **두 번째**. `return` 을 쓸 때 for 와 같은 높이인지 확인하는 습관.
- `guard_years` 결과를 받아 놓고 `AgentResult(text=resp.text)` 로 원본을 넣음 → **가드가 돌지만 결과가 버려지는** 상태. 테스트가 없었다면 "가드를 붙였다"고 믿은 채 넘어갔을 버그.
- `"사용자 : "` 콜론 앞 공백 → 테스트가 형식을 고정. 프롬프트 형식이 바뀌면 답변도 미묘하게 달라진다.
- ruff: 같은 이름 테스트 함수 2개(`F811`) — 파이썬은 나중 것으로 덮어써 **앞 테스트가 조용히 사라진다**. import 가 파일 중간(`E402`). 나머지 33개는 `--fix` 로 자동 정리.

## 다음 교시
- 11교시 (Step 7): RAG. 일반 의학 지식 문서를 임베딩해 검색하고, `KnowledgeAgent` 가 근거 문서를 인용해 답한다.
