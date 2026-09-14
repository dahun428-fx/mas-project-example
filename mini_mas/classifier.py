import json
import re

from mini_mas.llm import OpenAILLM
from mini_mas.prompts import render
from mini_mas.router import FALLBACK_AGENT, ROUTE_MAP


def parse_json(text: str) -> dict | None:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return None

def classify(query: str, llm=None) -> dict:
    llm = llm or OpenAILLM("gpt-5.4-nano")
    system, user = render("classifier", query=query)
    resp = llm.invoke(system=system, user=user, max_tokens=128)
    parsed = parse_json(resp.text)
    if not parsed or parsed.get("agent") not in ROUTE_MAP:
        return {"agent": FALLBACK_AGENT, "reason": "분류 실패","fallback": True, "raw": resp.text}
    return {
        "agent": parsed["agent"],
        "reason": parsed.get("reason", ""),
        "fallback": False,
        "raw": resp.text
    }