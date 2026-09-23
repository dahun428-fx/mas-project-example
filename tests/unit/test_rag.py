
from mini_mas.agents.knowledge import KnowledgeAgent, build_reference_block
from mini_mas.rag import Retriever, cosine
from tests.unit.conftest import FakeLLM

FAKE_INDEX = [
    {"id": "K01", "title": "공복혈당", "text": "정상은 70~99 mg/dL 입니다.", "source": "안내서", "embedding": [1.0, 0.0]},
    {"id": "K03", "title": "LDL", "text": "130 mg/dL 미만이 적정입니다.", "source": "안내서", "embedding": [0.0, 1.0]},
]


def fake_embed_for(vector):
    return lambda texts: [vector]


def test_cosine_basics():
    assert cosine([1, 0], [1, 0]) == 1.0
    assert cosine([1, 0], [0, 1]) == 0.0
    assert cosine([0, 0], [1, 0]) == 0.0


def test_search_returns_closest_doc():
    r = Retriever(index=FAKE_INDEX, embed_fn=fake_embed_for([0.0, 1.0]))
    hits = r.search("LDL 기준")
    assert hits[0]["id"] == "K03"
    assert hits[0]["score"] == 1.0


def test_search_drops_below_threshold():
    r = Retriever(index=FAKE_INDEX, embed_fn=fake_embed_for([0.71, 0.71]))
    assert r.search("q", threshold=0.9) == []


def test_search_respects_k():
    r = Retriever(index=FAKE_INDEX, embed_fn=fake_embed_for([0.71, 0.71]))
    assert len(r.search("q", k=1, threshold=0.1)) == 1


def test_reference_block_empty_when_no_hits():
    assert build_reference_block([]) == ""


def test_agent_puts_reference_into_prompt(fake_llm):
    r = Retriever(index=FAKE_INDEX, embed_fn=fake_embed_for([0.0, 1.0]))
    result = KnowledgeAgent(llm=fake_llm, retriever=r).run("LDL 기준이 뭐야?")
    prompt = fake_llm.calls[0]["user"]
    assert "[참고 자료]" in prompt
    assert "130 mg/dL 미만" in prompt
    assert result.docs[0]["id"] == "K03"
    assert result.metadata["used_rag"] is True


def test_agent_without_hits_has_no_reference_block():
    # 두 문서와 모두 반대 방향인 질문 벡터 → cosine 이 음수라 threshold 에서 전부 잘린다
    r = Retriever(index=FAKE_INDEX, embed_fn=fake_embed_for([-1.0, -1.0]))
    llm = FakeLLM()
    result = KnowledgeAgent(llm=llm, retriever=r).run("오늘 점심 뭐 먹지")

    assert result.docs == []
    assert result.metadata["used_rag"] is False
    assert "[참고 자료]" not in llm.calls[0]["user"]
