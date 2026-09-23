import re

ALL = "ALL"

_ALL_PATTERNS = (r"전체\s*(연도|검진|결과)", r"모든\s*(연도|검진|결과)", r"지금까지", r"그동안", r"추이")

_RELATIVE = {
    "재작년": -2,
    "작년": -1,
    "지난해": -1,
    "올해": 0,
    "금년": 0,
}


def resolve_years(query: str, today: str) -> list[str]:
    current_year = int(today[:4])

    for pattern in _ALL_PATTERNS:
        if re.search(pattern, query):
            return [ALL]

    years: list[str] = []

    def add(value: str):
        if value not in years:
            years.append(value)

    for match in re.finditer(r"(20\d{2})\s*년?\s*(\d{1,2})\s*월", query):
        add(f"{match.group(1)}-{int(match.group(2)):02d}")

    # 쉼표 나열: "2023, 2024년" — 앞쪽 연도에는 "년"이 없다
    for match in re.finditer(r"((?:20\d{2}\s*,\s*)+20\d{2})\s*년", query):
        for year in re.findall(r"20\d{2}", match.group(1)):
            add(year)

    # 단일 연도: 뒤에 월이 오지 않을 때만 (이미 "2024-03" 으로 잡힌 건 제외)
    for match in re.finditer(r"(20\d{2})\s*년(?!\s*\d{1,2}\s*월)", query):
        add(match.group(1))

    for match in re.finditer(r"(?<!\d)(\d{2})\s*년(?!\s*전)", query):
        add(str(2000 + int(match.group(1))))

    for match in re.finditer(r"(\d{1,2})\s*년\s*전", query):
        add(str(current_year - int(match.group(1))))

    for word, offset in _RELATIVE.items():
        if word == "작년" and re.search(r"재작년", query):
            continue
        if word in query:
            add(str(current_year + offset))

    return sorted(years)
