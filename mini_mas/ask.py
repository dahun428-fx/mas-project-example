import sys

from mini_mas.llm import OpenAILLM

SYSTEM = (
    "당신은 건강검진 결과를 쉽게 설명하는 건강 코치입니다. "
    "진단이나 처방은 하지 않습니다. 3문장 이내로 답합니다."
)

def main():
    query = " ".join(sys.argv[1:])
    llm = OpenAILLM(model="gpt-5.4-nano")
    resp = llm.invoke(system=SYSTEM, user=query)
    print(resp.text)
    print(f"\n[{resp.model}] in={resp.input_tokens} out={resp.output_tokens} "
        f"finish={resp.finish_reason} {resp.latency_ms:.0f}ms")

if __name__ == "__main__":
    main()