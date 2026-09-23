
import pytest

from mini_mas.year import resolve_years

TODAY = "2026-09-18"


@pytest.mark.parametrize(
    "query,expected",
    [
        ("작년 공복혈당 어땠어?", ["2025"]),
        ("재작년 결과 알려줘", ["2024"]),
        ("올해 검진 결과", ["2026"]),
        ("2024년 공복혈당", ["2024"]),
        ("2024년 3월 결과", ["2024-03"]),
        ("24년 결과", ["2024"]),
        ("3년 전 혈압", ["2023"]),
        ("2023, 2024년 비교해줘", ["2023", "2024"]),
        ("전체 연도 추이 보여줘", ["ALL"]),
        ("지금까지 결과 다 보여줘", ["ALL"]),
        ("공복혈당이 뭐야?", []),
        ("내 콜레스테롤 정상이야?", []),
    ],
)
def test_resolve_years(query, expected):
    assert resolve_years(query, today=TODAY) == expected
