from __future__ import annotations

from fastapi import APIRouter,Depends,HTTPException,status

from backend.app.dependencies import get_chat_service
from backend.app.models.schemas import (ChatRequest,ChatResponse)
from backend.app.services.chat_service import ChatService

router = APIRouter(prefix="/chat",tags=["Document Chat"],)

@router.post("",response_model=ChatResponse,)
def chat_with_document(
    request: ChatRequest,chat_service: ChatService = Depends(get_chat_service),) -> ChatResponse:
    try:
        result = chat_service.ask(
            question=request.question,
            user_id=request.user_id,
            document_id=request.document_id,
        )

        return ChatResponse(**result)

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Question answering failed: {exc}",
        ) from exc