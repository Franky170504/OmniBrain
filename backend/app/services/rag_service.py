from __future__ import annotations

from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq

<<<<<<< HEAD
from config.settings import settings
from app.services.guardrail_service import RetrievalGuardrail
=======
from app.core.app_config import settings
>>>>>>> upstream/feature/database
from app.services.qdrant_service import QdrantService

class RagService:
    def __init__(self, qdrant_service: QdrantService) -> None:
        self.qdrant_service = qdrant_service
        self.model = ChatGroq(
            model=settings.groq_model,
            api_key=settings.groq_api_key,
            temperature=0,
            max_retries=0,
        )

    @staticmethod
    def build_context(results: list[dict[str, Any]]) -> str:
        sections: list[str] = []

        for index, result in enumerate(results, start=1):
            filename = result.get("filename", "Unknown document")
            page_start = result.get("page_start")
            page_end = result.get("page_end")
            sections.append(
                f"[Source {index}: {filename}, "
                f"pages {page_start}-{page_end}]\n"
                f"{result.get('text', '')}"
            )
        return "\n\n".join(sections)

    def answer(self, *, question: str, user_id: str, document_id: str | None = None) -> dict[str, Any]:
<<<<<<< HEAD
        results = self.qdrant_service.search(question, user_id=user_id, document_id=document_id)
        retrieval_attempts = 1

        if not RetrievalGuardrail.is_relevant(results):
            rewritten_query = RetrievalGuardrail.rewrite_query(question)
            results = self.qdrant_service.search(
                rewritten_query,
                user_id=user_id,
                document_id=document_id,
            )
            retrieval_attempts = 2

        if not RetrievalGuardrail.is_relevant(results):
=======
        results = self.qdrant_service.search(
            question,
            user_id=user_id,
            document_id=document_id,
            limit=settings.qdrant_top_k,
            score_threshold=settings.qdrant_score_threshold,
        )

        # Controlled fallback:
        # If no high-confidence result meets the primary threshold,
        # retry with the lower fallback threshold.
        if not results:
            results = self.qdrant_service.search(
                question,
                user_id=user_id,
                document_id=document_id,
                limit=settings.qdrant_top_k,
                score_threshold=settings.qdrant_fallback_threshold,
            )

        if not results:
>>>>>>> upstream/feature/database
            return {
                "answer": RetrievalGuardrail.refusal(),
                "sources": [],
                "retrieval_attempts": retrieval_attempts,
                "error": "Guardrail blocked an ungrounded document response.",
            }

        context = self.build_context(results)
        response = self.model.invoke(
            [
                SystemMessage(
                    content=(
                        "Answer only from the supplied document "
                        "context. Cite sources as [Source 1], "
                        "[Source 2], and so on."
                    )
                ),
                HumanMessage(
                    content=f"""
                        Document context:{context}
                        Question:{question}
                        """.strip()
                ),
            ]
        )
        answer = (
            response.content
            if isinstance(response.content, str)
<<<<<<< HEAD
            else str(response.content))
        answer = RetrievalGuardrail.validate_answer(answer, len(results))
=======
            else str(response.content)
        )
>>>>>>> upstream/feature/database

        return {
            "answer": answer,
            "retrieval_attempts": retrieval_attempts,
            "error": None,
            "sources": [
                {
                    "point_id": item.get("point_id"),
                    "chunk_id": item.get("chunk_id"),
                    "document_id": item.get("document_id"),
                    "filename": item.get("filename"),
                    "page_start": item.get("page_start"),
                    "page_end": item.get("page_end"),
                    "score": item.get("score"),
                }
                for item in results
            ],
        }
