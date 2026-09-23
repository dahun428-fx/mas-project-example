import json


def sse_event(name: str, data) -> str:
    payload = json.dumps(data, ensure_ascii=False)
    return f"event: {name}\ndata: {payload}\n\n"
