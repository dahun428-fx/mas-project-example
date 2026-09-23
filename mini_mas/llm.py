import os
import time
from dataclasses import dataclass

from dotenv import load_dotenv
from openai import OpenAI

from mini_mas.trace import record

load_dotenv()  # .env 파일에서 환경변수 로드

@dataclass
class LLMResponse :
    text: str
    model: str
    input_tokens: int
    output_tokens: int
    finish_reason: str
    latency_ms: float

class OpenAILLM:
    def __init__(self, model: str, agent: str = "unknown"):
        self.model = model
        self.agent = agent
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def invoke(self, system:str, user:str, max_tokens: int = 512) -> LLMResponse:
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ]
        t0 = time.perf_counter()
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_completion_tokens=max_tokens
        )
        latency = (time.perf_counter() - t0) * 1000  # ms
        choice = resp.choices[0]

        record(
            model=self.model,
            agent=getattr(self, "agent", "unknown"),
            input_tokens=resp.usage.prompt_tokens,
            output_tokens=resp.usage.completion_tokens,
            latency_ms=latency,
            finish_reason=choice.finish_reason,
            query=user,
            response=choice.message.content or "",
        )

        return LLMResponse(
            text=choice.message.content or "",
            model=self.model,
            input_tokens=resp.usage.prompt_tokens,
            output_tokens=resp.usage.completion_tokens,
            finish_reason=choice.finish_reason,
            latency_ms=latency
        )
