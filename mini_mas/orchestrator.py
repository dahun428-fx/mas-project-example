import asyncio
import time

from mini_mas.classifier import classify
from mini_mas.router import resolve
from mini_mas.schemas import TurnResult
from mini_mas.synthesizer import synthesize
from mini_mas.trace import new_trace

AGENT_TIMEOUT_S = 30

class Orchestrator:
    def __init__(self, classifier_llm=None, agent_llm=None, agent_llms=None, synth_llm=None, timeout_s=AGENT_TIMEOUT_S):
        self.classifier_llm = classifier_llm
        self.agent_llm = agent_llm
        self.agent_llms = agent_llms or {}
        self.synth_llm = synth_llm
        self.timeout_s = timeout_s

    def run(self, query: str, force_agents: list[str] | None = None) -> TurnResult:
        return asyncio.run(self.arun(query, force_agents))

    async def arun(self, query:str, force_agents: list[str] | None = None) -> TurnResult:
        turn = None
        async for event in self.astream(query, force_agents):
            if event["event"] == "done":
                turn = event["data"]
        return turn

    async def astream(self, query:str, force_agents: list[str] | None = None) :
        t0 = time.perf_counter()
        trace_id = new_trace(query)
        def ms() -> float:
            return (time.perf_counter() - t0) * 1000

        yield {"event":"progress", "data":{"stage":"classify","label":"질문 의도 분류 중", "elapsed_ms":round(ms())}}

        if force_agents:
            decision = {"agents":list(force_agents), "reason":"수동 지정","fallback": False}
        else:
            decision = await asyncio.to_thread(classify, query, self.classifier_llm)
        classify_ms = ms()

        yield {"event":"agents","data":{"agents":decision["agents"], "reason":decision["reason"], "fallback":decision["fallback"], "elapsed_ms": round(classify_ms)}}

        yield {"event":"progress", "data": {"stage":"agents", "label":f"{len(decision['agents'])}개 담당 동시 실행 중", "elapsed_ms": round(ms())}}

        t1 = time.perf_counter()
        tasks = [asyncio.create_task(self._run_one(key, query)) for key in decision["agents"]]
        collected = {}
        for task in asyncio.as_completed(tasks):
            key, result, error = await task
            collected[key] = (result, error)
            yield {"event": "agent_done", "data":{"agent":key, "ok":error is None, "error":error, "elapsed_ms": round(ms())}}
        agents_ms = (time.perf_counter() - t1) * 1000

        results = []
        errors = {}
        for key in decision["agents"]:
            result, error = collected[key]
            if error:
                errors[key] = error
            else:
                results.append(result)

        yield {"event":"progress", "data":{"stage":"synth", "label":"답변 정리 중", "elapsed_ms": round(ms())}}

        t2 = time.perf_counter()
        final_text, refined = await asyncio.to_thread(synthesize, results, query, self.synth_llm)
        synth_ms = (time.perf_counter() - t2) * 1000

        turn = TurnResult(
            query=query,
            agents=decision["agents"],
            reason=decision["reason"],
            fallback=decision["fallback"],
            results=results,
            errors=errors,
            final_text=final_text,
            refined=refined,
            classify_ms=classify_ms,
            agents_ms=agents_ms,
            synth_ms=synth_ms,
            total_ms=ms(),
        )
        yield {"event": "result", "data": {"text": final_text, "refined": refined}}
        yield {"event": "status", "data": {"code": "0000" if results else "9999", "total_ms": round(turn.total_ms), "trace_id": trace_id}}
        yield {"event": "done", "data": turn}

    async def _run_one(self, key: str, query: str):
        llm = self.agent_llms.get(key, self.agent_llm)
        agent = resolve(key, llm=llm)
        try:
            result = await asyncio.wait_for(asyncio.to_thread(agent.run, query), timeout=self.timeout_s)
            return key, result, None
        except TimeoutError:
            return key, None, f"timeout ({self.timeout_s}s)"
        except Exception as e:
            return key, None, f"{type(e).__name__}: {e}"
