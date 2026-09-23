from mini_mas.agents.chat import ChatAgent
from mini_mas.agents.knowledge import KnowledgeAgent
from mini_mas.agents.numbers import NumbersAgent

ROUTE_MAP = {
    "numbers": NumbersAgent,
    "knowledge": KnowledgeAgent,
    "chat": ChatAgent,
}

FALLBACK_AGENT = "chat"

def resolve(agent_key : str, llm=None) :
    return ROUTE_MAP[agent_key](llm=llm)
