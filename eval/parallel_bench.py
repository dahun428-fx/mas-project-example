
import statistics
import time

from mini_mas.orchestrator import Orchestrator

QUERY = "내 LDL 높은데 뭘 먹어야 돼?"
AGENTS = ["numbers", "knowledge"]
REPEAT = 3


def serial_once(orch: Orchestrator) -> float:
    t0 = time.perf_counter()
    for key in AGENTS:
        orch.run(QUERY, force_agents=[key])
    return (time.perf_counter() - t0) * 1000


def parallel_once(orch: Orchestrator) -> float:
    t0 = time.perf_counter()
    orch.run(QUERY, force_agents=AGENTS)
    return (time.perf_counter() - t0) * 1000


def main():
    orch = Orchestrator()
    serial = [serial_once(orch) for _ in range(REPEAT)]
    parallel = [parallel_once(orch) for _ in range(REPEAT)]

    s = statistics.median(serial)
    p = statistics.median(parallel)

    print(f"질문: {QUERY}   담당: {AGENTS}   반복: {REPEAT}회\n")
    print(f"차례로   {[round(x) for x in serial]} ms   중앙값 {s:.0f} ms")
    print(f"동시에   {[round(x) for x in parallel]} ms   중앙값 {p:.0f} ms")
    print(f"\n단축: {s - p:.0f} ms ({(s - p) / s:.0%})   속도: {s / p:.2f}배")


if __name__ == "__main__":
    main()
