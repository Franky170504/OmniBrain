from __future__ import annotations

from typing import Any


class RetrievalGuardrail:
    """Small, deterministic guardrails for grounded document responses."""

    MIN_RELEVANCE_SCORE = 0.45

    @classmethod
    def is_relevant(cls, results: list[dict[str, Any]]) -> bool:
        return bool(results) and max(float(item.get("score") or 0) for item in results) >= cls.MIN_RELEVANCE_SCORE

    @staticmethod
    def rewrite_query(question: str) -> str:
        """Create a narrower second retrieval query after a weak first pass."""
        return (
            f"{question.strip()} Focus on directly stated facts, named entities, "
            "and numerical evidence in the uploaded document."
        )

    @staticmethod
    def refusal() -> str:
        return (
            "I could not find sufficiently relevant evidence in the selected document, "
            "even after refining the search. Please rephrase the question or upload a more relevant source."
        )

    @staticmethod
    def has_citations(answer: str) -> bool:
        return "[Source " in answer

    @classmethod
    def validate_answer(cls, answer: str, source_count: int) -> str:
        if source_count and cls.has_citations(answer):
            return answer
        return (
            "I retrieved document context but could not produce a cited answer. "
            "Please ask a more specific question about the selected document."
        )
