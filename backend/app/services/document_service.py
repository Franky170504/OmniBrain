import hashlib
import logging
import uuid

from pathlib import Path
from typing import Any
from fastapi import UploadFile
from sqlalchemy import select

from app.core.app_config import app_settings
from app.database.database_service import DatabaseService
from app.database.models.authentication.role import Role
from app.database.models.authentication.user import User
from app.database.models.knowledge.chunk import Chunk
from app.database.models.knowledge.collection import Collection
from app.database.models.knowledge.domain import Domain
from app.database.models.knowledge.document import Document
from app.database.models.knowledge.page import Page
from app.database.repositories.knowledge.document_repository import DocumentRepository
from app.pipeline.parsing_pipeline import parse_pdf
from app.services.qdrant_service import QdrantService
from app.storage.minio_service import MinioService

logger = logging.getLogger(__name__)


class DocumentAuthorizationError(PermissionError):
    pass


class DocumentService:
    def __init__(
        self,
        qdrant_service: QdrantService,
        document_repository: DocumentRepository | None = None,
        database_service: DatabaseService | None = None,
        minio_service: MinioService | None = None,
    ) -> None:
        self.qdrant_service = qdrant_service
        self.document_repository = document_repository
        self.database_service = database_service or DatabaseService()
        self.minio_service = minio_service
        app_settings.INPUT_DIR.mkdir(parents=True, exist_ok=True)
        app_settings.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def validate_filename(filename: str | None) -> str:
        clean_name = Path(filename or "").name

        if not clean_name:
            raise ValueError("The uploaded file has no filename.")

        if Path(clean_name).suffix.lower() != ".pdf":
            raise ValueError("Only PDF files are supported.")
        return clean_name

    async def save_upload(self, file: UploadFile) -> tuple[Path, str]:
        original_filename = self.validate_filename(file.filename)
        stored_filename = (f"{uuid.uuid4().hex}-{original_filename}")
        saved_path = (app_settings.OUTPUT_DIR / stored_filename)
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

    def _build_document_record(
        self,
        *,
        parsed_document: dict[str, Any],
        saved_path: Path,
        original_filename: str,
        bucket_name: str,
        object_path: str,
        user_id: str,
        collection_id: uuid.UUID,
    ) -> dict[str, Any]:
        metadata = parsed_document.get("metadata") or {}
        document_title = metadata.get("title") or original_filename
        return {
            "document_id": parsed_document.get("document_id"),
            "document_title": document_title,
            "original_filename": original_filename,
            "bucket_name": bucket_name,
            "object_path": object_path,
            "processing_status": "UPLOADED",
            "page_count": parsed_document.get("page_count", 0),
            "chunk_count": parsed_document.get("chunk_count", 0),
            "image_count": parsed_document.get("image_occurrence_count", 0),
            "file_size_bytes": saved_path.stat().st_size if saved_path.exists() else 0,
            "checksum_sha256": parsed_document.get("sha256", ""),
            "mime_type": "application/pdf",
            "file_extension": self._normalize_file_extension(original_filename),
            "document_type": "PDF",
            "language_code": metadata.get("language") or None,
            "document_description": metadata.get("subject") or None,
            "owner_user_id": self._resolve_user_id(user_id),
            "collection_id": collection_id,
            "created_by": user_id,
        }

    @staticmethod
    def _resolve_user_id(user_id: str) -> uuid.UUID:
        try:
            return uuid.UUID(user_id)
        except (ValueError, AttributeError):
            return uuid.uuid5(uuid.NAMESPACE_URL, user_id)

    def _ensure_owner_user(self, session, user_id: uuid.UUID) -> None:
        if session.get(User, user_id) is not None:
            return

        role_id = session.execute(
            select(Role.role_id).where(Role.role_name == "Viewer")
        ).scalar_one_or_none()
        if role_id is None:
            role_id = session.execute(
                select(Role.role_id).where(Role.role_name == "Admin")
            ).scalar_one_or_none()
        if role_id is None:
            raise RuntimeError("No usable auth role exists for document owner.")

        session.add(
            User(
                user_id=user_id,
                role_id=role_id,
                email=f"{user_id}@local.omnibrain",
                full_name="OmniBrain Local User",
                is_active=True,
            )
        )
        session.flush()

    def _ensure_default_collection(self) -> uuid.UUID:
        with self.database_service.transaction() as session:
            domain = session.query(Domain).filter_by(slug="default").one_or_none()
            if domain is None:
                domain = Domain(
                    domain_name="Default",
                    description="Default knowledge domain.",
                    slug="default",
                )
                session.add(domain)
                session.flush()

            collection = session.query(Collection).filter_by(slug="default").one_or_none()
            if collection is None:
                collection = Collection(
                    domain_id=domain.domain_id,
                    collection_name="Default Collection",
                    description="Default collection for uploaded documents.",
                    slug="default",
                )
                session.add(collection)
                session.flush()

            return collection.collection_id

    def _transition_processing_status(self, *, document_id: str | None, status: str, error: str | None = None) -> None:
        if document_id is None:
            return

        repository = self.document_repository
        if repository is None:
            with self.database_service.transaction() as session:
                repository = DocumentRepository(session)
                document = repository.get_by_id(document_id)
                if document is None:
                    return
                self._update_status(document, status=status, error=error, repository=repository)
                return

        document = repository.get_by_id(document_id)
        if document is None:
            return
        self._update_status(document, status=status, error=error, repository=repository)

    def _update_status(self, document: Document, status: str, error: str | None, repository: DocumentRepository) -> None:
        current_status = document.processing_status or "UPLOADED"
        if status == "FAILED":
            document.processing_status = "FAILED"
            document.processing_error = error
            repository.update(document)
            return

        allowed_next_states = {
            "UPLOADED": ("PARSING",),
            "PARSING": ("CHUNKING",),
            "CHUNKING": ("EMBEDDING",),
            "EMBEDDING": ("INDEXED",),
            "INDEXED": (),
            "FAILED": (),
        }

        if current_status == "FAILED":
            return

        if current_status == "UPLOADED" and status == "CHUNKING":
            document.processing_status = status
            document.processing_error = None
            repository.update(document)
            return

        if status not in allowed_next_states.get(current_status, ()):
            raise RuntimeError(
                f"Invalid processing state transition from {current_status} to {status}."
            )

        document.processing_status = status
        document.processing_error = None
        repository.update(document)

    @staticmethod
    def _normalize_file_extension(filename: str) -> str:
        extension = Path(filename).suffix.lower().lstrip('.')
        if not extension:
            raise ValueError(
                f"Invalid filename '{filename}': unable to determine file extension."
            )
        return extension

    def _mark_processing_status(self, *, document_id: str | None, status: str, error: str | None = None) -> None:
        self._transition_processing_status(document_id=document_id, status=status, error=error)

    def _verify_document_ready_for_index(self, *, document_id: str | None, expected_chunk_count: int, user_id: str) -> bool:
        if document_id is None:
            return False

        repository = self.document_repository
        if repository is None:
            with self.database_service.transaction() as session:
                repository = DocumentRepository(session)
                return self._verify_document_ready(
                    repository=repository,
                    document_id=document_id,
                    expected_chunk_count=expected_chunk_count,
                    user_id=user_id,
                )

        return self._verify_document_ready(
            repository=repository,
            document_id=document_id,
            expected_chunk_count=expected_chunk_count,
            user_id=user_id,
        )

    def _verify_document_ready(
        self,
        *,
        repository: DocumentRepository,
        document_id: str,
        expected_chunk_count: int,
        user_id: str,
    ) -> bool:
        document = repository.get_by_id(document_id)
        if document is None or self.minio_service is None:
            return False

        if not self.minio_service.object_exists(document.bucket_name, document.object_path):
            return False

        if expected_chunk_count <= 0 or document.chunk_count != expected_chunk_count:
            return False

        if self.qdrant_service is None:
            return False

        return self.qdrant_service.verify_document_index(
            user_id=user_id,
            document_id=document_id,
            expected_count=expected_chunk_count,
        )

    def delete_document(self, *, document_id: str, user_id: str) -> bool:
        with self.database_service.transaction() as session:
            repository = DocumentRepository(session)
            document = repository.get_by_id(document_id)
            owner_user_id = self._resolve_user_id(user_id)
            if document is None:
                return False
            if document.owner_user_id != owner_user_id:
                raise DocumentAuthorizationError("Document deletion is not authorized.")

            if self.qdrant_service is not None:
                self.qdrant_service.delete_document(
                    user_id=user_id,
                    document_id=document_id,
                )

            if self.minio_service is not None and self.minio_service.object_exists(
                document.bucket_name,
                document.object_path,
            ):
                self.minio_service.delete(
                    document.bucket_name,
                    document.object_path,
                )

            repository.delete(document)
            return True

    def assign_document_owner(
        self,
        *,
        document_id: str,
        owner_user_id: str,
        assigning_user_id: str,
        auth_service,
    ) -> bool:
        if not auth_service.is_admin(assigning_user_id):
            raise DocumentAuthorizationError("Administrator authorization is required.")

        requested_owner = self._resolve_user_id(owner_user_id)
        with self.database_service.transaction() as session:
            repository = DocumentRepository(session)
            document = repository.get_by_id(document_id)
            if document is None:
                return False

            target_user = session.get(User, requested_owner)
            if target_user is None or not target_user.is_active:
                raise ValueError("The requested owner does not exist or is inactive.")

            if document.owner_user_id is not None and document.owner_user_id != requested_owner:
                raise ValueError("An assigned document owner cannot be overwritten.")

            document.owner_user_id = requested_owner
            repository.update(document)
            logger.info(
                "Document ownership assigned: document_id=%s owner_user_id=%s assigned_by=%s",
                document_id,
                requested_owner,
                assigning_user_id,
            )
            return True

    def _persist_document_ingestion(self, *, record: dict[str, Any], chunks: list[Any], images: list[Any], saved_path: Path) -> tuple[bool, Document | None]:
        if self.minio_service is None:
            raise RuntimeError("MinIO service is required for document persistence.")

        bucket_name = record["bucket_name"]
        object_path = record["object_path"]
        uploaded = False

        try:
            with self.database_service.transaction() as session:
                repository = DocumentRepository(session)
                owner_user_id = record.get("owner_user_id")
                if owner_user_id is not None:
                    self._ensure_owner_user(session, owner_user_id)

                checksum = record.get("checksum_sha256")
                if checksum:
                    existing_document = repository.get_by_checksum(checksum)
                    if existing_document is not None and str(existing_document.document_id) != str(record.get("document_id")):
                        return False, existing_document

                with saved_path.open("rb") as source_file:
                    self.minio_service.upload(bucket_name, object_path, source_file)
                    uploaded = True

                document = repository.create_document_from_record(record)

                page = Page(
                    document_id=document.document_id,
                    page_number=1,
                    page_label=None,
                    page_type='DOCUMENT',
                    ocr_applied=False,
                    character_count=len(chunks[0].text) if chunks else 0,
                    word_count=len(chunks[0].text.split()) if chunks else 0,
                    chunk_count=len(chunks),
                    image_count=len(images),
                    table_count=0,
                    is_active=True,
                )
                session.add(page)
                session.flush()

                for chunk in chunks:
                    session.add(
                        Chunk(
                            chunk_id=chunk.chunk_id,
                            page_id=page.page_id,
                            chunk_index=chunk.chunk_index,
                            chunk_text=chunk.text,
                            chunk_type='TEXT',
                            character_start=0,
                            character_end=len(chunk.text),
                            token_count=len(chunk.text.split()),
                            content_checksum=hashlib.sha256(chunk.text.encode('utf-8')).hexdigest(),
                            chunk_status='CREATED',
                            is_active=True,
                        )
                    )

                session.flush()
                return True, document
        except Exception:
            if uploaded and self.minio_service is not None:
                try:
                    self.minio_service.delete(bucket_name, object_path)
                except Exception as cleanup_error:
                    logger.exception(
                        "Failed to clean up MinIO object %s/%s after transaction failure",
                        bucket_name,
                        object_path,
                        exc_info=cleanup_error,
                    )
            raise

    async def process_upload(self, *, file: UploadFile, user_id: str) -> dict[str, Any]:
        saved_path, original_filename = (await self.save_upload(file))
        document_id: str | None = None
        try:
            document, chunks, images = parse_pdf(
                pdf_path=saved_path,
                output_path=app_settings.OUTPUT_DIR,
                chunk_size=2_000,
                overlap=250,
            )
            collection_id = self._ensure_default_collection()
            record = self._build_document_record(
                parsed_document=document,
                saved_path=saved_path,
                original_filename=original_filename,
                bucket_name=app_settings.MINIO_BUCKET,
                object_path=f"uploads/{document['document_id']}/{original_filename}",
                user_id=user_id,
                collection_id=collection_id,
            )
            document_id = str(record["document_id"]) if record.get("document_id") is not None else None
            created_new, persisted_document = self._persist_document_ingestion(
                record=record,
                chunks=chunks,
                images=images,
                saved_path=saved_path,
            )
            self._mark_processing_status(
                document_id=document_id,
                status="PARSING",
            )
            self._mark_processing_status(
                document_id=document_id,
                status="CHUNKING",
            )
            indexed_points = 0
            if created_new and self.qdrant_service is not None:
                self._mark_processing_status(
                    document_id=document_id,
                    status="EMBEDDING",
                )
                try:
                    indexed_points = (
                        self.qdrant_service.ingest_chunks(
                            chunks,
                            user_id=user_id,
                            original_filename=original_filename,
                        )
                    )
                except Exception as exc:
                    self._mark_processing_status(
                        document_id=document_id,
                        status="FAILED",
                        error=str(exc),
                    )
                    raise

                if not self._verify_document_ready_for_index(
                    document_id=document_id,
                    expected_chunk_count=len(chunks),
                    user_id=user_id,
                ):
                    raise RuntimeError(
                        "Qdrant verification failed before document could be marked INDEXED. "
                        f"document_id={document_id}, expected_count={len(chunks)}, actual_count={indexed_points}."
                    )
            self._mark_processing_status(
                document_id=document_id,
                status="INDEXED",
            )
            document_id = (
                str(persisted_document.document_id)
                if persisted_document is not None
                else document["document_id"]
            )
            return {
                "message": "Document uploaded and indexed.",
                "document_id": document_id,
                "filename": original_filename,
                "page_count": document["page_count"],
                "chunk_count": len(chunks),
                "image_count": len(images),
                "indexed_points": indexed_points,
            }
        except Exception as exc:
            self._mark_processing_status(
                document_id=document_id,
                status="FAILED",
                error=str(exc),
            )
            saved_path.unlink(missing_ok=True)
            raise
