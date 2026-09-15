
from mini_mas.orchestrator import Orchestrator
from tests.unit.conftest import FakeLLM


def test_orchestrator_routes_by_classifier():
    clf = FakeLLM(text='{"agent": "numbers", "reason": "본인 기록"}')
    agent = FakeLLM(text="작년 공복혈당은 96 mg/dL 입니다.")
    turn = Orchestrator(classifier_llm=clf, agent_llm=agent).run("작년 공복혈당 어땠어?")
    assert turn.agent == "numbers"
    assert turn.result.name == "Numbers"
    assert turn.result.text.startswith("작년 공복혈당")
    assert len(clf.calls) == 1 and len(agent.calls) == 1


def test_force_agent_skips_classifier():
    clf = FakeLLM(text='{"agent": "numbers"}')
    agent = FakeLLM()
    turn = Orchestrator(classifier_llm=clf, agent_llm=agent).run("안녕", force_agent="chat")
    assert turn.agent == "chat"
    assert len(clf.calls) == 0


def test_classifier_failure_goes_to_chat():
    clf = FakeLLM(text="모르겠어요")
    turn = Orchestrator(classifier_llm=clf, agent_llm=FakeLLM()).run("???")
    assert turn.agent == "chat" and turn.fallback is True