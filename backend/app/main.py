from __future__ import annotations

from pathlib import Path
from contextlib import asynccontextmanager

from dotenv import load_dotenv
load_dotenv(Path(".env"))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.agents.graph import OmniBrainGraph
from app.core.app_config import app_settings
from app.core.langsmith_config import configure_langsmith
from app.database.schema_loader import load_database_schema
from app.routes import auth, chat, health, upload
from app.services.chat_service import ChatService
from app.services.auth_service import AuthService
from app.services.document_service import DocumentService
from app.database.database_service import DatabaseService
from app.services.qdrant_service import QdrantService
from app.services.rag_service import RagService
from app.services.query_engine_service import QueryEngineService
from app.storage.bucket_manager import BucketManager
from app.storage.minio_service import MinioService

cors_origins = app_settings.CORS_ORIGINS or [
    "http://127.0.0.1:8501",
    "http://127.0.0.1:8000",
]

@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_langsmith()

    database_service = DatabaseService()
    database_service.connect()

    if app_settings.database_auto_init:
        load_database_schema()

    qdrant_service = QdrantService()
    qdrant_service.connect()
    qdrant_service.ensure_collection()

    minio_service = MinioService(
        endpoint=app_settings.MINIO_ENDPOINT,
        access_key=app_settings.MINIO_ACCESS_KEY,
        secret_key=app_settings.MINIO_SECRET_KEY,
        secure=app_settings.MINIO_SECURE,
    )
    minio_service.connect()

    bucket_manager = BucketManager(minio_service=minio_service)
    bucket_manager.ensure_bucket(app_settings.MINIO_BUCKET)

    document_service = DocumentService(
        qdrant_service=qdrant_service,
        database_service=database_service,
        minio_service=minio_service,
    )
    auth_service = AuthService(database_service=database_service)
    rag_service = RagService(qdrant_service=qdrant_service)
    agent_graph = OmniBrainGraph(rag_service=rag_service)
    query_engine_service = QueryEngineService(database_service=database_service)
    chat_service = ChatService(
        agent_graph=agent_graph,
        query_engine_service=query_engine_service,
    )

    app.state.database_service = database_service
    app.state.qdrant_service = qdrant_service
    app.state.document_service = document_service
    app.state.auth_service = auth_service
    app.state.rag_service = rag_service
    app.state.agent_graph = agent_graph
    app.state.query_engine_service = query_engine_service
    app.state.chat_service = chat_service
    
    yield

    database_service.close()
    qdrant_service.close()

app = FastAPI(
    title="OmniBrain API",
    version="1.0.0",
    lifespan=lifespan,
)

@app.get("/", tags=["Root"])
def root() -> dict:
    return {
        "status": "ok",
        "message": "OmniBrain API is running",
    }

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(upload.router)
app.include_router(chat.router)