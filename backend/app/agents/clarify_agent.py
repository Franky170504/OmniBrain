from __future__ import annotations

from app.agents.state import AgentState


class ClarifyAgentNode:
    def __call__(self, state: AgentState) -> dict:
        question = state.get("question", "").strip()
        document_id = state.get("document_id")

        if not question:
            answer = "Please enter a question."
        elif not document_id:
            answer = (
                "Your question appears to refer to a document, "
                "but no document is selected."
            )
        else:
            answer = (
                "Please provide more information so I can route "
                "your question correctly."
            )

        return {
            "answer": answer,
            "sources": [],
            "error": None,
        }