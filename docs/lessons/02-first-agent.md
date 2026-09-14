# 2교시 · KnowledgeAgent + yaml 프롬프트 + AgentResult

날짜: 2026-09-11 · Step 2 · 상태: 완료 · 커밋 `e78a904`

## 목표
LLM 호출을 "에이전트" 모양(프롬프트 파일 + LLM 담당자 + 결과 상자)으로 바꾼다. 앞으로 만들 모든 에이전트가 같은 모양.

## 만든 파일
- `mini_mas/prompts/knowledge.yaml`: `system`, `user` 키. `{today}`, `{query}` 빈칸.
- `mini_mas/prompts/__init__.py`: `render(name, **slots) -> (system, user)`. 빈칸 누락 시 `KeyError`(일부러).
- `mini_mas/schemas.py`: `AgentResult(name, text, docs=[], metadata={})`.
- `mini_mas/agents/__init__.py` (빈 파일), `mini_mas/agents/knowledge.py`: `KnowledgeAgent(llm=None).run(query)`.
- `mini_mas/ask.py`: 에이전트 호출로 변경.

## 핵심 개념
- 에이전트 `run` 은 세 줄 구조: 빈칸 채우기 → LLM 호출 → 상자에 담기.
- 프롬프트는 코드가 아니라 데이터(yaml). 코드 수정 없이 답변 스타일이 바뀐다.
- `llm=None` 주입 가능 → 3교시에서 가짜 LLM 으로 테스트.
- `metadata["block_type"]="general"`: Step 4 합성기가 결과 배치 순서에 쓴다 (원본과 동일 방식).
- `field(default_factory=list)`: 가변 기본값 공유 함정 회피.

## 실험
- yaml 의 "3문장" → "1문장" 만 바꿔도 답이 짧아짐.
- `render('knowledge', today='x')` → `KeyError: 'query'`.

## 다음 교시
- 3교시: FakeLLM 으로 유닛 테스트.
