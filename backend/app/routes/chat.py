from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_chat_service
from app.models.schemas import ChatRequest,ChatResponse,ErrorResponse
from app.services.chat_service import ChatService

LOGGER = logging.getLogger("omnibrain.routes.chat")

router = APIRouter(prefix="/chat", tags=["Document Chat"])

@router.post(
    "",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorResponse,
            "description": "Invalid chat request.",
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ErrorResponse,
            "description": "Question answering failed.",
        },
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "model": ErrorResponse,
            "description": "Chat service is unavailable.",
        },
    },
    summary="Chat With Document",
    description=(
        "Routes the question through the LangGraph supervisor. "
        "The supervisor selects the document, SQL, general, or clarification "
        "agent."
    ),
)

def chat_with_document(
    request: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service),
) -> ChatResponse:
    """
    Process a user question through the OmniBrain LangGraph workflow.

    The graph performs the following steps:

    1. The supervisor evaluates the question.
    2. The supervisor selects an appropriate subagent.
    3. The selected agent produces the final answer.
    4. Document answers may include Qdrant source references.
    """

    question = request.question.strip()
    user_id = request.user_id.strip()
    document_id = (
        request.document_id.strip()
        if request.document_id
        else None
    )

    if not question:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question cannot be empty.",
        )

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user_id cannot be empty.",
        )

    try:
        LOGGER.info(
            "Processing chat request user_id=%s document_id=%s",
            user_id,
            document_id,
        )

        result = chat_service.ask(
            question=question,
            user_id=user_id,
            document_id=document_id,
        )

        answer = result.get("answer")

        if not answer:
            raise RuntimeError(
                "The agent graph completed without producing an answer."
            )

        response = ChatResponse(
            answer=answer,
            sources=result.get("sources", []),
            route=result.get("route"),
            route_reason=result.get("route_reason"),
            error=result.get("error"),
            retrieval_attempts=result.get("retrieval_attempts", 0),
        )

        LOGGER.info("Chat request completed route=%s source_count=%d", response.route, len(response.sources))
        return response

    except HTTPException:
        raise

    except ValueError as exc:
        LOGGER.warning(
            "Invalid chat request: %s",
            exc,
        )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except RuntimeError as exc:
        LOGGER.exception(
            "Chat workflow failed: %s",
            exc
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Question answering failed: {exc}",
        ) from exc

    except Exception as exc:
        LOGGER.exception(
            "Unexpected chat workflow error",
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Question answering failed due to an unexpected error: "
                f"{exc}"
            ),
        ) from exc
