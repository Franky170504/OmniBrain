from __future__ import annotations

import os
from typing import Any
from dotenv import load_dotenv
from openai import OpenAI
from services import QdrantService
load_dotenv()


class RagService:
    def __init__(self) -> None:
        self.vector_store = QdrantService()
        self.llm = OpenAI(
            api_key=os.environ["OPENAI_API_KEY"]
        )
        self.model = os.getenv(
            "OPENAI_MODEL",
        )

    @staticmethod
    def build_context(
        results: list[dict[str, Any]],
    ) -> str:
        context_parts: list[str] = []

        for index, result in enumerate(results, start=1):
            filename = result.get("filename") or "Unknown document"
            page_start = result.get("page_start")
            page_end = result.get("page_end")

            citation = f"{filename}, pages {page_start}-{page_end}"

            context_parts.append(
                f"[Source {index}: {citation}]\n"
                f"{result['text']}"
            )

        return "\n\n".join(context_parts)

    def answer(
        self,
        *,
        question: str,
        user_id: str,
        document_id: str | None = None,
    ) -> dict[str, Any]:
        results = self.vector_store.search(
            question,
            user_id=user_id,
            document_id=document_id,
            limit=6,
        )

        if not results:
            return {
                "answer": (
                    "I could not find relevant information "
                    "in the uploaded document."
                ),
                "sources": [],
            }

        context = self.build_context(results)

        prompt = f"""
Answer the question using only the supplied context.

Rules:
- Do not use information outside the context.
- If the context does not contain the answer, say so.
- Cite sources using [Source 1], [Source 2], and so on.
- Give a direct, clear answer.

Context:
{context}

Question:
{question}
""".strip()

        response = self.llm.responses.create(
            model=self.model,
            input=prompt,
            store=False,
        )

        return {
            "answer": response.output_text,
            "sources": [
                {
                    "filename": result["filename"],
                    "page_start": result["page_start"],
                    "page_end": result["page_end"],
                    "score": result["score"],
                }
                for result in results
            ],
        }