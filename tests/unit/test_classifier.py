
from mini_mas.classifier import classify, parse_json
from tests.unit.conftest import FakeLLM


def test_valid_json_routes_to_agent():
    llm = FakeLLM(text='{"agent": "numbers", "reason": "본인 기록"}')
    d = classify("작년 공복혈당 어땠어?", llm=llm)
    assert d["agent"] == "numbers" and d["fallback"] is False


def test_json_inside_code_fence_is_parsed():
    llm = FakeLLM(text='```json\n{"agent": "knowledge", "reason": "일반 지식"}\n```')
    assert classify("공복혈당이 뭐야?", llm=llm)["agent"] == "knowledge"


def test_unknown_agent_falls_back_to_chat():
    llm = FakeLLM(text='{"agent": "doctor", "reason": "x"}')
    d = classify("아무거나", llm=llm)
    assert d["agent"] == "chat" and d["fallback"] is True


def test_garbage_falls_back_to_chat():
    llm = FakeLLM(text="죄송합니다, 잘 모르겠습니다.")
    d = classify("아무거나", llm=llm)
    assert d["agent"] == "chat" and d["fallback"] is True


def test_parse_json_returns_none_on_broken_json():
    assert parse_json('{"agent": "numbers", ') is None

def test_two_agents_kept_in_order():
    d = classify("q", llm=FakeLLM(text='{"agents": ["numbers", "knowledge"], "reason": "섞인 질문"}'))
    assert d["agents"] == ["numbers", "knowledge"]
    assert d["agent"] == "numbers"

def test_chat_removed_when_mixed():
    d = classify("q", llm=FakeLLM(text='{"agents": ["chat", "knowledge"]}'))
    assert d["agents"] == ["knowledge"]

def test_duplicates_removed_and_max_two():
    d = classify("q", llm=FakeLLM(text='{"agents": ["numbers", "numbers", "knowledge", "chat"]}'))
    assert d["agents"] == ["numbers", "knowledge"]
