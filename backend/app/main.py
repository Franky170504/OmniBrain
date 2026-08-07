from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.agents.graph import OmniBrainGraph
from app.core.app_config import app_settings
from app.core.database import check_database_connection, close_database
from app.routes import chat, health, history, upload
from app.services.chat_service import ChatService
from app.services.document_service import DocumentService
from app.services.qdrant_service import QdrantService
from app.services.rag_service import RagService


@asynccontextmanager
async def lifespan(app: FastAPI):
    await check_database_connection()

    qdrant_service = QdrantService()
    rag_service = RagService(qdrant_service)
    document_service = DocumentService(qdrant_service)
    agent_graph = OmniBrainGraph(rag_service)
    chat_service = ChatService(agent_graph)

    app.state.qdrant_service = qdrant_service
    app.state.rag_service = rag_service
    app.state.document_service = document_service
    app.state.agent_graph = agent_graph
    app.state.chat_service = chat_service

    yield

    await close_database()


app = FastAPI(
    title=app_settings.PROJECT_NAME,
    version="0.2.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=app_settings.CORS_ORIGINS or [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(upload.router)
app.include_router(chat.router)
app.include_router(history.router)