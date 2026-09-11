
import pytest

from mini_mas.agents.knowledge import KnowledgeAgent
from mini_mas.prompts import render
from mini_mas.schemas import AgentResult


def test_run_returns_agent_result(fake_llm):
    result = KnowledgeAgent(llm=fake_llm).run("공복혈당이 뭐야?")
    assert isinstance(result, AgentResult)
    assert result.name == "Knowledge"
    assert result.text == "가짜 답변입니다."
    assert result.metadata["block_type"] == "general"


def test_query_goes_into_user_prompt(fake_llm):
    KnowledgeAgent(llm=fake_llm).run("LDL 기준이 뭐야?")
    assert len(fake_llm.calls) == 1
    assert "LDL 기준이 뭐야?" in fake_llm.calls[0]["user"]
    assert "건강 코치" in fake_llm.calls[0]["system"]


def test_render_missing_slot_raises():
    with pytest.raises(KeyError):
        render("knowledge", today="2026-09-11")
