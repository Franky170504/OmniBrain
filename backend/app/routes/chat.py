from fastapi import APIRouter, status
from app.models.schemas import ChatRequest, ChatResponse, ErrorResponse
from app.services.chat_service import chat_service

router = APIRouter(tags=["Document Chat"])


@router.post(
    "/chat",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Query Document (Mock Chat)",
    description="Submit a question regarding an uploaded document specified by its document_id. Returns a structured mock answer ready for future AI pipeline integration.",
    responses={
        200: {"model": ChatResponse, "description": "Successful chat query response."},
        404: {"model": ErrorResponse, "description": "Document ID not found in storage."},
        422: {"description": "Validation error for request payload."}
    }
)
async def chat_with_document(request: ChatRequest) -> ChatResponse:
    """
    Accepts document_id and question, checks document availability,
    and returns a mock response payload.
    """
    response_data = await chat_service.get_chat_response(
        document_id=request.document_id,
        question=request.question
    )
    return ChatResponse(**response_data)
