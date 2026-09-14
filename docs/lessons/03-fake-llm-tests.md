# 3교시 · FakeLLM 으로 유닛 테스트 (CP1)

날짜: 2026-09-11 · Step 2 · 상태: 완료 (CP1 통과)

## 목표
API 를 부르지 않고 에이전트가 맞게 동작하는지 검사한다.

## 만든 파일
- `tests/__init__.py`, `tests/unit/__init__.py` (빈 파일)
- `tests/unit/conftest.py`: `FakeLLM` (진짜와 같은 `invoke` 시그니처, `calls` 에 호출 기록) + `fake_llm` fixture
- `tests/unit/test_knowledge_agent.py`: 결과 상자 검사 / 질문이 user 프롬프트에 들어갔는지 / 빈칸 누락 KeyError

## 핵심 개념
- 가짜 LLM 은 진짜와 **같은 함수 이름·같은 반환 상자**만 지키면 에이전트가 구분 못 한다 → 끼워 넣기 가능.
- `conftest.py` 는 pytest 가 자동으로 읽는다. fixture 는 인자 이름으로 주입된다.
- pytest 실패 메시지 읽기: `-` 기대값, `+` 실제값, `?` 차이 위치.

## 겪은 문제
- `pytest` 가 전역(`/opt/homebrew/bin/pytest`)으로 실행돼 `No module named 'dotenv'` → **항상 `python -m pytest`**.
- `name = "Knowldge"` 오타를 테스트가 잡음 → 수정. (에이전트 이름은 Step 3 라우팅 표의 키가 되므로 중요.)

## 다음 교시
- 4교시: NumbersAgent(검진 데이터 컨텍스트) + ChatAgent, `ask.py --agent`.
