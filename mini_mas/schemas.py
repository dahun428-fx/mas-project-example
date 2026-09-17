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
    agents: list[str]
    reason: str
    fallback: bool
    results: list[AgentResult]
    errors: dict[str, str]
    final_text: str
    refined: bool
    classify_ms: float
    agents_ms: float
    synth_ms: float
    total_ms: float