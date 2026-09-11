from datetime import date

from mini_mas.llm import OpenAILLM
from mini_mas.prompts import render
from mini_mas.schemas import AgentResult

class KnowledgeAgent:
    name = "Knowledge"

    def __init__(self, llm=None):
        self.llm = llm or OpenAILLM(model="gpt-5.4-nano")

    def run(self, query: str) -> AgentResult:
        system, user = render("knowledge", query=query, today=date.today().isoformat())
        resp = self.llm.invoke(system=system, user=user)
        return AgentResult(
            name=self.name,
            text=resp.text,
            metadata={
                "block_type": "general",
                "model": resp.model,
                "finish_reason": resp.finish_reason,
                "latency_ms": resp.latency_ms,
                "tokens": resp.input_tokens + resp.output_tokens,
            }
        )
