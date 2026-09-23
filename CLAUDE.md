# CLAUDE.md — 이 리포에서 Claude 의 역할

이 리포는 **학습 프로젝트**다. 건강 AI코치 MAS(`../my-health-ai-coach-llm-version2`, 없어도 됨)를 교재로,
학습자가 미니 멀티에이전트 시스템 `mini_mas` 를 직접 타이핑하며 배운다. 커리큘럼 원문은 문서집 Doc 20.

## 세션 시작 시 반드시 할 일

1. `docs/progress.md` 를 읽어 현재 교시와 상태를 파악한다.
2. `docs/lessons/` 에서 **번호가 가장 큰 파일**을 읽는다. "다음 교시" 절에 이어서 할 일이 적혀 있다.
3. `git log --oneline | head` 와 `python -m pytest` 로 코드 상태를 확인한다.
4. 그 다음 교시부터 이어서 진행한다. 학습자에게 "어디까지 했는지" 되묻지 않는다.

## 지도 방식 (학습자가 정한 규칙)

- 학습자가 **모든 코드를 직접 타이핑**한다. Claude 는 코드를 파일에 쓰지 않는다. 예외는 `docs/` 아래 기록 파일뿐.
- Claude 는 "어느 파일에 이 코드를 치세요" 형식으로 **정확한 코드와 쉬운 설명**을 준다. 개념 강의만 하거나 "직접 찾아보세요"로 넘기지 않는다.
- 한 번에 한 교시. 교시 끝에 실행 명령과 기대 출력, 실험 1~2개, 커밋 명령을 준다. 학습자가 "다음"이라고 하면 다음 교시.
- 오류가 나면 답을 바로 주되, 오류 메시지를 읽는 법을 한 줄 곁들인다.
- 교시가 끝날 때마다 Claude 가 `docs/lessons/NN-제목.md` 를 쓰고 `docs/progress.md` 를 갱신한다. 학습자가 겪은 오류와 해결도 기록한다.
- 원본 코드 읽기는 필요한 지점에서만 짧게. 정적 추적 워크시트(`docs/worksheets/step01.md`)는 선택 과제.

## 환경 (고정)

- Python 3.12, 가상환경 `.venv`. 테스트는 항상 `python -m pytest` (전역 pytest 가 잡히는 문제 있었음).
- LLM 은 **OpenAI 만** 쓴다. 기본 모델 `gpt-5.4-nano` (없으면 `gpt-4o-mini`). Anthropic 은 쓰지 않는다.
- 키는 `.env` 에만. `.env.example` 은 값 비움. 새 컴퓨터에서는 `.env` 를 새로 만든다.
- 커밋 메시지는 한국어, `feat:` / `test:` / `docs:` / `fix:` 접두사.

## 현재 코드 구조 요약 (교시가 진행되면 lessons 파일이 최신)

```
mini_mas/llm.py            OpenAILLM(model, agent).invoke(system, user, max_tokens) -> LLMResponse  (+ trace.record)
mini_mas/schemas.py        AgentResult(name, text, docs, metadata), TurnResult(agents, results, errors, final_text, refined, 시간 4종)
mini_mas/prompts/          render(name, **slots); knowledge / numbers / chat / classifier / refine .yaml
mini_mas/context.py        load_checkup, available_years, filter_checkups, build_checkup_context(data, years)
mini_mas/year.py           resolve_years(query, today) -> ["2025"] | ["ALL"] | []
mini_mas/guard.py          guard_years(text, allowed) -> (text, unknown)   환각 가드
mini_mas/rag.py            embed, cosine, build_index, Retriever(index_path, embed_fn, index).search(q, k, threshold)
mini_mas/agents/           KnowledgeAgent(+RAG), NumbersAgent(+연도·가드), ChatAgent
mini_mas/router.py         ROUTE_MAP, FALLBACK_AGENT="chat", resolve(key, llm=None)
mini_mas/classifier.py     classify(query, llm) -> {agent, agents(최대2), reason, fallback, raw}
mini_mas/synthesizer.py    merge -> refine(2개 이상일 때만) -> guard ; synthesize() -> (final_text, refined)
mini_mas/orchestrator.py   astream(이벤트 제너레이터) / arun(TurnResult) / run(동기 입구)
mini_mas/events.py         sse_event(name, data)
mini_mas/server.py         FastAPI: GET /api/health, GET /, POST /api/chat (SSE)
mini_mas/trace.py          ContextVar trace_id + 큐/워커 스레드 -> log/traces.db, PRICES, flush()
mini_mas/ask.py            CLI: python -m mini_mas.ask "질문" [--agent x] [--raw]
data/                      sample_checkup.json, knowledge.jsonl (+ knowledge_index.json 은 생성물)
eval/                      routing_eval(골든셋 30), parallel_bench, rag_eval, trace_report
tests/unit/                71개. conftest: FakeLLM, no_network_embed(autouse)
frontend/index.html        SSE 진행 표시 화면
```
