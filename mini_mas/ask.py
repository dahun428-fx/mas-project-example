import argparse

from mini_mas.orchestrator import Orchestrator
from mini_mas.router import ROUTE_MAP


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("query")
    parser.add_argument("--agent", choices=ROUTE_MAP.keys(), action="append", default=None)
    parser.add_argument("--raw", action="store_true", help="담당별 원문도 출력")
    args = parser.parse_args()

    turn = Orchestrator().run(args.query, force_agents=args.agent)

    flag = " (fallback)" if turn.fallback else ""
    mode = "refine" if turn.refined else "fast-path"
    print(f"[분류] agents={turn.agents}{flag} · {turn.reason} · {turn.classify_ms:.0f}ms")
    print(f"[실행] {len(turn.agents)}개 동시 실행 · {turn.agents_ms:.0f}ms")
    print(f"[합성] {mode} · {turn.synth_ms:.0f}ms\n")

    if args.raw:
        for r in turn.results:
            print(f"── {r.name} ({r.metadata['latency_ms']:.0f}ms)")
            print(r.text + "\n")

    print(turn.final_text + "\n")

    for key, error in turn.errors.items():
        print(f"── {key} 실패: {error}\n")

    print(f"total={turn.total_ms:.0f}ms")

if __name__ == "__main__":
    main()
