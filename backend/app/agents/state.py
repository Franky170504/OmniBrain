from __future__ import annotations

from typing import Any, Literal, TypedDict


AgentRoute = Literal["document_agent", "general_agent", "clarify_agent"]


class AgentState(TypedDict, total=False):
    question: str
    user_id: str
    document_id: str | None
    route: AgentRoute
    route_reason: str
    answer: str
    sources: list[dict[str, Any]]
    context_items: list[dict[str, Any]]
    retrieval_latency_ms: int | None
    error: str | None
