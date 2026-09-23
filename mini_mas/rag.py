
import json
import math
import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from mini_mas.trace import record

load_dotenv()

DOCS_PATH = Path(__file__).parent.parent / "data" / "knowledge.jsonl"
INDEX_PATH = Path(__file__).parent.parent / "data" / "knowledge_index.json"

EMBED_MODEL = "text-embedding-3-small"
EMBED_DIM = 256
TOP_K = 3
THRESHOLD = 0.35

def embed(texts: list[str]) -> list[list[float]]:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    t0 = time.perf_counter()
    resp = client.embeddings.create(model=EMBED_MODEL, input=texts, dimensions=EMBED_DIM)
    record(
        model=EMBED_MODEL,
        agent="RAG",
        input_tokens=resp.usage.prompt_tokens,
        latency_ms=(time.perf_counter() - t0) * 1000,
        query=texts[0][:200],
    )
    return [item.embedding for item in resp.data]

def cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a,b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)

def load_docs(path: Path = DOCS_PATH) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]

def build_index(docs_path: Path = DOCS_PATH, index_path: Path = INDEX_PATH) -> int:
    docs = load_docs(docs_path)
    vectors = embed([f"{d['title']}\n{d['text']}" for d in docs])
    for doc, vector in zip(docs, vectors):
        doc["embedding"] = vector
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(docs, f, ensure_ascii=False)
    return len(docs)

class Retriever:
    def __init__(self, index_path: Path = INDEX_PATH, embed_fn=None, index=None):
        self.embed_fn = embed_fn or embed
        if index is not None:
            self.index = index
        elif index_path.exists():
            with open(index_path, encoding="utf-8") as f:
                self.index = json.load(f)
        else:
            # 인덱스가 없으면 검색 없이 동작한다 (근거 없이 답하게 두고, 빌드를 안내)
            print(f"[rag] 인덱스가 없습니다: {index_path}. `python -m mini_mas.rag build` 로 생성하세요.")
            self.index = []

    def search(self, query: str, k: int = TOP_K, threshold: float = THRESHOLD) -> list[dict]:
        if not self.index:
            return []

        query_vector = self.embed_fn([query])[0]

        scored = []
        for doc in self.index:
            score = cosine(query_vector, doc["embedding"])
            if score >= threshold:
                scored.append({"id": doc["id"], "title":doc["title"], "text":doc["text"], "source": doc["source"], "score": round(score, 3)})

        scored.sort(key=lambda d: d["score"], reverse=True)
        return scored[:k]

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "build":
        count = build_index()
        print(f"인덱스 생성 완료 : {count}건 -> {INDEX_PATH}")
    else:
        query = " ".join(sys.argv[1:]) or "LDL 기준이 뭐야 ?"
        for hit in Retriever().search(query):
            print(f"{hit['score']:.3f}  [{hit['id']}] {hit['title']} — {hit['text'][:40]}...")
