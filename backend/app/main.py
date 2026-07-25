from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import (
    HTTPException as StarletteHTTPException,
)

from backend.app.core.app_config import settings
from backend.app.routes import chat, health, upload
from backend.app.services.chat_service import ChatService
from backend.app.services.document_service import DocumentService
from backend.app.services.rag_service import RagService
from backend.app.services.qdrant_service import QdrantService


logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s - %(name)s - "
        "%(levelname)s - %(message)s"
    ),
)

logger = logging.getLogger("omnibrain")


tags_metadata = [
    {
        "name": "Health Check",
        "description": (
            "System health and Qdrant status endpoints."
        ),
    },
    {
        "name": "Document Management",
        "description": (
            "Document upload, parsing, and indexing endpoints."
        ),
    },
    {
        "name": "Document Chat",
        "description": (
            "Question answering over indexed documents."
        ),
    },
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting OmniBrain services")

    qdrant_service = QdrantService()
    qdrant_service.connect()
    qdrant_service.ensure_collection()

    document_service = DocumentService(
        qdrant_service=qdrant_service
    )

    rag_service = RagService(
        qdrant_service=qdrant_service
    )

    chat_service = ChatService(
        rag_service=rag_service
    )

    app.state.qdrant_service = qdrant_service
    app.state.document_service = document_service
    app.state.rag_service = rag_service
    app.state.chat_service = chat_service

    logger.info("OmniBrain services initialized")

    try:
        yield
    finally:
        logger.info("Stopping OmniBrain services")
        qdrant_service.close()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    openapi_tags=tags_metadata,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException,
):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    messages: list[str] = []

    for error in exc.errors():
        location = " -> ".join(
            str(item)
            for item in error.get("loc", [])
        )

        message = error.get(
            "msg",
            "Invalid input",
        )

        messages.append(
            f"{location}: {message}"
        )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": (
                "Validation Error: "
                + "; ".join(messages)
            )
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(
    request: Request,
    exc: Exception,
):
    logger.error(
        "Unhandled exception: %s",
        exc,
        exc_info=True,
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": (
                "An internal server error occurred."
            )
        },
    )


app.include_router(health.router)
app.include_router(upload.router)
app.include_router(chat.router)


@app.get("/", include_in_schema=False)
async def root():
    return {
        "message": "Welcome to OmniBrain Backend API",
        "docs": "/docs",
        "health": "/health",
    }