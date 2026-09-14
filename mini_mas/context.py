import json
from pathlib import Path

DATA_PATH = Path(__file__).parent.parent / "data" / "sample_checkup.json"

def load_checkup(path: Path = DATA_PATH) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def build_checkup_context(data: dict) -> str:
    lines = [f"사용자: {data['name']}, {data['age']}세, {data['gender']}"]
    for checkup in data["checkups"]:
        lines.append(f"\n[검진일 {checkup['checkup_date']}]")
        for item in checkup["result"]:
            lines.append(
                f"- {item['da_name']}: {item['user_value']} {item['unit']} "
                f"(기준 {item['normal_value']}, 판정 {item['status']})"
            )
    return "\n".join(lines)