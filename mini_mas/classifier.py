import json
import re

from mini_mas.llm import OpenAILLM
from mini_mas.prompts import render
from mini_mas.router import FALLBACK_AGENT, ROUTE_MAP

MAX_AGENTS = 2

def parse_json(text: str) -> dict | None:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return None

def normalize_agents(raw) -> list[str]:
    if isinstance(raw, str):
        raw = [raw]
    if not isinstance(raw, list):
        return []

    agents = []
    for key in raw:
        if key in ROUTE_MAP and key not in agents:
            agents.append(key)
    if len(agents) > 1 and "chat" in agents:
        agents.remove("chat")
    return agents[:MAX_AGENTS]

def classify(query: str, llm=None) -> dict:
    llm = llm or OpenAILLM("gpt-5.4-nano", agent="Classifier")
    system, user = render("classifier", query=query)
    resp = llm.invoke(system=system, user=user, max_tokens=128)
    parsed = parse_json(resp.text)
    agents = normalize_agents(parsed.get("agents", parsed.get("agent"))) if parsed else []

    if not agents:
        return {
            "agent": FALLBACK_AGENT,
            "agents": [FALLBACK_AGENT],
            "reason": "분류 실패",
            "fallback": True,
            "raw": resp.text
        }

    return {
        "agent": agents[0],
        "agents": agents,
        "reason": parsed.get("reason", ""),
        "fallback": False,
        "raw": resp.text
    }
