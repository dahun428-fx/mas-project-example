import time
import asyncio

from mini_mas.classifier import classify
from mini_mas.router import resolve
from mini_mas.schemas import TurnResult

AGENT_TIMEOUT_S = 30

class Orchestrator:
    def __init__(self, classifier_llm=None, agent_llm=None, agent_llms=None, timeout_s=AGENT_TIMEOUT_S):
        self.classifier_llm = classifier_llm
        self.agent_llm = agent_llm
        self.agent_llms = agent_llms or {}
        self.timeout_s = timeout_s

    def run(self, query: str, force_agents: list[str] | None = None) -> TurnResult:
        return asyncio.run(self.arun(query, force_agents))

    async def arun(self, query:str, force_agents: list[str] | None = None) -> TurnResult:
        t0 = time.perf_counter()

        if force_agents:
            decision = {"agents": list(force_agents), "reason": "수동 지정", "fallback": False}
        else:
            decision = await asyncio.to_thread(classify, query, self.classifier_llm)
        classify_ms = (time.perf_counter() - t0) * 1000

        t1 = time.perf_counter()
        outcomes = await asyncio.gather(
            *(self._run_one(key, query) for key in decision["agents"])
        )

        agents_ms = (time.perf_counter() - t1) * 1000

        results = []
        errors = {}
        for key, (result, error) in zip(decision["agents"], outcomes):
            if error:
                errors[key] = error
            else:
                results.append(result)

        return TurnResult(
            query=query,
            agents=decision["agents"],
            reason=decision["reason"],
            fallback=decision["fallback"],
            results=results,
            errors=errors,
            classify_ms=classify_ms,
            agents_ms=agents_ms,
            total_ms=(time.perf_counter() - t0) * 1000,
        )
    async def _run_one(self, key:str, query:str):
        llm = self.agent_llms.get(key, self.agent_llm)
        agent = resolve(key, llm=llm)
        try:
            result = await asyncio.wait_for(asyncio.to_thread(agent.run, query), timeout=self.timeout_s)
            return result, None
        except TimeoutError:
            return None, f"timeout ({self.timeout_s}s)"
        except Exception as e:
            return None, f"{type(e).__name__}: {e}"