# 6교시 · Orchestrator + 골든셋 라우팅 평가

날짜: 2026-09-15 · Step 3 · 상태: 완료 (**Step 3 수락 기준 통과**) · 테스트 14 passed

## 목표
1. "분류 → 담당 찾기 → 실행" 흐름을 `Orchestrator` 하나로 묶어 CLI·병렬 실행·웹 API 가 같이 쓰게 한다.
2. 분류기 정확도를 골든셋으로 숫자로 잰다. 수락 기준: 에이전트 정확도 ≥ 90%.

## 만든 파일
### 파트 A · Orchestrator
- `mini_mas/schemas.py`: `TurnResult(query, agent, reason, fallback, result, classify_ms, total_ms)` 추가 (`@dataclass`).
- `mini_mas/orchestrator.py`: `Orchestrator(classifier_llm=None, agent_llm=None).run(query, force_agent=None) -> TurnResult`.
  `force_agent` 는 분류기를 건너뛴다 (원본의 "@멘션 강제 라우팅"과 같은 역할).
- `mini_mas/router.py`: `resolve(agent_key, llm=None)` 로 에이전트에 LLM 주입.
- `mini_mas/ask.py`: 로직 제거, `Orchestrator().run()` 호출과 출력만.
- `tests/unit/test_orchestrator.py`: 분류 결과대로 라우팅 / 강제 지정 시 분류기 호출 0회 / 분류 실패 시 chat.

### 파트 B · 골든셋
- `eval/golden_routing.jsonl`: 30문항 (numbers 11, knowledge 11, chat 8). 1~20 기본 문항, 21~30 헷갈리는 유형 5종 × 2.
- `eval/routing_eval.py`: 분류기만 호출해 채점. 정확도, fallback 수, 혼동 행렬, 틀린 문항과 LLM 원문 출력.
  `load_golden()` 에 **평가 데이터 검증** 2개: 정답이 3담당 중 하나인지, 질문이 안내 문구로 남아 있지 않은지.
- `mini_mas/prompts/classifier.yaml`: 규칙 추가 "건강 단어가 있어도 정보나 조언을 요청하지 않고 감정만 표현하면 chat. 질문에 없는 의도를 추측하지 않습니다."

## 헷갈리는 문항 유형과 정한 정책
| 유형 | 문항 | 정답 | 정한 이유 |
|---|---|---|---|
| A 본인 수치 + 기준 질문 | #21 공복혈당 102면 높은 거야? / #22 LDL 138이면 위험한 수준이야? | knowledge | 수치를 사용자가 직접 줬으므로 기록 조회 불필요 |
| B "내" 없는 본인 기록 | #23 검진에서 뭐가 제일 안 좋았어? / #24 혈당 수치 두 해 비교해줘 | numbers | 기록 없이는 답할 수 없음 |
| C 건강 단어 섞인 잡담 | #25 혈압 때문에 짜증나 ㅠㅠ / #26 콜레스테롤 얘기 그만하고 싶다 | chat | 정보가 아니라 감정 표현 |
| D 한 단어 | #27 콜레스테롤 / #28 혈압 | knowledge | 규칙 "애매하면 knowledge" |
| E 본인 수치 + 일반 조언 | #29 내 LDL 높은데 뭘 먹어야 돼? / #30 제 공복혈당 괜찮으면 운동은 뭐가 좋아요? | numbers | 본인 수치를 모르면 조언이 틀릴 수 있음 (knowledge 도 정당한 선택 → 7교시 주제) |

판단 기준: "이 질문에 답하려면 사용자의 검진 기록을 꼭 봐야 하나?" 봐야 하면 numbers, 일반 지식으로 답할 수 있으면 knowledge, 정보 요청이 아니면 chat.

## 결과
| 실행 | 정확도 | 틀린 문항 |
|---|---|---|
| 20문항 (쉬운 문항만) | 20/20 100% | 없음. 문제지가 쉬워서 의미 없는 숫자 |
| 30문항, 규칙 추가 전 | 29/30 96.7% | #25 chat → knowledge (분류기가 "관리 방법을 묻는다"고 확대 해석) |
| 30문항, 규칙 추가 후 1회차 | 30/30 100% | 없음 |
| 30문항, 규칙 추가 후 2회차 | 29/30 96.7% | #29 numbers → knowledge |

## 핵심 개념
- 쉬운 문제지의 100% 는 실력이 아니다. 헷갈리는 유형을 일부러 넣어야 평가가 의미를 갖는다.
- 정확도 한 숫자보다 **틀린 방향**(혼동 행렬의 대각선 밖)이 중요하다. chat→knowledge 는 위험도 낮음, knowledge→numbers 는 높음.
- 틀린 문항을 프롬프트 예시로 복사하면 컨닝. **유형을 규칙으로** 일반화한다.
- LLM 은 매번 답이 조금씩 다르다. 개선 확인은 최소 2회 실행.
- 규칙 추가로 #25(C유형)는 두 번 모두 고쳐졌다. 대신 #29(E유형)가 실행마다 흔들린다. 분류기의 reason("본인 수치 언급은 있지만 무엇을 먹어야 하는지는 일반 지식")도 틀린 말이 아니다. **섞인 질문은 하나만 고르는 구조 자체가 불안정하다** → 7교시에서 여러 에이전트를 동시에 부르는 이유.
- 원본 대응: 원본은 routing_eval_compound_120_v2.json(120문항)으로 같은 평가를 하고, single(에이전트 1개) vs multi(여러 개) 품질을 논문으로 비교했다 (문서집 Doc 16).

## 겪은 문제
- `TurnResult` 에 `@dataclass` 누락 → `TurnResult() takes no arguments`. 클래스에 이 오류가 나면 `@dataclass` 또는 `__init__` 누락.
- `TurnResult` 필드 `fallback: bool` 과 `result: AgentResult` 가 한 줄(`fallback: AgentResult`)로 합쳐짐 → 두 줄로 복구.
- `NumbersAgent.name = "NumbersAgent"` (다른 에이전트는 "Knowledge", "Chat") → 오케스트레이터 테스트가 처음 이름을 검사하며 잡음 → "Numbers" 로 통일.
- 골든셋에 안내 예시 줄(`"query": "..."`)을 그대로 붙여 넣음 → 분류기는 올바르게 chat 을 골랐지만 채점이 틀림으로 처리. 혼동 행렬 합계(21)가 문항 수(22)와 달라 드러남.
- 이를 막으려고 `load_golden()` 에 정답 값·안내 문구 검사 추가. 이후 빈 정답(`""`)과 남은 안내 문구를 검사가 차례로 잡음 (검사는 첫 문제에서 멈추므로 하나씩 드러난다).

## 다음 교시
- 7교시 (Step 4 시작): 병렬 실행. 분류기가 에이전트를 **여러 개**(최대 2개) 고르게 하고, `asyncio` 로 동시에 실행한다. 직렬 대비 지연 단축을 측정하고, #29·#30 같은 섞인 질문이 numbers + knowledge 를 함께 부르는지 확인한다.
