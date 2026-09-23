from datetime import date

from mini_mas.llm import OpenAILLM
from mini_mas.prompts import render
from mini_mas.rag import Retriever
from mini_mas.schemas import AgentResult


def build_reference_block(hits: list[dict]) -> str:
    """검색 결과를 프롬프트용 [참고 자료] 블록으로. 결과가 없으면 빈 문자열."""
    if not hits:
        return ""
    lines = ["[참고 자료]"]
    for hit in hits:
        lines.append(f"- ({hit['source']}) {hit['title']}: {hit['text']}")
    return "\n".join(lines) + "\n"


class KnowledgeAgent:
    name = "Knowledge"

    def __init__(self, llm=None, retriever=None):
        self.llm = llm or OpenAILLM(model="gpt-5.4-nano", agent="Knowledge")
        self._retriever = retriever

    @property
    def retriever(self):
        # 인덱스 파일 읽기를 실제 검색 시점까지 미룬다 (테스트는 주입해서 파일을 안 읽음)
        if self._retriever is None:
            self._retriever = Retriever()
        return self._retriever

    def run(self, query: str) -> AgentResult:
        hits = self.retriever.search(query)
        context = build_reference_block(hits)

        system, user = render(
            "knowledge",
            today=date.today().isoformat(),
            context=context,
            query=query,
        )
        resp = self.llm.invoke(system=system, user=user)

        return AgentResult(
            name=self.name,
            text=resp.text,
            docs=[
                {"id": h["id"], "title": h["title"], "source": h["source"], "score": h["score"]}
                for h in hits
            ],
            metadata={
                "block_type": "general",
                "model": resp.model,
                "finish_reason": resp.finish_reason,
                "latency_ms": resp.latency_ms,
                "tokens": resp.input_tokens + resp.output_tokens,
                "used_rag": bool(hits),
            },
        )
