
from mini_mas.agents.numbers import NumbersAgent
from mini_mas.guard import find_unknown_years, guard_years
from tests.unit.conftest import FakeLLM

ALLOWED = ["2025", "2024"]


def test_no_unknown_year_passes_through():
    text = "2024년 공복혈당은 96 mg/dL 입니다."
    assert guard_years(text, ALLOWED) == (text, [])


def test_unknown_year_replaces_answer():
    text, unknown = guard_years("2020년 공복혈당은 88 mg/dL 였습니다.", ALLOWED)
    assert unknown == ["2020"]
    assert "2020" not in text
    assert "2025, 2024" in text


def test_find_unknown_years_ignores_known():
    assert find_unknown_years("2024년과 2025년 비교", ALLOWED) == []


def test_agent_blocks_hallucinated_year():
    llm = FakeLLM(text="2019년에는 공복혈당이 85 mg/dL 였습니다.")
    result = NumbersAgent(llm=llm).run("2019년 공복혈당은?")
    assert result.metadata["hallucinated_years"] == ["2019"]
    assert "85" not in result.text
