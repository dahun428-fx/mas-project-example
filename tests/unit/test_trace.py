
import sqlite3

import pytest

from mini_mas import trace
from mini_mas.orchestrator import Orchestrator
from tests.unit.conftest import FakeLLM

TWO_AGENTS = '{"agents": ["numbers", "knowledge"], "reason": "섞인 질문"}'


@pytest.fixture
def temp_db(tmp_path, monkeypatch):
    db = tmp_path / "traces.db"
    monkeypatch.setattr(trace, "DB_PATH", db)
    monkeypatch.setattr(trace, "_queue", None)
    yield db


def rows(db):
    conn = sqlite3.connect(db)
    return conn.execute("SELECT trace_id, seq, agent, model, cost_usd FROM traces ORDER BY seq").fetchall()


def test_cost_uses_price_table():
    assert trace.compute_cost("gpt-5.4-nano", 1_000_000, 0) == pytest.approx(0.1)
    assert trace.compute_cost("gpt-5.4-nano", 0, 1_000_000) == pytest.approx(0.4)


def test_unknown_model_costs_zero():
    assert trace.compute_cost("gpt-9-ultra", 1_000_000, 1_000_000) == 0.0


def test_new_trace_resets_seq():
    first = trace.new_trace("q1")
    trace.record(model="gpt-5.4-nano", agent="A")
    second = trace.new_trace("q2")
    assert first != second
    assert trace.get_trace_id() == second


def test_records_are_written(temp_db):
    trace.new_trace("q")
    trace.record(model="gpt-5.4-nano", agent="Classifier", input_tokens=100, output_tokens=20)
    trace.record(model="gpt-5.4-nano", agent="Numbers", input_tokens=300, output_tokens=80)
    trace.flush()

    saved = rows(temp_db)
    assert len(saved) == 2
    assert [r[1] for r in saved] == [1, 2]
    assert saved[0][0] == saved[1][0]
    assert saved[1][4] > 0


def test_fake_llm_turn_writes_nothing(temp_db):
    """가짜 LLM 으로 도는 테스트는 DB 를 건드리지 않는다.

    기록은 OpenAILLM.invoke 안에서만 일어난다. record 가 한 번도 안 불리면
    writer 스레드도 안 뜨고 DB 파일 자체가 생기지 않는다.
    """
    Orchestrator(
        classifier_llm=FakeLLM(text=TWO_AGENTS),
        agent_llm=FakeLLM(text="답"),
        synth_llm=FakeLLM(text="합친 답"),
    ).run("내 LDL 높은데 뭘 먹어야 돼?")
    trace.flush()
    assert not temp_db.exists()
