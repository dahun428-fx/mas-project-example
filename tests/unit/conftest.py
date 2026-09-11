import pytest

from mini_mas.llm import LLMResponse

class FakeLLM:
    def __init__(self, text="가짜 답변입니다."):
        self.model = "fake-model"
        self.text = text
        self.calls = []
    def invoke(self, system, user, max_tokens=512):
        self.calls.append({"system": system, "user": user, "max_tokens": max_tokens})
        return LLMResponse(
            text=self.text,
            model=self.model,
            input_tokens=10,
            output_tokens=5,
            finish_reason="stop",
            latency_ms=1.0,
        )

@pytest.fixture
def fake_llm():
    return FakeLLM()