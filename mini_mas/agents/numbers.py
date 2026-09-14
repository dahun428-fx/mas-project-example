from datetime import date

from mini_mas.context import build_checkup_context, load_checkup
from mini_mas.llm import OpenAILLM
from mini_mas.prompts import render
from mini_mas.schemas import AgentResult

class NumbersAgent:
    name = "NumbersAgent"

    def __init__(self, llm=None, data=None):
        self.llm = llm or OpenAILLM("gpt-5.4-nano")
        self.data = data or load_checkup()

    def run(self, query:str) -> AgentResult:
        context = build_checkup_context(self.data)
        system, user = render(
            "numbers",
            today=date.today().isoformat(),
            context=context,
            query=query,
        )
        resp = self.llm.invoke(system=system, user=user)
        return AgentResult(
            name=self.name,
            text=resp.text,
            metadata={
                "block_type": "personal_numbers",
                "model" : resp.model,
                "finish_reason" : resp.finish_reason,
                "latency_ms" : resp.latency_ms,
                "tokens":resp.input_tokens+resp.output_tokens,
            }
        )