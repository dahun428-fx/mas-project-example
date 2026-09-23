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
