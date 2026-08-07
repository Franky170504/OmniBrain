from __future__ import annotations

from fastapi import HTTPException, Request, status

from app.services.qdrant_service import QdrantService
from app.services.document_service import DocumentService
from app.services.rag_service import RagService
from app.agents.graph import OmniBrainGraph
from app.services.chat_service import ChatService

def _get_app_state_service(request: Request, attribute_name: str):
    service = getattr(request.app.state, attribute_name,None)
    if service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                f"Application service '{attribute_name}' "
                "is not initialized."
            ),
        )
    return service

def get_qdrant_service(request: Request) -> QdrantService:
    return _get_app_state_service(request,"qdrant_service")

def get_document_service(request: Request) -> DocumentService:
    return _get_app_state_service(request,"document_service")

def get_rag_service(request: Request) -> RagService:
    return _get_app_state_service(request,"rag_service")

def get_agent_graph(request: Request) -> OmniBrainGraph:
    return _get_app_state_service(request,"agent_graph")

def get_chat_service(request: Request) -> ChatService:
    return _get_app_state_service(request,"chat_service")
