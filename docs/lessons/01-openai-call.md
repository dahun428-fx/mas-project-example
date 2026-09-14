# 1교시 · OpenAI 호출 1회로 답 받는 CLI

날짜: 2026-09-10 · Step 2 · 상태: 완료 · 커밋 `bdb3bb4`

## 목표
`python -m mini_mas.ask "공복혈당이 뭐야?"` 가 답을 출력한다.

## 만든 파일
- `mini_mas/__init__.py` (빈 파일, 패키지 표시)
- `mini_mas/llm.py`: `LLMResponse`(text, model, input_tokens, output_tokens, finish_reason, latency_ms) + `OpenAILLM(model).invoke(system, user, max_tokens=512)`
- `mini_mas/ask.py`: argv 로 질문 받아 호출·출력

## 핵심 개념
- system(역할 지시) / user(질문) 분리가 기본 습관.
- 답 텍스트만 받지 않고 상자(`LLMResponse`)에 담는 이유: 토큰(비용), 지연, `finish_reason`(잘림 감지)을 나중에 쓴다.
- `max_completion_tokens` 로 답 길이 상한. `finish_reason == "length"` 면 잘린 것.

## 실험
- `max_tokens=8` → 답이 끊기고 `finish=length`.
- 모델명 오타 → API 오류. (Step 3 에서 화이트리스트로 미리 막는다.)

## 겪은 문제
- `__init__.py` 를 리포 루트에 만들었음 → `mini_mas/` 안으로 이동.

## 다음 교시
- 2교시: 이 호출을 "에이전트" 모양으로 바꾼다 (yaml 프롬프트 + AgentResult).
