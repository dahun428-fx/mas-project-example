from datetime import date

from mini_mas.context import available_years, build_checkup_context, load_checkup
from mini_mas.guard import guard_years
from mini_mas.llm import OpenAILLM
from mini_mas.prompts import render
from mini_mas.schemas import AgentResult
from mini_mas.year import resolve_years


class NumbersAgent:
    name = "Numbers"

    def __init__(self, llm=None, data=None):
        self.llm = llm or OpenAILLM("gpt-5.4-nano", agent="Numbers")
        self.data = data or load_checkup()

    def run(self, query:str) -> AgentResult:
        today = date.today().isoformat()
        years = resolve_years(query, today=today)
        context = build_checkup_context(self.data, years)
        system, user = render(
            "numbers",
            today=today,
            context=context,
            query=query,
        )
        resp = self.llm.invoke(system=system, user=user)

        allowed = available_years(self.data)
        text, hallucinated = guard_years(resp.text, allowed)

        return AgentResult(
            name=self.name,
            text=text,
            metadata={
                "block_type": "personal_numbers",
                "model" : resp.model,
                "finish_reason" : resp.finish_reason,
                "latency_ms" : resp.latency_ms,
                "tokens":resp.input_tokens+resp.output_tokens,
                "years": years,
                "hallucinated_years": hallucinated,
            }
        )
