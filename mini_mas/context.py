import json
from pathlib import Path

DATA_PATH = Path(__file__).parent.parent / "data" / "sample_checkup.json"

def load_checkup(path: Path = DATA_PATH) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def available_years(data: dict) -> list[str]:
    return sorted({c["checkup_date"][:4] for c in data["checkups"]}, reverse=True)

def filter_checkups(data: dict, years: list[str]) -> tuple[list[dict], list[str]]:
    if not years or years == ["ALL"]:
        return data["checkups"], []

    matched = []
    missing = []
    for year in years:
        found = [c for c in data['checkups'] if c['checkup_date'].startswith(year)]
        if found:
            matched.extend(found)
        else:
            missing.append(year)
    return matched, missing

def build_checkup_context(data: dict, years: list[str] | None = None) -> str:
    checkups, missing = filter_checkups(data, years or [])

    lines = [f"사용자: {data['name']}, {data['age']}세, {data['gender']}"]
    lines.append(f"보유 검진 연도: {', '.join(available_years(data))}")

    for checkup in checkups:
        lines.append(f"\n[검진일 {checkup['checkup_date']}]")
        for item in checkup['result']:
            lines.append(
                f"- {item['da_name']}: {item['user_value']} {item['unit']} "
                f"(기준 {item['normal_value']}, 판정 {item['status']})"
            )
    if missing:
        lines.append(f"\n[없음] 요청한 연도 {', '.join(missing)} 의 검진 기록이 없습니다.")

    return "\n".join(lines)

