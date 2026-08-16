from __future__ import annotations

from app.agents.state import AgentState
from app.services.vision_service import VisionService


class VisionAgentNode:
    """
    Vision Agent.

    Handles:
    - tables
    - charts
    - graphs
    - figures
    - diagrams
    - images
    """

    def __init__(
        self,
        vision_service: VisionService,
    ) -> None:
        self.vision_service = (
            vision_service
        )

    def __call__(
        self,
        state: AgentState,
    ) -> dict:
        question = (
            state
            .get("question", "")
            .strip()
        )

        document_id = state.get(
            "document_id"
        )

        if not question:
            return {
                "answer": (
                    "Please enter a visual question."
                ),
                "sources": [],
                "visual_context": [],
                "visual_type": None,
                "page_number": None,
                "error": "Missing question",
            }

        if not document_id:
            return {
                "answer": (
                    "Please upload or select a "
                    "document before asking about "
                    "its visual content."
                ),
                "sources": [],
                "visual_context": [],
                "visual_type": None,
                "page_number": None,
                "error": "Missing document_id",
            }

        try:
            result = (
                self.vision_service.answer(
                    question=question,
                    document_id=document_id,
                )
            )

            return {
                "answer": result.get(
                    "answer",
                    "No visual answer was produced.",
                ),
                "sources": result.get(
                    "sources",
                    [],
                ),
                "visual_context": result.get(
                    "visual_context",
                    [],
                ),
                "visual_type": result.get(
                    "visual_type"
                ),
                "page_number": result.get(
                    "page_number"
                ),
                "error": result.get(
                    "error"
                ),
            }

        except Exception as exc:
            return {
                "answer": (
                    "Visual analysis failed."
                ),
                "sources": [],
                "visual_context": [],
                "visual_type": None,
                "page_number": None,
                "error": str(exc),
            }