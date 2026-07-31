from pydantic import BaseModel
from typing import Literal
import datetime

class TraceEvent(BaseModel):
    trace_id: str
    span_id: str
    parent_span_id: str | None
    agent: Literal['orchestrator', 'validator_subagent', 'memo_subagent']
    iteration: int
    event_type: Literal['perceive', 'reason', 'act', 'observe', 'escalation', 'subagent_invocation', 'subagent_result']
    timestamp: datetime
    content: dict
    latency_ms: float
    token_count: int

def log_event(event: TraceEvent) -> None:
    ...