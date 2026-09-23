import itertools
import queue
import sqlite3
import threading
import uuid
from contextvars import ContextVar
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "log" / "traces.db"

_trace_id: ContextVar[str | None] = ContextVar("trace_id", default=None)
# 숫자가 아니라 카운터 "객체" 를 담는다.
# asyncio.to_thread 는 컨텍스트를 복사하므로, 숫자를 넣으면 스레드 안의 set() 이 부모에 반영되지 않아
# 담당마다 seq 가 1 부터 다시 시작한다. 객체를 넣으면 사본들이 같은 객체를 가리켜 번호가 이어진다.
_seq: ContextVar[itertools.count | None] = ContextVar("seq", default=None)

PRICES = {
    "gpt-5.4-nano": (0.0000001, 0.0000004),
    "gpt-4o-mini": (0.00000015, 0.0000006),
    "text-embedding-3-small": (0.00000002, 0.0),
}

def new_trace(query: str = "") -> str:
    trace_id = uuid.uuid4().hex[:12]
    _trace_id.set(trace_id)
    _seq.set(itertools.count(1))
    return trace_id

def get_trace_id() -> str | None:
    return _trace_id.get()

def compute_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    price_in, price_out = PRICES.get(model, (0.0, 0.0))
    return input_tokens * price_in + output_tokens * price_out

def record(*, model, agent, input_tokens=0, output_tokens=0, latency_ms=0.0, finish_reason="stop", error=None, query="", response=""):
    counter = _seq.get()
    seq = next(counter) if counter is not None else 0
    row = {
        "trace_id": _trace_id.get() or "-",
        "seq": seq,
        "agent": agent,
        "model": model,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cost_usd": compute_cost(model, input_tokens, output_tokens),
        "latency_ms": latency_ms,
        "finish_reason": finish_reason,
        "error": error,
        "query": query[:200],
        "response": response[:500],
    }
    _writer().put(row)

_queue: queue.Queue | None = None
_lock = threading.Lock()

SCHEMA = """
CREATE TABLE IF NOT EXISTS traces (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT DEFAULT CURRENT_TIMESTAMP,
    trace_id TEXT, seq INTEGER, agent TEXT, model TEXT,
    input_tokens INTEGER, output_tokens INTEGER, cost_usd REAL,
    latency_ms REAL, finish_reason TEXT, error TEXT,
    query TEXT, response TEXT
);
CREATE INDEX IF NOT EXISTS idx_trace ON traces(trace_id);
"""

def _worker(q: queue.Queue):
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA)
    columns = ["trace_id", "seq", "agent", "model", "input_tokens", "output_tokens",
               "cost_usd", "latency_ms", "finish_reason", "error", "query", "response"]
    sql = f"INSERT INTO traces ({','.join(columns)}) VALUES ({','.join('?' * len(columns))})"

    while True:
        row = q.get()
        if row is None:
            break
        try:
            conn.execute(sql, [row[c] for c in columns])
            conn.commit()
        except Exception as e:
            print(f"[trace] 기록 실패: {e}")
        finally:
            q.task_done()
    conn.close()

def _writer() -> queue.Queue:
    global _queue
    with _lock:
        if _queue is None:
            _queue = queue.Queue(maxsize=1000)
            threading.Thread(target=_worker, args=(_queue,), daemon=True).start()
        return _queue

def flush():
    if _queue is not None:
        _queue.join()

