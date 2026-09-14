import sys

import argparse

from mini_mas.agents.chat import ChatAgent
from mini_mas.agents.knowledge import KnowledgeAgent
from mini_mas.agents.numbers import NumbersAgent


AGENTS = {
    "numbers": NumbersAgent,
    "knowledge": KnowledgeAgent,
    "chat": ChatAgent,
}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("query")
    parser.add_argument("--agent", choices=AGENTS.keys(), default="knowledge")
    args = parser.parse_args()

    result = AGENTS[args.agent]().run(args.query)
    print(result.text)
    m = result.metadata
    print(f"\n[{result.name}] model={m['model']} finish={m['finish_reason']} "
          f"tokens={m['tokens']} {m['latency_ms']:.0f}ms")

if __name__ == "__main__":
    main()