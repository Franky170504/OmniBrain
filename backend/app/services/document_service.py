from __future__ import annotations

import asyncio
import hashlib
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.app_config import app_settings
from app.db.repositories import KnowledgeRepository, UserRepository
from app.services.qdrant_service import QdrantService
from app.pipeline.parsing_pipeline import parse_pdf


class DocumentService:
    def __init__(self, qdrant_service: QdrantService) -> None:
        self.qdrant_service = qdrant_service

    @staticmethod
    def _as_dict(value: Any) -> dict[str, Any]:
        if isinstance(value, dict):
            return dict(value)
        if hasattr(value, "model_dump"):
            return dict(value.model_dump())
        if hasattr(value, "__dict__"):
            return dict(vars(value))
        return {}

    async def process_upload(self, *, file: UploadFile, user_id: str, session: AsyncSession) -> dict[str, Any]:
        if not file.filename:
            raise ValueError("Uploaded file must have a filename.")
        if Path(file.filename).suffix.lower() != ".pdf":
            raise ValueError("Only PDF files are supported by this upload route.")

        content = await file.read()
        if not content:
            raise ValueError("Uploaded PDF is empty.")

        checksum = hashlib.sha256(content).hexdigest()
        users = UserRepository(session)
        knowledge = KnowledgeRepository(session)
        db_user_id = await users.resolve_user(user_id)

        duplicate = await knowledge.find_document_by_checksum(checksum)
        if duplicate is not None:
            document_id = UUID(str(duplicate["document_id"]))
            await knowledge.grant_document_access(
                document_id=document_id,
                user_id=db_user_id,
                access_level="OWNER",
            )
            await session.commit()
            return {
                "message": "Document already exists in PostgreSQL; access was reused.",
                "document_id": str(document_id),
                "filename": duplicate["original_filename"],
                "page_count": int(duplicate["page_count"] or 0),
                "chunk_count": int(duplicate["chunk_count"] or 0),
                "image_count": int(duplicate["image_count"] or 0),
                "indexed_points": int(duplicate["chunk_count"] or 0),
                "processing_status": duplicate["processing_status"],
            }

        collection_id = await knowledge.ensure_default_collection()
        document_id = uuid4()
        safe_filename = Path(file.filename).name
        stored_filename = f"{document_id}-{safe_filename}"
        saved_path = app_settings.OUTPUT_DIR / stored_filename
        saved_path.write_bytes(content)

        await knowledge.create_document(
            document_id=document_id,
            collection_id=collection_id,
            document_title=Path(safe_filename).stem[:255] or safe_filename,
            original_filename=safe_filename,
            file_size_bytes=len(content),
            checksum_sha256=checksum,
        )
        await knowledge.grant_document_access(
            document_id=document_id,
            user_id=db_user_id,
            access_level="OWNER",
        )
        await knowledge.update_document_status(document_id=document_id, status="PARSING")
        await session.commit()

        try:
            parsed = await asyncio.to_thread(
                parse_pdf,
                pdf_path=saved_path,
                output_path=app_settings.OUTPUT_DIR,
            )
            if not isinstance(parsed, tuple) or len(parsed) != 3:
                raise RuntimeError("parse_pdf must return (document, chunks, images).")
            raw_document, raw_chunks, raw_images = parsed
            document = self._as_dict(raw_document)
            chunks = [self._as_dict(item) for item in raw_chunks]
            images = [self._as_dict(item) for item in raw_images]

            page_count = int(document.get("page_count") or 0)
            if page_count <= 0:
                page_numbers = [
                    int(item.get("page_number") or item.get("page_start") or item.get("page") or 1)
                    for item in chunks
                ]
                page_count = max(page_numbers, default=1)

            for item in chunks:
                item["document_id"] = str(document_id)
                item["user_id"] = user_id
                item["filename"] = safe_filename

            await knowledge.update_document_status(
                document_id=document_id,
                status="EMBEDDING",
                page_count=page_count,
                chunk_count=len(chunks),
                image_count=len(images),
            )
            await session.commit()

            indexed_chunks = await asyncio.to_thread(
                self.qdrant_service.ingest_chunks,
                chunks,
                user_id=user_id,
                document_id=str(document_id),
                original_filename=safe_filename,
            )

            await knowledge.replace_page_and_chunk_metadata(
                document_id=document_id,
                chunks=indexed_chunks,
                page_count=page_count,
                embedding_model=app_settings.EMBEDDING_MODEL,
                embedding_dimension=app_settings.EMBEDDING_DIMENSION,
            )
            await knowledge.update_document_status(
                document_id=document_id,
                status="INDEXED",
                page_count=page_count,
                chunk_count=len(indexed_chunks),
                image_count=len(images),
            )
            await session.commit()

            return {
                "message": "Document uploaded, indexed in Qdrant, and recorded in PostgreSQL.",
                "document_id": str(document_id),
                "filename": safe_filename,
                "page_count": page_count,
                "chunk_count": len(indexed_chunks),
                "image_count": len(images),
                "indexed_points": len(indexed_chunks),
                "processing_status": "INDEXED",
            }
        except Exception as exc:
            await session.rollback()
            await knowledge.update_document_status(
                document_id=document_id,
                status="FAILED",
                error=str(exc),
            )
            await session.commit()
            raise
