
from mini_mas.orchestrator import Orchestrator
from tests.unit.conftest import FakeLLM

TWO_AGENTS = '{"agents": ["numbers", "knowledge"], "reason": "섞인 질문"}'


def test_single_agent_route():
    clf = FakeLLM(text='{"agents": ["numbers"], "reason": "본인 기록"}')
    turn = Orchestrator(classifier_llm=clf, agent_llm=FakeLLM()).run("작년 공복혈당 어땠어?")
    assert turn.agents == ["numbers"]
    assert [r.name for r in turn.results] == ["Numbers"]
    assert turn.errors == {}


def test_force_agents_skips_classifier():
    clf = FakeLLM()
    turn = Orchestrator(classifier_llm=clf, agent_llm=FakeLLM()).run("안녕", force_agents=["chat"])
    assert turn.agents == ["chat"]
    assert len(clf.calls) == 0


def test_classifier_failure_goes_to_chat():
    turn = Orchestrator(classifier_llm=FakeLLM(text="모르겠어요"), agent_llm=FakeLLM()).run("???")
    assert turn.agents == ["chat"] and turn.fallback is True


def test_two_agents_run_at_the_same_time():
    slow = FakeLLM(delay=0.3)
    turn = Orchestrator(classifier_llm=FakeLLM(text=TWO_AGENTS), agent_llm=slow).run("내 LDL 높은데 뭘 먹어야 돼?")
    assert [r.name for r in turn.results] == ["Numbers", "Knowledge"]
    assert turn.agents_ms < 500


def test_one_agent_error_keeps_the_other():
    turn = Orchestrator(
        classifier_llm=FakeLLM(text=TWO_AGENTS),
        agent_llm=FakeLLM(),
        agent_llms={"numbers": FakeLLM(error=RuntimeError("API 다운"))},
    ).run("q")
    assert [r.name for r in turn.results] == ["Knowledge"]
    assert "RuntimeError" in turn.errors["numbers"]


def test_one_agent_timeout_keeps_the_other():
    turn = Orchestrator(
        classifier_llm=FakeLLM(text=TWO_AGENTS),
        agent_llm=FakeLLM(),
        agent_llms={"knowledge": FakeLLM(delay=1.0)},
        timeout_s=0.1,
    ).run("q")
    assert [r.name for r in turn.results] == ["Numbers"]
    assert turn.errors["knowledge"].startswith("timeout")


def test_all_agents_fail():
    broken = FakeLLM(error=RuntimeError("x"))
    turn = Orchestrator(classifier_llm=FakeLLM(text=TWO_AGENTS), agent_llm=broken).run("q")
    assert turn.results == []
    assert set(turn.errors) == {"numbers", "knowledge"}