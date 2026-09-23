# 진행표

마지막 갱신: 2026-09-23 · 현재 위치: **Step 9 / 12교시 (관측성·비용) 시작**

## 교시 단위 (실제 진행 기록)

| 교시 | 제목 | Step | 상태 | 기록 |
|---|---|---|---|---|
| 0 | 환경 준비 (venv, .env, 골격 커밋) | 0 | 완료 | [00](lessons/00-setup.md) |
| 1 | OpenAI 호출 1회로 답 받는 CLI | 2 | 완료 | [01](lessons/01-openai-call.md) |
| 2 | KnowledgeAgent + yaml 프롬프트 + AgentResult | 2 | 완료 | [02](lessons/02-first-agent.md) |
| 3 | FakeLLM 으로 유닛 테스트 · **CP1** | 2 | 완료 | [03](lessons/03-fake-llm-tests.md) |
| 4 | NumbersAgent(검진 컨텍스트) + ChatAgent | 3 | 완료 | [04](lessons/04-three-agents.md) |
| 5 | LLM 분류기 (질문 → 에이전트 선택) | 3 | 완료 | [05](lessons/05-classifier.md) |
| 6 | 오케스트레이터 연결 + 골든셋 정확도 | 3 | 완료 (30문항 96.7~100%) | [06](lessons/06-orchestrator-golden-set.md) |
| 7 | 병렬 실행 (asyncio) | 4 | 완료 | [07](lessons/07-parallel-agents.md) |
| 8 | 합성기 merge → refine → guard | 4 | 완료 | [08](lessons/08-synthesizer.md) |
| 9 | FastAPI SSE 스트리밍 · **CP2** | 5 | 완료 (CP2) | [09](lessons/09-sse-server.md) |
| 10 | 규칙 계층 (연도·컨텍스트·환각 가드) | 6 | 완료 | [10](lessons/10-rules-layer.md) |
| 11 | RAG (지식 문서 검색) | 7 | 구현 완료 (테스트·평가 작성 중) | [11](lessons/11-rag.md) |
| 12 | 관측성·비용 (SQLite 트레이스) | 9 | 진행 중 | |
| … | Step 6~12 는 Doc 20 참조 | | | |

## Step 단위 (커리큘럼 Doc 20 기준)

| Step | 내용 | 상태 | 수락 기준 |
|---|---|---|---|
| 0 | 환경 · 사전 지식 요약 | 완료 | pytest 수집 성공, .env 키 |
| 1 | 전체 그림 잡기 (원본 정적 추적) | 선택 (보류) | `docs/worksheets/step01.md` |
| 2 | 단일 에이전트 | **완료 (CP1)** | FakeLLM 테스트 초록 |
| 3 | 의도 분류 · 라우팅 | **완료** | 골든셋 30문항 에이전트 ≥90% → 96.7~100% |
| 4 | 병렬 실행 · 합성 | **완료** | 부분 실패 3케이스 통과, 벤치마크 스크립트 |
| 5 | 스트리밍 · 이벤트 계약 | **완료 (CP2)** | 브라우저에서 2담당 병렬 + 진행 표시 |
| 6 | 규칙 계층 | **완료** | 연도/컨텍스트/가드 테스트 21개 (총 59) |
| 7 | RAG | 진행 중 | 질문 10 × top-3 적중표 |
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
