# 4교시 · NumbersAgent(검진 컨텍스트) + ChatAgent

날짜: 2026-09-11 · Step 3 · 상태: **진행 중** (코드 작성 완료, 실행 3번 확인 남음)

## 목표
에이전트를 3개로 늘린다. 개인 수치 담당(NumbersAgent)은 검진 데이터를 프롬프트에 넣어 답한다.

## 만든 파일
- `data/sample_checkup.json`: 가상 사용자 "다나아" 2년치(2025-11-12, 2024-11-16) 5항목. 필드명은 원본과 동일(da_name, user_value, unit, normal_value, status).
- `mini_mas/context.py`: `load_checkup()`, `build_checkup_context(data) -> str` (LLM 이 읽기 좋은 줄글 표)
- `mini_mas/prompts/numbers.yaml`: "데이터에 있는 수치만, 없으면 '해당 기록이 없습니다'" 규칙. `{context}` 빈칸.
- `mini_mas/agents/numbers.py`: `NumbersAgent(llm=None, data=None)`, block_type `personal_numbers`
- `mini_mas/prompts/chat.yaml`, `mini_mas/agents/chat.py`: `ChatAgent`, max_tokens 128
- `mini_mas/ask.py`: `--agent {numbers,knowledge,chat}` (분류기 전까지 사람이 선택). `AGENTS` 딕셔너리 = 라우팅 표의 원형.
- `tests/unit/test_numbers_agent.py`: 컨텍스트 내용 / 프롬프트 주입 / chat max_tokens

## 핵심 개념
- 개인 데이터 질문은 데이터를 프롬프트에 **넣어 줘야** 답할 수 있다. 지금은 전체를 넣고, Step 6 에서 슬롯(항목·연도)으로 필터한다.
- "컨텍스트 밖 수치 금지"는 프롬프트로 부탁하고(지금) 코드로 검사한다(Step 6).
- 에이전트 셋의 `run` 구조는 동일. 다른 건 프롬프트·컨텍스트·block_type 뿐.

## 겪은 문제
- `open(path, encording=...)` 오타 → `encoding`. (오류는 맨 아래 줄부터 읽기)
- `DATA_PATH = Path(__file__).parent / "data"` → `mini_mas/data` 를 찾음. `.parent.parent` 로 리포 루트 기준으로 수정.

## 남은 확인
```bash
python -m mini_mas.ask --agent numbers "작년 공복혈당 어땠어?"
python -m mini_mas.ask --agent numbers "2020년 공복혈당은?"     # "기록 없음" 이어야 함. 지어내면 답을 기록해 둘 것 (Step 6 재료)
python -m mini_mas.ask --agent chat "안녕"
python -m pytest                                              # 6 passed
git add -A && git commit -m "feat: NumbersAgent(검진 데이터 컨텍스트) + ChatAgent"
```

## 다음 교시
- 5교시: LLM 분류기. 질문을 보고 `numbers / knowledge / chat` 중 하나를 JSON 으로 고르게 하고, 코드가 검증한 뒤 `AGENTS` 표로 연결.
