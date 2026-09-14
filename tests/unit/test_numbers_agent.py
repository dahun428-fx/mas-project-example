
from mini_mas.agents.chat import ChatAgent
from mini_mas.agents.numbers import NumbersAgent
from mini_mas.context import build_checkup_context, load_checkup


def test_context_contains_values_and_dates():
    text = build_checkup_context(load_checkup())
    assert "2025-11-12" in text and "2024-11-16" in text
    assert "공복혈당: 102 mg/dL" in text
    assert "판정 주의" in text


def test_numbers_agent_puts_context_into_prompt(fake_llm):
    result = NumbersAgent(llm=fake_llm).run("작년 공복혈당 어땠어?")
    assert result.metadata["block_type"] == "personal_numbers"
    user_prompt = fake_llm.calls[0]["user"]
    assert "공복혈당: 96 mg/dL" in user_prompt
    assert "작년 공복혈당 어땠어?" in user_prompt


def test_chat_agent_is_short(fake_llm):
    ChatAgent(llm=fake_llm).run("안녕")
    assert fake_llm.calls[0]["max_tokens"] == 128
