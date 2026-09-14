import argparse

from mini_mas.classifier import classify
from mini_mas.router import ROUTE_MAP, resolve

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("query")
    parser.add_argument("--agent", choices=ROUTE_MAP.keys(), default="knowledge")
    args = parser.parse_args()

    if args.agent:
        agent_key, reason = args.agent, "수동 지정"
    else:
        decision = classify(args.query)
        agent_key, reason = decision["agent"], decision["reason"]
        if decision.get("fallback"):
            reason = f"분류 실패 → {agent_key} (raw: {decision['raw'][:60]})"

    print(f"[분류] agent={agent_key} · {reason}\n")
    result = resolve(agent_key).run(args.query)
    print(result.text)
    m = result.metadata
    print(f"\n[{result.name}] model={m['model']} finish={m['finish_reason']} "
          f"tokens={m['tokens']} {m['latency_ms']:.0f}ms")

if __name__ == "__main__":
    main()