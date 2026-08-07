from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_chat_service, get_db
from app.models.schemas import ChatRequest, ChatResponse
from app.services.chat_service import ChatService


router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("", response_model=ChatResponse)
async def chat(
    payload: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service),
    session: AsyncSession = Depends(get_db),
) -> ChatResponse:
    try:
        result = await chat_service.ask(
            question=payload.question,
            user_id=payload.user_id,
            document_id=payload.document_id,
            session_id=payload.session_id,
            session=session,
        )
        return ChatResponse(**result)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Chat failed: {exc}") from exc
