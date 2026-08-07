from __future__ import annotations

from app.agents.state import AgentState
from app.services.rag_service import RagService


class DocumentAgent:
    def __init__(self, rag_service: RagService) -> None:
        self.rag_service = rag_service

    async def __call__(self, state: AgentState) -> dict:
        document_id = state.get("document_id")
        if not document_id:
            return {
                "answer": "Please upload or select a document before asking a document-specific question.",
                "sources": [],
                "context_items": [],
                "error": None,
            }

        result = await self.rag_service.answer(
            question=state["question"],
            user_id=state["user_id"],
            document_id=document_id,
        )
        return result
