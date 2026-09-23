from mini_mas.llm import OpenAILLM
from mini_mas.prompts import render
from mini_mas.schemas import AgentResult


class ChatAgent:
    name = "Chat"

    def __init__(self, llm=None):
        self.llm = llm or OpenAILLM("gpt-5.4-nano", agent="Chat")
    def run(self, query:str) -> AgentResult:
        system, user = render("chat", query=query)
        resp = self.llm.invoke(system=system, user=user, max_tokens=128)
        return AgentResult(
            name=self.name,
            text=resp.text,
            metadata={
                "block_type": "general",
                "model" : resp.model,
                "finish_reason" : resp.finish_reason,
                "latency_ms" : resp.latency_ms,
                "tokens":resp.input_tokens+resp.output_tokens,
            }
        )
