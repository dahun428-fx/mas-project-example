import sys

from mini_mas.agents.knowledge import KnowledgeAgent

def main():
    query = " ".join(sys.argv[1:])
    result = KnowledgeAgent().run(query)
    print(result.text)
    m = result.metadata
    print(f"\n[{result.name}] model={m['model']} finish={m['finish_reason']} "
          f"tokens={m['tokens']} {m['latency_ms']:.0f}ms")

if __name__ == "__main__":
    main()