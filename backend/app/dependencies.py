from fastapi import Request

from backend.app.services.chat_service import ChatService
from backend.app.services.document_service import DocumentService
from backend.app.services.rag_service import RagService
from backend.app.services.qdrant_service import QdrantService


def get_qdrant_service(request: Request) -> QdrantService:
    return request.app.state.qdrant_service


def get_document_service(request: Request) -> DocumentService:
    return request.app.state.document_service


def get_rag_service(request: Request) -> RagService:
    return request.app.state.rag_service


def get_chat_service(request: Request) -> ChatService:
    return request.app.state.chat_service