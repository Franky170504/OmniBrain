from __future__ import annotations

from app.agents.state import AgentState
from app.services.rag_service import RagService

class DocumentAgentNode:
    def __init__(self, rag_service: RagService) -> None:
        self.rag_service = rag_service

    def __call__(self, state: AgentState) -> dict:
        question = state.get("question", "").strip()
        user_id = state.get("user_id", "").strip()
        document_id = state.get("document_id")
        if not document_id:
            return {
                "answer": (
                    "Please upload or select a document before asking "
                    "a document-specific question."
                ),
                "sources": [],
                "error": "Missing document_id",
            }

        result = self.rag_service.answer(
            question=question,
            user_id=user_id,
            document_id=document_id,
        )

        return {
            "answer": result["answer"],
            "sources": result.get("sources", []),
            "error": None,
        }