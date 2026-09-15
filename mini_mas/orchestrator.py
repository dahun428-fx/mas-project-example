import time

from mini_mas.classifier import classify
from mini_mas.router import resolve
from mini_mas.schemas import TurnResult

class Orchestrator:
    def __init__(self, classifier_llm=None, agent_llm=None):
        self.classifier_llm = classifier_llm
        self.agent_llm = agent_llm

    def run(self, query: str, force_agent: str | None = None) -> TurnResult:
        t0 = time.perf_counter()

        if force_agent:
            decision = {"agent": force_agent, "reason": "수동 지정", "fallback": False}
        else:
            decision = classify(query, self.classifier_llm)
        classify_ms = (time.perf_counter() - t0) * 1000

        agent = resolve(decision["agent"], llm=self.agent_llm)
        result = agent.run(query)

        return TurnResult(
            query=query,
            agent=decision["agent"],
            reason=decision["reason"],
            fallback=decision["fallback"],
            result=result,
            classify_ms=classify_ms,
            total_ms=(time.perf_counter() - t0) * 1000,
        )
