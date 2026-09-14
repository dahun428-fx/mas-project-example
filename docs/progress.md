# 진행표

마지막 갱신: 2026-09-11 · 현재 위치: **Step 3 / 4교시 (실행 확인 중)**

## 교시 단위 (실제 진행 기록)

| 교시 | 제목 | Step | 상태 | 기록 |
|---|---|---|---|---|
| 0 | 환경 준비 (venv, .env, 골격 커밋) | 0 | 완료 | [00](lessons/00-setup.md) |
| 1 | OpenAI 호출 1회로 답 받는 CLI | 2 | 완료 | [01](lessons/01-openai-call.md) |
| 2 | KnowledgeAgent + yaml 프롬프트 + AgentResult | 2 | 완료 | [02](lessons/02-first-agent.md) |
| 3 | FakeLLM 으로 유닛 테스트 · **CP1** | 2 | 완료 | [03](lessons/03-fake-llm-tests.md) |
| 4 | NumbersAgent(검진 컨텍스트) + ChatAgent | 3 | 진행 중 | [04](lessons/04-three-agents.md) |
| 5 | LLM 분류기 (질문 → 에이전트 선택) | 3 | 대기 | |
| 6 | 오케스트레이터 연결 + 골든셋 정확도 | 3 | 대기 | |
| 7 | 병렬 실행 (asyncio) | 4 | 대기 | |
| 8 | 합성기 merge → refine → guard | 4 | 대기 | |
| 9 | FastAPI SSE 스트리밍 · **CP2** | 5 | 대기 | |
| … | Step 6~12 는 Doc 20 참조 | | | |

## Step 단위 (커리큘럼 Doc 20 기준)

| Step | 내용 | 상태 | 수락 기준 |
|---|---|---|---|
| 0 | 환경 · 사전 지식 요약 | 완료 | pytest 수집 성공, .env 키 |
| 1 | 전체 그림 잡기 (원본 정적 추적) | 선택 (보류) | `docs/worksheets/step01.md` |
| 2 | 단일 에이전트 | **완료 (CP1)** | FakeLLM 테스트 초록 |
| 3 | 의도 분류 · 라우팅 | 진행 중 | 골든셋 30문항 인텐트 ≥85%, 에이전트 ≥90% |
| 4 | 병렬 실행 · 합성 | 대기 | 직렬 대비 지연 단축 + 부분 실패 3케이스 |
| 5 | 스트리밍 · 이벤트 계약 | 대기 | 브라우저 2에이전트 병렬 · CP2 |
| 6 | 규칙 계층 | 대기 | pytest 25개 |
| 7 | RAG | 대기 | 질문 10 × top-3 적중표 |
| 8 | 메모리 | 대기 | 세션 넘어 사실 2개 반영 |
| 9 | 관측 · 비용 | 대기 | 턴 20개 리포트 |
| 10 | 평가 | 대기 | single vs multi 비교표 · CP3 |
| 11 | 안전 · 운영 | 대기 | compose up 한 번에 기동 |
| 12 | 캡스톤 | 대기 | 원본 PR 2건 + ADR · CP4 |

## 다른 컴퓨터에서 이어가기

```bash
git clone https://github.com/dahun428-fx/mas-project-example.git && cd mas-project-example
python3.12 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
cp .env.example .env && echo "OPENAI_API_KEY=sk-..." > .env     # 키는 리포에 없음
python -m pytest                                                 # 초록 확인
```
그 다음 Claude 에게 "CLAUDE.md 읽고 이어서 진행해줘" 라고 하면 된다.
