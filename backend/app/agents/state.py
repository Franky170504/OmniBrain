from __future__ import annotations

from typing import Any, Literal, TypedDict


AgentRoute = Literal[
    "search_agent",
    "vision_agent",
    "sql_agent",
    "end",
]


class AgentState(TypedDict, total=False):
    # Request
    question: str
    user_id: str
    document_id: str | None

    # Supervisor
    route: AgentRoute
    route_reason: str

    # Final response
    answer: str
    sources: list[dict[str, Any]]
    error: str | None

    # Search Agent
    retrieval_attempts: int

    # Vision Agent
    visual_context: list[dict[str, Any]]
    visual_type: str | None
    page_number: int | None

    # SQL Agent
    generated_sql: str | None
    sql_rows: list[dict[str, Any]]