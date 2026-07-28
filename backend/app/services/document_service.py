import uuid
from pathlib import Path
from typing import Any
from fastapi import UploadFile, HTTPException, status
from backend.app.core.app_config import app_settings
from backend.app.pipeline.parsing_pipeline import parse_pdf
from backend.app.services.qdrant_service import QdrantService

class DocumentService:
    def __init__(
        self,
        qdrant_service: QdrantService,
    ) -> None:
        self.qdrant_service = qdrant_service

        app_settings.INPUT_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        app_settings.OUTPUT_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

    @staticmethod
    def validate_filename(filename: str | None) -> str:
        clean_name = Path(filename or "").name

        if not clean_name:
            raise ValueError(
                "The uploaded file has no filename."
            )

        if Path(clean_name).suffix.lower() != ".pdf":
            raise ValueError(
                "Only PDF files are supported."
            )

        return clean_name

    async def save_upload(
        self,
        file: UploadFile,
    ) -> tuple[Path, str]:
        original_filename = self.validate_filename(
            file.filename
        )

        stored_filename = (
            f"{uuid.uuid4().hex}-{original_filename}"
        )

        saved_path = (
            app_settings.OUTPUT_DIR
            / stored_filename
        )

        max_bytes = app_settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        bytes_written = 0

        try:
            with saved_path.open("wb") as output_file:
                while chunk := await file.read(1024 * 1024):
                    bytes_written += len(chunk)

                    if bytes_written > max_bytes:
                        raise ValueError(
                            "Uploaded file exceeds the maximum "
                            f"size of {app_settings.MAX_UPLOAD_SIZE_MB} MB."
                        )

                    output_file.write(chunk)

        except Exception:
            saved_path.unlink(missing_ok=True)
            raise

        finally:
            await file.close()

        return saved_path, original_filename

    async def process_upload(
        self,
        *,
        file: UploadFile,
        user_id: str,
    ) -> dict[str, Any]:
        saved_path, original_filename = (
            await self.save_upload(file)
        )

        try:
            document, chunks, images = parse_pdf(
                pdf_path=saved_path,
                output_path=app_settings.OUTPUT_DIR,
                chunk_size=2_000,
                overlap=250,
            )

            indexed_points = (
                self.qdrant_service.ingest_chunks(
                    chunks,
                    user_id=user_id,
                    original_filename=original_filename,
                )
            )

            return {
                "message": "Document uploaded and indexed.",
                "document_id": document["document_id"],
                "filename": original_filename,
                "page_count": document["page_count"],
                "chunk_count": len(chunks),
                "image_count": len(images),
                "indexed_points": indexed_points,
            }

        except Exception:
            saved_path.unlink(missing_ok=True)
            raise