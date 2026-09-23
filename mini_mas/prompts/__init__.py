from pathlib import Path

import yaml

PROMPTS_DIR = Path(__file__).parent

def render(name: str, **slots)-> tuple[str, str]:
    path = PROMPTS_DIR / f"{name}.yaml"
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    system = data["system"]
    user = data["user"].format(**slots)
    return system, user
