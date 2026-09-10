# Step 1 워크시트: 요청 하나를 끝까지 따라가기 (4h)

원본 프로젝트(`../my-health-ai-coach-llm-version2`)의 코드를 **읽으며** 표를 채운다. 코드는 안 짠다.

> 원본을 실제로 띄우려면 Naver Clova(HCX) 키와 Anthropic 키가 필요하다. 지금은 OpenAI 키만 쓰기로 했으므로
> 이 워크시트는 **정적 추적(코드 읽기)** 버전이다. 나중에 키가 생기면 맨 아래 "선택: 실행 추적"을 추가로 한다.

교재 파일 한 개만 연다: `chatbot/orchestrator/orchestrator.py`, 함수 `run_scenario_stream_async` (125행부터 673행).
옆에 문서집 Doc 07(처리 흐름도)을 띄워 둔다.

## 1-A. 단계 표 채우기 (1.5h)

`run_scenario_stream_async` 를 위에서 아래로 읽으며, `progress` SSE 를 내보내는 지점마다 한 행씩 채운다.
`sse_event("progress", ...)` 또는 `progress_event(...)` 를 찾으면 그게 단계 경계다.

| # | 단계 이름 (stage 값) | 시작 행 | 규칙 / LLM | 쓰는 모델 (있으면) | 호출하는 함수 | 이 단계가 없으면 무엇이 깨지나 |
|---|---|---|---|---|---|---|
| 1 | prefilter | 176 | 규칙 | 없음 | `prefilter(query)` | |
| 2 | | | | | | |
| 3 | | | | | | |
| 4 | | | | | | |
| 5 | | | | | | |
| 6 | | | | | | |
| 7 | | | | | | |

힌트: 모델 이름은 `orchestrator.py` 에 직접 없을 수 있다. `chatbot/config/models.py` 와 `chatbot/orchestrator/labels.py` 에서 찾는다.

## 1-B. SSE 이벤트 순서 (45분)

같은 함수에서 `sse_event("...")` 의 첫 번째 인자를 **등장 순서대로** 모두 적는다. 분기(if/else)로 갈리는 곳은 들여쓰기로 표시.

```
prefilter 차단 시:
  1. progress(prefilter)
  2.
  ...
  n. status = "rejected"

정상 · 에이전트 1개 · stream=True:
  1.
  ...

정상 · 에이전트 2개 이상:
  1.
  ...
```

확인: 마지막 다섯 이벤트가 항상 `document → sigungu → result → suggestQuestions → status` 인가?
그 순서를 만드는 함수 이름과 행 번호: ______________________

## 1-C. 한 턴의 LLM 호출 수 세기 (45분)

아래 질문 3개에 대해 **코드를 근거로** LLM 호출 횟수를 추정한다. 각 호출마다 "어느 파일의 어느 함수가 어떤 모델을" 부르는지 적는다.

| 질문 | 예상 intent | 실행 에이전트 | LLM 호출 목록 (파일:함수 → 모델) | 합계 |
|---|---|---|---|---|
| 작년 공복혈당 어땠어? | INT104 | DataAnalysisAgent | 1) intent_classifier: _classify_haiku → claude-haiku … | |
| 공복혈당이 뭐야? | | | | |
| 안녕 | | | | |

찾아볼 곳: `intent_classifier.py`, `agents/data_analysis/prompt_helpers.py`(Context Extractor 호출), `agents/*/main.py`, `synthesizer/synthesizer.py`, `agents/suggest_questions/main.py`, `memory/setup.py` → `worker.py`.

질문: 셋 중 합성기(Synthesizer)가 LLM 을 **부르지 않는** 경우는 어느 것이고, 코드의 어떤 조건 때문인가? (힌트: 416행 근처)

## 1-D. 망가뜨리기 (코드로 답하기, 30분)

실행 대신 코드에서 경로를 찾아 답한다.

1. `ANTHROPIC_API_KEY` 가 없으면 의도 분류는 어떻게 되는가? `intent_classifier.py` 의 `classify` 부터 따라가서
   폴백 체인을 화살표로 적어라: haiku → ______ → ______. 최종 폴백이 돌려주는 intent 값은? ______
2. `ORCHESTRATOR_MAX_TURN_SECONDS=3` 이면 에이전트가 3초 안에 못 끝났을 때 (a) 어떤 SSE 이벤트가 나가고 (b) 남은 태스크는 어떻게 되며 (c) status 는 무엇인가?
   근거 행: ______
3. 에이전트 2개 중 하나가 예외를 던지면 답변은 나오는가? 어떤 이벤트가 그 사실을 알리는가? 근거 행: ______

## 1-E. 점검 질문 (코드 안 보고 5분 안에)

1. 한 턴에서 LLM 은 최소 몇 번, 최대 몇 번 호출되는가? (1-C 표 근거)
2. `status` 가 `rejected` 로 끝나는 경로는 어디서 갈라지는가?
3. 단일 에이전트일 때 Synthesizer 가 하는 일과 하지 않는 일은?

## 1-F. 산출물

- 이 파일을 채운다.
- 종이(또는 excalidraw)에 "내가 이해한 파이프라인" 1장. Doc 07 의 그림과 다른 점 3개:
  1.
  2.
  3.

---

## 선택: 실행 추적 (HCX + Anthropic 키가 생기면)

```bash
cd ../my-health-ai-coach-llm-version2 && ./docker.sh up && ./docker.sh test && ./docker.sh seed
open http://localhost:8000          # chatRoomId 824107, DEV 패널의 ①~⑦ 시간 기록
docker exec -it aicoach-mas python scripts/simulate.py -q "작년 공복혈당 어땠어?" -s   # SSE 순서 실측
docker compose -f frontend/workflow_graph/docker-compose.yml up -d   # :8090 에서 LLM 호출 수·비용 실측
```
함정: seed 는 userToken 을 `test-token` 으로 심고 frontend 는 `test` 를 보낸다(Doc 18 R-71). Access denied 면 `.env` 에 `CHAT_AUTH_MODE=warn` 을 임시로.
