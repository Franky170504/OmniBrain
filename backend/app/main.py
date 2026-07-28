from __future__ import annotations

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.agents.graph import OmniBrainGraph
from config.settings import settings
from app.core.app_config import app_settings
from app.core.langsmith_config import configure_langsmith
from app.routes import chat, health, upload
from app.services.chat_service import ChatService
from app.services.document_service import DocumentService
from app.services.qdrant_service import QdrantService
from app.services.rag_service import RagService
from pathlib import Path
import os
from dotenv import load_dotenv
load_dotenv(Path(".env"))


cors_origins = app_settings.CORS_ORIGINS or [
    "http://localhost:8501",
    "http://127.0.0.1:8501",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_langsmith()

    qdrant_service = QdrantService()
    qdrant_service.connect()
    qdrant_service.ensure_collection()

    document_service = DocumentService(
        qdrant_service=qdrant_service,
    )

    rag_service = RagService(
        qdrant_service=qdrant_service,
    )

    agent_graph = OmniBrainGraph(
        rag_service=rag_service,
    )

    chat_service = ChatService(
        agent_graph=agent_graph,
    )

    app.state.qdrant_service = qdrant_service
    app.state.document_service = document_service
    app.state.rag_service = rag_service
    app.state.agent_graph = agent_graph
    app.state.chat_service = chat_service
    

    yield

    qdrant_service.close()


app = FastAPI(
    title="OmniBrain API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(upload.router)
app.include_router(chat.router)