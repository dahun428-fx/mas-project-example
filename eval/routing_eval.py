import json
import time
from collections import Counter
from pathlib import Path

from mini_mas.classifier import classify

VALID_AGENTS = {"numbers", "knowledge", "chat"}
GOLDEN = Path(__file__).parent / "golden_routing.jsonl"

def load_golden(path: Path = GOLDEN) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        items = [json.loads(line) for line in f if line.strip()]
    for item in items:
        if item["agent"] not in VALID_AGENTS:
            raise ValueError(f"골든셋 #{item['id']} 의 정답 {item['agent']!r} 가 잘못됐습니다. {VALID_AGENTS} 중 하나여야 합니다.")
        if "(" in item["query"] and "유형" in item["query"]:
            raise ValueError(f"골든셋 #{item['id']} 의 질문이 아직 안내 문구입니다: {item['query']!r}")
    return items

def main():
    items = load_golden()
    correct = 0
    fallbacks = 0
    confusion = Counter()
    wrong = []
    t0 = time.perf_counter()

    for item in items:
        d = classify(item["query"])
        predicted = d["agent"]
        confusion[(item["agent"], predicted)] += 1
        if d["fallback"]:
            fallbacks += 1
        if predicted == item["agent"]:
            correct += 1
        else:
            wrong.append((item["id"], item["query"], item["agent"], predicted, d["raw"]))
    n = len(items)
    print(f"정확도: {correct}/{n} = {correct / n:.1%}   fallback: {fallbacks}   {time.perf_counter() - t0:.1f}s\n")

    labels = ["numbers", "knowledge", "chat"]
    print("정답\\예측   " + "  ".join(f"{p:>9}" for p in labels))
    for truth in labels:
        print(f"{truth:>10}  " + "  ".join(f"{confusion[(truth, p)]:>9}" for p in labels))

    if wrong:
        print("\n틀린 문항:")
        for wid, q, truth, pred, reason in wrong:
            print(f"  #{wid} {q!r}  정답={truth} 예측={pred}  ({reason})")

if __name__ == "__main__":
    main()
