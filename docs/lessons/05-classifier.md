# 5교시 · LLM 분류기 + ROUTE_MAP 라우팅

날짜: 2026-09-14 · Step 3 · 상태: 완료 · 커밋 `442b75c` · 테스트 11 passed

## 목표
사용자가 `--agent` 를 고르지 않아도, LLM 이 질문을 읽고 담당 에이전트를 고른다. LLM 의 답은 코드가 검증하고 실패 시 안전한 기본값(chat)으로 떨어진다.

## 만든 파일
- `mini_mas/prompts/classifier.yaml`: 담당 3개를 "언제 쓰는지" 예시로 설명, 규칙("내/작년/추이" → numbers, 애매하면 knowledge), JSON 만 출력.
- `mini_mas/router.py`: `ROUTE_MAP = {numbers, knowledge, chat → 클래스}`, `FALLBACK_AGENT = "chat"`, `resolve(key)`. (ask.py 의 AGENTS 표를 이동)
- `mini_mas/classifier.py`: `parse_json(text)` (정규식 `\{.*\}` + DOTALL 로 코드펜스·잡말 제거), `classify(query, llm=None) -> {agent, reason, fallback, raw}`. 검증 2겹: JSON 파싱 실패 / agent 가 ROUTE_MAP 에 없음 → fallback.
- `mini_mas/ask.py`: `--agent` 없으면 `classify()` 결과로 `resolve()`. 첫 줄에 `[분류] agent=… · reason` 출력.
- `tests/unit/test_classifier.py`: 정상 JSON / 코드펜스 JSON / 미등록 agent / 잡문 / 깨진 JSON 5개.

## 핵심 개념
- 라우팅 = LLM 판단 + 코드 검증 + 정적 표. 셋 중 하나만 있으면 안 된다.
- 폴백을 chat 으로 두는 이유: 잘못 가도 피해가 가장 작다(수치를 지어낼 위험 없음).
- `fallback: True` 를 남겨 두면 나중에 분류 실패율을 셀 수 있다.
- 분류기 max_tokens 는 작게(JSON 한 줄). 매 질문마다 도는 비용이다.
- 원본 대응: `chatbot/orchestrator/intent_classifier.py`(같은 정규식 파싱, 폴백 INT101), `agent_capabilities.py`(담당 설명의 단일 출처), `agent_resolver.py`(ROUTE_MAP).

## 실험
- "애매하면 knowledge" 규칙을 지우면 한 단어 질문("혈압")의 담당이 흔들린다. 6교시에서 정확도로 잰다.

## 다음 교시
- 6교시: `Orchestrator` 로 분류→실행 묶기, 골든셋 30문항 라우팅 정확도 측정 (수락 기준: 에이전트 정확도 ≥ 90%).
