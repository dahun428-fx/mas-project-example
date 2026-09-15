from dataclasses import dataclass, field

@dataclass
class AgentResult:
    name: str
    text: str
    docs: list = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

@dataclass
class TurnResult:
    query: str
    agent: str
    reason: str
    fallback: bool
    result: AgentResult
    classify_ms: float
    total_ms: float

