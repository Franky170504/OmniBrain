from __future__ import annotations

from typing import Any
from langsmith import traceable

from app.agents.graph import OmniBrainGraph

class ChatService:
    def __init__(self, agent_graph: OmniBrainGraph) -> None:
        self.agent_graph = agent_graph

    @traceable(name="omnibrain-chat-request", run_type="chain")
    def ask(self, *, question: str, user_id: str, document_id: str | None = None,) -> dict[str, Any]:
        return self.agent_graph.invoke(
            question=question,
            user_id=user_id,
            document_id=document_id,
        )