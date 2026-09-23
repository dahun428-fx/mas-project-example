# 9교시 · 웹 API 와 실시간 진행 표시 (CP2)

날짜: 2026-09-18 · Step 5 · 상태: 완료 · 테스트 38 passed

## 목표
`ask.py` 는 4초 동안 아무것도 안 보여주다가 답을 한 번에 냈다. 브라우저가 질문을 보내고, 진행 단계를 **생기는 대로** 받게 한다.

## 구조: 입구 3개, 몸통 1개
```
astream   ← 진짜 일. 진행되는 대로 이벤트를 yield
   ↑
arun      ← astream 을 끝까지 돌려 "done" 이벤트의 TurnResult 만 꺼냄
   ↑
run       ← asyncio.run 으로 감싸 보통 함수처럼 부를 수 있게
```
| 부르는 쪽 | 쓰는 것 | 원하는 것 |
|---|---|---|
| ask.py, 테스트 | `run` | 최종 결과만 |
| server.py | `astream` | 진행 상황 실시간 |

같은 astream 을 두 소비자가 각자 필요한 것만 골라 쓴다.

## 이벤트 계약 (담당 2개 기준 9개)
```
progress(classify) → agents → progress(agents) → agent_done × 2 → progress(synth) → result → status → done
```
- `result`: 최종 글 / `status`: `"0000"` 성공, `"9999"` 전부 실패 / `done`: TurnResult 객체(서버 내부용, 브라우저로 안 보냄)
- 원본도 같은 방식: 마지막이 항상 `status` 라 프론트가 "끝"을 안다. 거부 경로에서도 종료 이벤트 집합이 같아야 화면이 멈추지 않는다.

## 만든 파일
- `mini_mas/events.py`: `sse_event(name, data)` → `event: {name}\ndata: {json}\n\n`. `ensure_ascii=False` 로 한글 그대로, 끝의 빈 줄이 덩어리 구분자.
- `mini_mas/orchestrator.py`: `_run_one` 이 `(key, result, error)` 반환(이름표), `astream` 신설, `arun` 은 astream 소비자로 축소.
- `mini_mas/server.py`: FastAPI. `GET /api/health`, `GET /`(frontend/index.html), `POST /api/chat`(SSE `StreamingResponse`).
  `try/except` 로 감싸 스트림 도중 오류에도 `status 9999` 를 보내 끝을 알린다. 헤더 `X-Accel-Buffering: no`.
- `frontend/index.html`: fetch + `resp.body.getReader()`. 받은 조각을 버퍼에 쌓고 `\n\n` 이 나올 때마다 잘라 처리.
- `tests/unit/test_stream.py` 5개: SSE 포맷 / 이벤트 순서 계약 / result 내용 / 전부 실패 시 9999 / **빠른 담당이 먼저 보고**.

## 핵심 개념
- `yield` 가 있는 함수는 값을 여러 번 내주고 그 자리에서 멈춰 있다가 이어서 실행된다. 주방이 다 만들어 놓고 주는 게 아니라 하나 만들면 바로 내주는 것.
- `asyncio.as_completed` 는 **먼저 끝난 것부터** 넘겨준다(gather 는 전부 끝나야 한 번에). 그래서 빠른 담당의 완료를 즉시 알릴 수 있다. 동시 실행은 그대로.
- **알림은 도착 순서, 결과는 정한 순서.** `collected` 딕셔너리에 담아 두고 `decision["agents"]` 순서로 다시 꺼내 `results` 를 만든다. 합성 결과가 네트워크 속도에 따라 달라지면 안 되기 때문.
- 네트워크는 우리가 보낸 덩어리 단위로 도착하지 않는다. 클라이언트는 버퍼에 쌓아 두고 완성된 덩어리만 꺼내 쓴다.
- 총 4초를 줄일 수 없어도 사용자가 4초 동안 빈 화면을 보지 않게 할 수는 있다. 그게 이 교시의 전부.

## 겪은 문제
- `arun` 의 `return turn` 이 `async for` **안**에 들어가 첫 이벤트에서 즉시 반환 → 모든 오케스트레이터 테스트가 `'NoneType' object has no attribute ...`. 들여쓰기 한 칸.
- `len(decision['agent'])` (문자열 길이 7) → `decision['agents']`. `force_agents` 경로에서는 `agent` 키가 없어 KeyError 가 났을 것.
- `frontend/index.html` 을 만들기 전에 `/` 접속 → `RuntimeError: File at path ... does not exist`. 긴 ASGI 추적에서 **맨 아래 줄**만 보면 된다. 이때도 `/api/health` 와 `/api/chat` 은 정상 — FastAPI 가 요청마다 오류를 가둔다.

## 다음 교시
- 10교시 (Step 6): 규칙 계층. 연도 정규화("작년" → 2024), 데이터에 없는 연도를 정직하게 답하기, 답변에 없는 수치·연도가 섞이면 코드가 잡아내는 환각 가드.
