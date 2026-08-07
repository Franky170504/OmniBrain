from __future__ import annotations

from time import perf_counter
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq

from app.core.app_config import app_settings
from app.services.qdrant_service import QdrantService


class RagService:
    def __init__(self, qdrant_service: QdrantService) -> None:
        self.qdrant_service = qdrant_service
        self.llm = ChatGroq(
            api_key=app_settings.GROQ_API_KEY,
            model=app_settings.GROQ_MODEL,
            temperature=0,
        )

    async def answer(
        self,
        *,
        question: str,
        user_id: str,
        document_id: str,
    ) -> dict[str, Any]:
        started = perf_counter()
        retrieved = self.qdrant_service.search(
            question,
            user_id=user_id,
            document_id=document_id,
            limit=app_settings.QDRANT_SEARCH_LIMIT,
            score_threshold=app_settings.QDRANT_SCORE_THRESHOLD,
        )
        retrieval_latency_ms = int((perf_counter() - started) * 1000)

        if not retrieved:
            return {
                "answer": "I could not find sufficiently relevant information in the selected document.",
                "sources": [],
                "context_items": [],
                "retrieval_latency_ms": retrieval_latency_ms,
                "error": None,
            }

        context_blocks: list[str] = []
        sources: list[dict[str, Any]] = []
        for index, item in enumerate(retrieved, start=1):
            label = f"Source {index}"
            page_start = item.get("page_start") or item.get("page_number")
            page_end = item.get("page_end") or page_start
            context_blocks.append(
                f"[{label}: {item.get('filename') or 'document'}, pages {page_start}-{page_end}]\n"
                f"{item.get('text') or ''}"
            )
            sources.append(
                {
                    "source_id": index,
                    "chunk_id": item.get("chunk_id"),
                    "document_id": item.get("document_id"),
                    "filename": item.get("filename"),
                    "page_start": page_start,
                    "page_end": page_end,
                    "score": item.get("score"),
                }
            )

        system_prompt = (
            "You are OmniBrain's document analysis agent. Answer only from the supplied document context. "
            "Do not invent values or use outside knowledge for document-specific facts. If the answer is not supported, "
            "say that it is not available in the retrieved context. Cite supporting passages using [Source 1], [Source 2], etc."
        )
        user_prompt = (
            "DOCUMENT CONTEXT:\n\n"
            + "\n\n".join(context_blocks)
            + f"\n\nQUESTION:\n{question}"
        )

        response = await self.llm.ainvoke(
            [SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)]
        )
        answer = str(response.content)

        return {
            "answer": answer,
            "sources": sources,
            "context_items": retrieved,
            "retrieval_latency_ms": retrieval_latency_ms,
            "error": None,
        }
