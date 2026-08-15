from __future__ import annotations

from app.agents.state import AgentState
from app.services.rag_service import RagService


class SearchAgentNode:
    """
    Search Agent.

    Searches textual document content using
    RagService + Qdrant.
    """

    def __init__(
        self,
        rag_service: RagService,
    ) -> None:
        self.rag_service = rag_service

    def __call__(
        self,
        state: AgentState,
    ) -> dict:
        question = (
            state
            .get("question", "")
            .strip()
        )

        user_id = (
            state
            .get("user_id", "")
            .strip()
        )

        document_id = state.get(
            "document_id"
        )

        if not question:
            return {
                "answer": (
                    "Please enter a question."
                ),
                "sources": [],
                "retrieval_attempts": 0,
                "error": "Missing question",
            }

        if not document_id:
            return {
                "answer": (
                    "Please upload or select a "
                    "document before searching it."
                ),
                "sources": [],
                "retrieval_attempts": 0,
                "error": "Missing document_id",
            }

        try:
            result = self.rag_service.answer(
                question=question,
                user_id=user_id,
                document_id=document_id,
            )

            return {
                "answer": result.get(
                    "answer",
                    "No answer was produced.",
                ),
                "sources": result.get(
                    "sources",
                    [],
                ),
                "retrieval_attempts": (
                    result.get(
                        "retrieval_attempts",
                        1,
                    )
                ),
                "error": result.get(
                    "error"
                ),
            }

        except Exception as exc:
            return {
                "answer": (
                    "Document search failed."
                ),
                "sources": [],
                "retrieval_attempts": 1,
                "error": str(exc),
            }