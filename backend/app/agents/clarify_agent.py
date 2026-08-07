from __future__ import annotations

from app.agents.state import AgentState


class ClarifyAgent:
    async def __call__(self, state: AgentState) -> dict:
        question = state.get("question", "")
        document_id = state.get("document_id")

        if not document_id and any(
            term in question.lower()
            for term in (
                "company",
                "document",
                "report",
                "uploaded",
                "book",
                "financial statement",
                "annual report",
            )
        ):
            answer = (
                "Please upload or select the relevant document before I analyze that document-specific request."
            )
        else:
            answer = (
                "Please clarify the missing analysis details—for example the company or document, "
                "financial metric, and comparison period you want me to use."
            )

        return {
            "answer": answer,
            "sources": [],
            "context_items": [],
            "retrieval_latency_ms": None,
            "error": None,
        }
