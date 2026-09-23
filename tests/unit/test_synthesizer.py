
from mini_mas.schemas import AgentResult
from mini_mas.synthesizer import EMPTY_ANSWER, guard, merge, synthesize
from tests.unit.conftest import FakeLLM


def _result(name, text, block_type):
    return AgentResult(name=name, text=text, metadata={"block_type": block_type})


def test_merge_orders_personal_numbers_first():
    results = [
        _result("Knowledge", "LDL은 나쁜 콜레스테롤입니다.", "general"),
        _result("Numbers", "사용자님의 LDL은 138입니다.", "personal_numbers"),
    ]
    merged = merge(results)
    assert merged.index("138") < merged.index("나쁜 콜레스테롤")


def test_merge_skips_empty_text():
    results = [_result("A", "내용", "general"), _result("B", "   ", "general")]
    assert merge(results) == "내용"


def test_guard_strips_markdown_headers():
    assert guard("## 요약\n내용입니다.") == "요약\n내용입니다."


def test_guard_spaces_units():
    assert guard("LDL 138mg/dL, 혈압 128mmHg") == "LDL 138 mg/dL, 혈압 128 mmHg"


def test_guard_softens_assertions():
    assert "전문의 상담을 통해 진단" in guard("반드시 진단을 받으세요.")


def test_guard_returns_message_on_empty():
    assert guard("   ") == EMPTY_ANSWER


def test_single_result_skips_llm():
    llm = FakeLLM(text="다듬은 답")
    text, refined = synthesize([_result("Numbers", "원문 그대로", "personal_numbers")], "q", llm=llm)
    assert text == "원문 그대로"
    assert refined is False
    assert len(llm.calls) == 0


def test_two_results_call_llm_once():
    llm = FakeLLM(text="합쳐진 답입니다.")
    results = [
        _result("Numbers", "LDL 138", "personal_numbers"),
        _result("Knowledge", "포화지방을 줄이세요", "general"),
    ]
    text, refined = synthesize(results, "q", llm=llm)
    assert text == "합쳐진 답입니다."
    assert refined is True
    assert len(llm.calls) == 1
    assert "LDL 138" in llm.calls[0]["user"]


def test_refine_failure_falls_back_to_merged():
    llm = FakeLLM(error=RuntimeError("합성 LLM 다운"))
    results = [
        _result("Numbers", "LDL 138", "personal_numbers"),
        _result("Knowledge", "포화지방을 줄이세요", "general"),
    ]
    text, _ = synthesize(results, "q", llm=llm)
    assert "LDL 138" in text and "포화지방" in text


def test_no_results_returns_message():
    text, refined = synthesize([], "q", llm=FakeLLM())
    assert text == EMPTY_ANSWER
    assert refined is False
