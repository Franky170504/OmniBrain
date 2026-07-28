from __future__ import annotations

from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq

from config.settings import settings
from app.services.qdrant_service import QdrantService


class RagService:
    def __init__(
        self,
        qdrant_service: QdrantService,
    ) -> None:
        self.qdrant_service = qdrant_service

        self.model = ChatGroq(
            model=settings.groq_model,
            api_key=settings.groq_api_key,
            temperature=0,
            max_retries=0,
        )

    @staticmethod
    def build_context(
        results: list[dict[str, Any]],
    ) -> str:
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

    def answer(
        self,
        *,
        question: str,
        user_id: str,
        document_id: str | None = None,
    ) -> dict[str, Any]:
        results = self.qdrant_service.search(
            question,
            user_id=user_id,
            document_id=document_id,
        )

        if not results:
            return {
                "answer": (
                    "I could not find relevant information "
                    "in the indexed document."
                ),
                "sources": [],
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
Document context:

{context}

Question:

{question}
""".strip()
                ),
            ]
        )

        answer = (
            response.content
            if isinstance(response.content, str)
            else str(response.content)
        )

        return {
            "answer": answer,
            "sources": [
                {
                    "chunk_id": item.get("chunk_id"),
                    "filename": item.get("filename"),
                    "page_start": item.get("page_start"),
                    "page_end": item.get("page_end"),
                    "score": item.get("score"),
                }
                for item in results
            ],
        }