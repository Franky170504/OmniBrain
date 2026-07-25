from __future__ import annotations
from typing import Any
from backend.app.services.rag_service import RagService

class ChatService:
    def __init__(
        self,
        rag_service: RagService,
    ) -> None:
        self.rag_service = rag_service

    def ask(
        self,
        *,
        question: str,
        user_id: str,
        document_id: str | None = None,
    ) -> dict[str, Any]:
        return self.rag_service.answer(
            question=question,
            user_id=user_id,
            document_id=document_id,
        )