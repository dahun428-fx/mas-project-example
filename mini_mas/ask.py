import argparse

from mini_mas.orchestrator import Orchestrator
from mini_mas.router import ROUTE_MAP

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("query")
    parser.add_argument("--agent", choices=ROUTE_MAP.keys(), action="append", default=None)
    args = parser.parse_args()

    turn = Orchestrator().run(args.query, force_agents=args.agent)

    flag = " (fallback)" if turn.fallback else ""
    print(f"[분류] agents={turn.agents}{flag} · {turn.reason} · {turn.classify_ms:.0f}ms")
    print(f"[실행] {len(turn.agents)}개 동시 실행 · {turn.agents_ms:.0f}ms\n")
    
    for r in turn.results:
        m = r.metadata
        print(f"── {r.name} ({m['latency_ms']:.0f}ms, tokens={m['tokens']})")
        print(r.text + "\n")

    for key, error in turn.errors.items():
        print(f"── {key} 실패: {error}\n")

    if not turn.results:
        print("지금은 답변을 만들지 못했습니다. 잠시 후 다시 시도해 주세요.\n")

    print(f"total={turn.total_ms:.0f}ms")

if __name__ == "__main__":
    main()