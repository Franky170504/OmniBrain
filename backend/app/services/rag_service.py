from __future__ import annotations

import os
from pathlib import Path
from typing import Any
from dotenv import load_dotenv
from openai import OpenAI,RateLimitError
from backend.app.services.qdrant_service import QdrantService

from config.settings import settings

load_dotenv(Path(".env"))
class RagService:
    def __init__(self, qdrant_service : QdrantService) -> None:
        self.qdrant_service = qdrant_service
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is not configured.")

        self.client = OpenAI(
            api_key=settings.openai_api_key,
            max_retries=0
        )

        self.model = settings.openai_model

    @staticmethod
    def build_context(
        results: list[dict[str, Any]],
    ) -> str:
        sections: list[str] = []

        for index, result in enumerate(results, start=1):
            filename = (
                result.get("filename")
                or "Unknown document"
            )

            page_start = result.get("page_start")
            page_end = result.get("page_end")

            if page_start == page_end:
                page_label = f"page {page_start}"
            else:
                page_label = (
                    f"pages {page_start}-{page_end}"
                )

            sections.append(
                f"[Source {index}: {filename}, {page_label}]\n"
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

        prompt = f"""
You answer questions using only the supplied document context.

Rules:
1. Do not use outside knowledge.
2. If the answer is not present, clearly say that it is not available in the document.
3. Cite supporting passages using [Source 1], [Source 2], and so on.
4. Do not invent page numbers, facts, or citations.
5. Give a direct answer before additional explanation.

Document context:
{context}

Question:
{question}
""".strip()

        response = self.client.responses.create(
            model=self.model,
            input=prompt,
            store=False,
        )

        return {
            "answer": response.output_text,
            "sources": [
                {
                    "chunk_id": result.get("chunk_id"),
                    "filename": result.get("filename"),
                    "page_start": result.get("page_start"),
                    "page_end": result.get("page_end"),
                    "score": result.get("score"),
                }
                for result in results
            ],
        }       

   