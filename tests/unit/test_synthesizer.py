
from mini_mas.schemas import AgentResult
from mini_mas.synthesizer import EMPTY_ANSWER, guard, merge


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