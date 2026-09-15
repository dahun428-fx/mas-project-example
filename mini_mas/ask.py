import argparse

from mini_mas.classifier import classify
from mini_mas.orchestrator import Orchestrator
from mini_mas.router import ROUTE_MAP

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("query")
    parser.add_argument("--agent", choices=ROUTE_MAP.keys(), default=None)
    args = parser.parse_args()

    turn = Orchestrator().run(args.query, force_agent=args.agent)

    flag = " (fallback)" if turn.fallback else ""
    print(f"[분류] agent={turn.agent}{flag} · {turn.reason} · {turn.classify_ms:.0f}ms\n")
    print(turn.result.text)
    m = turn.result.metadata
    print(f"\n[{turn.result.name}] model={m['model']} tokens={m['tokens']} total={turn.total_ms:.0f}ms")

if __name__ == "__main__":
    main()