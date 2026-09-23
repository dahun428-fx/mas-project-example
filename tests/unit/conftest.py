import time

import pytest

from mini_mas.llm import LLMResponse


class FakeLLM:
    def __init__(self, text="가짜 답변입니다.", delay=0.0, error=None):
        self.model = "fake-model"
        self.text = text
        self.delay = delay
        self.error = error
        self.calls = []

    def invoke(self, system, user, max_tokens=512):
        self.calls.append({"system": system, "user": user, "max_tokens": max_tokens})
        if self.delay:
            time.sleep(self.delay)
        if self.error:
            raise self.error
        return LLMResponse(
            text=self.text,
            model=self.model,
            input_tokens=10,
            output_tokens=5,
            finish_reason="stop",
            latency_ms=self.delay * 1000,
        )


@pytest.fixture
def fake_llm():
    return FakeLLM()


@pytest.fixture(autouse=True)
def no_network_embed(monkeypatch):
    """모든 테스트에서 임베딩 API 호출을 막는다.

    KnowledgeAgent 는 retriever 를 안 넘기면 진짜 Retriever 를 만들고, 그 안에서 OpenAI
    임베딩 API 를 부른다. 유닛 테스트가 네트워크를 타면 느려지고 키가 없으면 멈춘다.
    autouse=True 라 모든 테스트에 자동 적용된다.
    """
    from mini_mas import rag

    def fake_embed(texts: list[str]) -> list[list[float]]:
        return [[1.0] + [0.0] * (rag.EMBED_DIM - 1) for _ in texts]

    monkeypatch.setattr(rag, "embed", fake_embed)


@pytest.fixture(autouse=True)
def no_network_llm(monkeypatch):
    """유닛 테스트에서 실제 LLM 호출을 막는다.

    LLM 을 주입하지 않은 코드 경로가 있으면 조용히 진짜 API 를 부르고 돈이 나간다.
    (실제로 orchestrator 테스트가 synth_llm 을 안 넘겨 합성기가 OpenAI 를 호출하고 있었다.)
    여기서 막아 두면 그런 경로가 테스트에서 바로 드러난다.
    """
    from mini_mas.llm import OpenAILLM

    def blocked(self, *args, **kwargs):
        raise RuntimeError(
            f"유닛 테스트에서 실제 LLM 을 호출했습니다 (model={self.model}, agent={self.agent}). "
            "가짜 LLM 을 주입하세요."
        )

    monkeypatch.setattr(OpenAILLM, "invoke", blocked)
