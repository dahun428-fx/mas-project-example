
from mini_mas.events import sse_event
from mini_mas.orchestrator import Orchestrator
from tests.unit.conftest import FakeLLM

TWO_AGENTS = '{"agents": ["numbers", "knowledge"], "reason": "섞인 질문"}'


def _orch(**kw):
    kw.setdefault("classifier_llm", FakeLLM(text=TWO_AGENTS))
    kw.setdefault("agent_llm", FakeLLM(text="담당 답"))
    kw.setdefault("synth_llm", FakeLLM(text="합쳐진 답"))
    return Orchestrator(**kw)


async def _collect(orch, query="q"):
    return [event async for event in orch.astream(query)]


def test_sse_event_format():
    assert sse_event("result", {"text": "안녕"}) == 'event: result\ndata: {"text": "안녕"}\n\n'


async def test_event_order_contract():
    events = await _collect(_orch())
    names = [e["event"] for e in events]
    assert names[0] == "progress"
    assert names[1] == "agents"
    assert names.count("agent_done") == 2
    assert names[-3:] == ["result", "status", "done"]


async def test_result_event_carries_final_text():
    events = await _collect(_orch())
    result = next(e for e in events if e["event"] == "result")
    assert result["data"]["text"] == "합쳐진 답"


async def test_status_is_9999_when_all_agents_fail():
    events = await _collect(_orch(agent_llm=FakeLLM(error=RuntimeError("x"))))
    status = next(e for e in events if e["event"] == "status")
    assert status["data"]["code"] == "9999"


async def test_faster_agent_reports_first():
    events = await _collect(_orch(agent_llms={"numbers": FakeLLM(delay=0.4)}))
    done = [e["data"]["agent"] for e in events if e["event"] == "agent_done"]
    assert done == ["knowledge", "numbers"]
