from __future__ import annotations

import hashlib
import io
import json
import logging
import mimetypes
import uuid

from pathlib import Path
from typing import Any

from fastapi import UploadFile
from sqlalchemy import select, text

from app.core.app_config import app_settings

from app.database.database_service import (
    DatabaseService,
)

from app.database.models.authentication.role import (
    Role,
)

from app.database.models.authentication.user import (
    User,
)

from app.database.models.knowledge.chunk import (
    Chunk,
)

from app.database.models.knowledge.collection import (
    Collection,
)

from app.database.models.knowledge.domain import (
    Domain,
)

from app.database.models.knowledge.document import (
    Document,
)

from app.database.models.knowledge.page import (
    Page,
)

from app.database.repositories.knowledge.document_repository import (
    DocumentRepository,
)

from app.pipeline.parsing_pipeline import (
    ParsedChunk,
    ParsedDocumentResult,
    ParsedImage,
    ParsedPage,
    ParsedTable,
    SUPPORTED_EXTENSIONS,
    detect_document_type,
    detect_mime_type,
    parse_document,
)

from app.services.qdrant_service import (
    QdrantService,
)

from app.storage.minio_service import (
    MinioService,
)


logger = logging.getLogger(
    __name__
)


class DocumentAuthorizationError(
    PermissionError
):
    pass


class DocumentService:
    def __init__(
        self,
        qdrant_service: QdrantService,
        document_repository: (
            DocumentRepository | None
        ) = None,
        database_service: (
            DatabaseService | None
        ) = None,
        minio_service: (
            MinioService | None
        ) = None,
    ) -> None:
        self.qdrant_service = (
            qdrant_service
        )

        self.document_repository = (
            document_repository
        )

        self.database_service = (
            database_service
            or DatabaseService()
        )

        self.minio_service = (
            minio_service
        )

        app_settings.INPUT_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        app_settings.OUTPUT_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

    # ========================================================
    # File validation
    # ========================================================

    @staticmethod
    def _normalize_page_label(
        label: str | None,
    ) -> str | None:
        """
        Final PostgreSQL safety guard.

        knowledge.pages.page_label is VARCHAR(50).
        """

        if label is None:
            return None

        clean_label = str(
            label
        ).strip()

        if not clean_label:
            return None

        if len(clean_label) <= 50:
            return clean_label

        path = Path(
            clean_label
        )

        suffix = (
            path.suffix
        )

        stem = (
            path.stem
        )

        if suffix:
            reserved = (
                len(suffix)
                + 3
            )

            available = (
                50 - reserved
            )

            if available > 0:
                return (
                    stem[:available]
                    + "..."
                    + suffix
                )

        return (
            clean_label[:47]
            + "..."
        )

    @staticmethod
    def validate_filename(
        filename: str | None,
    ) -> str:
        clean_name = Path(
            filename or ""
        ).name

        if not clean_name:
            raise ValueError(
                "The uploaded file has no filename."
            )

        extension = (
            Path(clean_name)
            .suffix
            .lower()
        )

        # Unknown formats are allowed and will
        # use the OTHER/fallback parser.
        if not extension:
            raise ValueError(
                "The uploaded file must have "
                "a file extension."
            )

        return clean_name

    # ========================================================
    # Upload temporary file
    # ========================================================

    async def save_upload(
        self,
        file: UploadFile,
    ) -> tuple[
        Path,
        str,
    ]:
        original_filename = (
            self.validate_filename(
                file.filename
            )
        )

        stored_filename = (
            f"{uuid.uuid4().hex}-"
            f"{original_filename}"
        )

        saved_path = (
            app_settings.OUTPUT_DIR
            / stored_filename
        )

        max_bytes = (
            app_settings.MAX_UPLOAD_SIZE_MB
            * 1024
            * 1024
        )

        bytes_written = 0

        try:
            with saved_path.open(
                "wb"
            ) as output_file:
                while True:
                    chunk = await file.read(
                        1024 * 1024
                    )

                    if not chunk:
                        break

                    bytes_written += len(
                        chunk
                    )

                    if (
                        bytes_written
                        > max_bytes
                    ):
                        raise ValueError(
                            "Uploaded file exceeds "
                            "the maximum size of "
                            f"{app_settings.MAX_UPLOAD_SIZE_MB} "
                            "MB."
                        )

                    output_file.write(
                        chunk
                    )

        except Exception:
            saved_path.unlink(
                missing_ok=True
            )

            raise

        finally:
            await file.close()

        if bytes_written == 0:
            saved_path.unlink(
                missing_ok=True
            )

            raise ValueError(
                "The uploaded file is empty."
            )

        return (
            saved_path,
            original_filename,
        )

    # ========================================================
    # DB document record
    # ========================================================

    def _build_document_record(
        self,
        *,
        parsed_document: dict[
            str,
            Any,
        ],
        saved_path: Path,
        original_filename: str,
        bucket_name: str,
        object_path: str,
        user_id: str,
        collection_id: uuid.UUID,
    ) -> dict[str, Any]:
        metadata = (
            parsed_document.get(
                "metadata"
            )
            or {}
        )

        document_title = (
            metadata.get("title")
            or original_filename
        )

        mime_type = (
            parsed_document.get(
                "mime_type"
            )
            or detect_mime_type(
                saved_path
            )
        )

        document_type = (
            parsed_document.get(
                "document_type"
            )
            or detect_document_type(
                saved_path
            )
        )

        return {
            "document_id": (
                parsed_document.get(
                    "document_id"
                )
            ),
            "document_title": (
                document_title
            ),
            "original_filename": (
                original_filename
            ),
            "bucket_name": (
                bucket_name
            ),
            "object_path": (
                object_path
            ),
            "processing_status": (
                "UPLOADED"
            ),
            "page_count": int(
                parsed_document.get(
                    "page_count",
                    0,
                )
            ),
            "chunk_count": int(
                parsed_document.get(
                    "chunk_count",
                    0,
                )
            ),
            "image_count": int(
                parsed_document.get(
                    "image_occurrence_count",
                    0,
                )
            ),
            "table_count": int(
                parsed_document.get(
                    "table_count",
                    0,
                )
            ),
            "file_size_bytes": (
                saved_path.stat().st_size
                if saved_path.exists()
                else 0
            ),
            "checksum_sha256": (
                parsed_document.get(
                    "sha256",
                    "",
                )
            ),
            "mime_type": mime_type,
            "file_extension": (
                self._normalize_file_extension(
                    original_filename
                )
            ),
            "document_type": (
                document_type
            ),
            "language_code": (
                metadata.get(
                    "language"
                )
                or None
            ),
            "document_description": (
                metadata.get(
                    "subject"
                )
                or None
            ),
            "owner_user_id": (
                self._resolve_user_id(
                    user_id
                )
            ),
            "collection_id": (
                collection_id
            ),
            "created_by": user_id,
        }

    # ========================================================
    # User helpers
    # ========================================================

    @staticmethod
    def _resolve_user_id(
        user_id: str,
    ) -> uuid.UUID:
        try:
            return uuid.UUID(
                user_id
            )

        except (
            ValueError,
            AttributeError,
        ):
            return uuid.uuid5(
                uuid.NAMESPACE_URL,
                user_id,
            )

    def _ensure_owner_user(
        self,
        session,
        user_id: uuid.UUID,
    ) -> None:
        if (
            session.get(
                User,
                user_id,
            )
            is not None
        ):
            return

        role_id = session.execute(
            select(
                Role.role_id
            ).where(
                Role.role_name
                == "Viewer"
            )
        ).scalar_one_or_none()

        if role_id is None:
            role_id = session.execute(
                select(
                    Role.role_id
                ).where(
                    Role.role_name
                    == "Admin"
                )
            ).scalar_one_or_none()

        if role_id is None:
            raise RuntimeError(
                "No usable auth role exists "
                "for document owner."
            )

        session.add(
            User(
                user_id=user_id,
                role_id=role_id,
                email=(
                    f"{user_id}"
                    "@local.omnibrain"
                ),
                full_name=(
                    "OmniBrain Local User"
                ),
                is_active=True,
            )
        )

        session.flush()

    # ========================================================
    # Default collection
    # ========================================================

    def _ensure_default_collection(
        self,
    ) -> uuid.UUID:
        with (
            self.database_service
            .transaction()
            as session
        ):
            domain = (
                session
                .query(Domain)
                .filter_by(
                    slug="default"
                )
                .one_or_none()
            )

            if domain is None:
                domain = Domain(
                    domain_name="Default",
                    description=(
                        "Default knowledge "
                        "domain."
                    ),
                    slug="default",
                )

                session.add(
                    domain
                )

                session.flush()

            collection = (
                session
                .query(Collection)
                .filter_by(
                    slug="default"
                )
                .one_or_none()
            )

            if collection is None:
                collection = Collection(
                    domain_id=(
                        domain.domain_id
                    ),
                    collection_name=(
                        "Default Collection"
                    ),
                    description=(
                        "Default collection "
                        "for uploaded documents."
                    ),
                    slug="default",
                )

                session.add(
                    collection
                )

                session.flush()

            return (
                collection
                .collection_id
            )

    # ========================================================
    # Status management
    # ========================================================

    def _transition_processing_status(
        self,
        *,
        document_id: str | None,
        status: str,
        error: str | None = None,
    ) -> None:
        if document_id is None:
            return

        repository = (
            self.document_repository
        )

        if repository is None:
            with (
                self.database_service
                .transaction()
                as session
            ):
                repository = (
                    DocumentRepository(
                        session
                    )
                )

                document = (
                    repository.get_by_id(
                        document_id
                    )
                )

                if document is None:
                    return

                self._update_status(
                    document,
                    status=status,
                    error=error,
                    repository=(
                        repository
                    ),
                )

                return

        document = (
            repository.get_by_id(
                document_id
            )
        )

        if document is None:
            return

        self._update_status(
            document,
            status=status,
            error=error,
            repository=repository,
        )

    @staticmethod
    def _update_status(
        document: Document,
        status: str,
        error: str | None,
        repository: (
            DocumentRepository
        ),
    ) -> None:
        current_status = (
            document.processing_status
            or "UPLOADED"
        )

        if status == "FAILED":
            document.processing_status = (
                "FAILED"
            )

            document.processing_error = (
                error
            )

            repository.update(
                document
            )

            return

        allowed_next_states = {
            "UPLOADED": (
                "PARSING",
            ),
            "PARSING": (
                "CHUNKING",
            ),
            "CHUNKING": (
                "EMBEDDING",
            ),
            "EMBEDDING": (
                "INDEXED",
            ),
            "INDEXED": (),
            "FAILED": (),
        }

        if current_status == "FAILED":
            return

        if (
            current_status
            == "UPLOADED"
            and status == "CHUNKING"
        ):
            document.processing_status = (
                status
            )

            document.processing_error = (
                None
            )

            repository.update(
                document
            )

            return

        if (
            status
            not in allowed_next_states.get(
                current_status,
                (),
            )
        ):
            raise RuntimeError(
                "Invalid processing state "
                f"transition from "
                f"{current_status} "
                f"to {status}."
            )

        document.processing_status = (
            status
        )

        document.processing_error = (
            None
        )

        repository.update(
            document
        )

    @staticmethod
    def _normalize_file_extension(
        filename: str,
    ) -> str:
        extension = (
            Path(filename)
            .suffix
            .lower()
            .lstrip(".")
        )

        if not extension:
            return "bin"

        return extension[:20]

    def _mark_processing_status(
        self,
        *,
        document_id: str | None,
        status: str,
        error: str | None = None,
    ) -> None:
        self._transition_processing_status(
            document_id=document_id,
            status=status,
            error=error,
        )

    # ========================================================
    # MinIO helpers
    # ========================================================

    def _upload_file_to_minio(
        self,
        *,
        bucket_name: str,
        object_path: str,
        path: Path,
    ) -> None:
        if self.minio_service is None:
            raise RuntimeError(
                "MinIO service is required "
                "for document persistence."
            )

        with path.open(
            "rb"
        ) as source:
            self.minio_service.upload(
                bucket_name,
                object_path,
                source,
            )

    def _upload_bytes_to_minio(
        self,
        *,
        bucket_name: str,
        object_path: str,
        data: bytes,
    ) -> None:
        if self.minio_service is None:
            raise RuntimeError(
                "MinIO service is required "
                "for document persistence."
            )

        source = io.BytesIO(
            data
        )

        self.minio_service.upload(
            bucket_name,
            object_path,
            source,
        )

    # ========================================================
    # Page persistence
    # ========================================================

    def _persist_pages(
        self,
        *,
        session,
        document: Document,
        pages: list[ParsedPage],
        chunks: list[ParsedChunk],
        images: list[ParsedImage],
        tables: list[ParsedTable],
    ) -> dict[
        int,
        Page,
    ]:
        page_map: dict[
            int,
            Page,
        ] = {}

        # Guarantee at least one logical page.
        if not pages:
            pages = [
                ParsedPage(
                    page_number=1,
                    page_type=(
                        "DOCUMENT"
                    ),
                    text="",
                )
            ]

        for parsed_page in pages:
            page_number = int(
                parsed_page.page_number
            )

            page_chunks = [
                chunk
                for chunk in chunks
                if (
                    int(
                        chunk.page_start
                    )
                    <= page_number
                    <= int(
                        chunk.page_end
                    )
                )
            ]

            page_images = [
                image
                for image in images
                if int(
                    image.page_number
                )
                == page_number
            ]

            page_tables = [
                table
                for table in tables
                if int(
                    table.page_number
                )
                == page_number
            ]

            page_text = (
                parsed_page.text
                or ""
            )

            page_type = (
                parsed_page.page_type
                or "DOCUMENT"
            )

            allowed_page_types = {
                "DOCUMENT",
                "SLIDE",
                "IMAGE",
                "HTML",
                "MARKDOWN",
                "OCR",
            }

            if (
                page_type
                not in allowed_page_types
            ):
                page_type = "DOCUMENT"

            page = Page(
                document_id=(
                    document.document_id
                ),
                page_number=(
                    page_number
                ),
                page_label=(
                    parsed_page.label
                ),
                page_type=page_type,
                ocr_applied=bool(
                    parsed_page.ocr_applied
                ),
                character_count=len(
                    page_text
                ),
                word_count=len(
                    page_text.split()
                ),
                chunk_count=len(
                    page_chunks
                ),
                image_count=len(
                    page_images
                ),
                table_count=len(
                    page_tables
                ),
                is_active=True,
            )

            session.add(
                page
            )

            session.flush()

            page_map[
                page_number
            ] = page

        return page_map

    # ========================================================
    # Chunk persistence
    # ========================================================

    @staticmethod
    def _persist_chunks(
        *,
        session,
        chunks: list[
            ParsedChunk
        ],
        page_map: dict[
            int,
            Page,
        ],
    ) -> None:
        page_chunk_indexes: dict[
            int,
            int,
        ] = {}

        for chunk in chunks:
            page_number = int(
                chunk.page_start
            )

            page = page_map.get(
                page_number
            )

            if page is None:
                logger.warning(
                    "Skipping chunk because "
                    "page %s does not exist.",
                    page_number,
                )

                continue

            page_chunk_indexes[
                page_number
            ] = (
                page_chunk_indexes.get(
                    page_number,
                    0,
                )
                + 1
            )

            local_index = (
                page_chunk_indexes[
                    page_number
                ]
            )

            try:
                chunk_uuid = uuid.UUID(
                    str(
                        chunk.chunk_id
                    )
                )

            except ValueError:
                chunk_uuid = uuid.uuid5(
                    uuid.NAMESPACE_URL,
                    str(
                        chunk.chunk_id
                    ),
                )

            session.add(
                Chunk(
                    chunk_id=chunk_uuid,
                    page_id=(
                        page.page_id
                    ),
                    chunk_index=(
                        local_index
                    ),
                    chunk_text=(
                        chunk.text
                    ),
                    chunk_type="TEXT",
                    character_start=0,
                    character_end=len(
                        chunk.text
                    ),
                    token_count=len(
                        chunk.text.split()
                    ),
                    content_checksum=(
                        hashlib.sha256(
                            chunk.text.encode(
                                "utf-8"
                            )
                        ).hexdigest()
                    ),
                    chunk_status=(
                        "CREATED"
                    ),
                    is_active=True,
                )
            )

        session.flush()

    # ========================================================
    # Image persistence
    # ========================================================

    def _persist_images(
        self,
        *,
        session,
        document_id: str,
        images: list[
            ParsedImage
        ],
        page_map: dict[
            int,
            Page,
        ],
        bucket_name: str,
    ) -> None:
        for image in images:
            page = page_map.get(
                int(
                    image.page_number
                )
            )

            if page is None:
                continue

            image_path = Path(
                image.path
            )

            if not image_path.exists():
                logger.warning(
                    "Extracted image does "
                    "not exist: %s",
                    image_path,
                )

                continue

            extension = (
                image.extension
                .lower()
                .lstrip(".")
                or "png"
            )

            mime_type = (
                mimetypes.guess_type(
                    image_path.name
                )[0]
                or (
                    f"image/{extension}"
                )
            )

            object_path = (
                "images/"
                f"{document_id}/"
                f"{image.image_id}."
                f"{extension}"
            )

            self._upload_file_to_minio(
                bucket_name=(
                    bucket_name
                ),
                object_path=(
                    object_path
                ),
                path=image_path,
            )

            image_index = max(
                int(
                    image.image_index
                ),
                1,
            )

            width = max(
                int(
                    image.width
                ),
                1,
            )

            height = max(
                int(
                    image.height
                ),
                1,
            )

            image_id = uuid.UUID(
                str(
                    image.image_id
                )
            )

            session.execute(
                text(
                    """
                    INSERT INTO knowledge.images
                    (
                        image_id,
                        page_id,
                        image_index,
                        original_filename,
                        image_format,
                        mime_type,
                        file_size_bytes,
                        bucket_name,
                        object_path,
                        width_px,
                        height_px,
                        bbox_x,
                        bbox_y,
                        bbox_width,
                        bbox_height,
                        caption,
                        alt_text,
                        ocr_text,
                        content_checksum,
                        image_status,
                        is_active
                    )
                    VALUES
                    (
                        :image_id,
                        :page_id,
                        :image_index,
                        :original_filename,
                        :image_format,
                        :mime_type,
                        :file_size_bytes,
                        :bucket_name,
                        :object_path,
                        :width_px,
                        :height_px,
                        :bbox_x,
                        :bbox_y,
                        :bbox_width,
                        :bbox_height,
                        :caption,
                        :alt_text,
                        :ocr_text,
                        :content_checksum,
                        'EXTRACTED',
                        TRUE
                    )
                    ON CONFLICT
                        (content_checksum)
                    DO NOTHING
                    """
                ),
                {
                    "image_id": (
                        image_id
                    ),
                    "page_id": (
                        page.page_id
                    ),
                    "image_index": (
                        image_index
                    ),
                    "original_filename": (
                        image_path.name
                    ),
                    "image_format": (
                        extension.upper()
                    ),
                    "mime_type": (
                        mime_type
                    ),
                    "file_size_bytes": (
                        image_path
                        .stat()
                        .st_size
                    ),
                    "bucket_name": (
                        bucket_name
                    ),
                    "object_path": (
                        object_path
                    ),
                    "width_px": width,
                    "height_px": height,
                    "bbox_x": max(
                        float(
                            image.bbox_x
                        ),
                        0.0,
                    ),
                    "bbox_y": max(
                        float(
                            image.bbox_y
                        ),
                        0.0,
                    ),
                    "bbox_width": max(
                        float(
                            image.bbox_width
                        ),
                        1.0,
                    ),
                    "bbox_height": max(
                        float(
                            image.bbox_height
                        ),
                        1.0,
                    ),
                    "caption": (
                        image.caption
                    ),
                    "alt_text": (
                        image.alt_text
                    ),
                    "ocr_text": (
                        image.ocr_text
                    ),
                    "content_checksum": (
                        image.sha256
                    ),
                },
            )

        session.flush()

    # ========================================================
    # Table persistence
    # ========================================================

    def _persist_tables(
        self,
        *,
        session,
        document_id: str,
        tables: list[
            ParsedTable
        ],
        page_map: dict[
            int,
            Page,
        ],
        bucket_name: str,
    ) -> None:
        for table in tables:
            page = page_map.get(
                int(
                    table.page_number
                )
            )

            if page is None:
                continue

            table_payload = {
                "title": (
                    table.title
                ),
                "headers": (
                    table.headers
                ),
                "rows": (
                    table.rows
                ),
            }

            binary = json.dumps(
                table_payload,
                ensure_ascii=False,
                default=str,
            ).encode(
                "utf-8"
            )

            checksum = (
                hashlib.sha256(
                    binary
                ).hexdigest()
            )

            object_path = (
                "tables/"
                f"{document_id}/"
                f"{table.table_id}.json"
            )

            self._upload_bytes_to_minio(
                bucket_name=(
                    bucket_name
                ),
                object_path=(
                    object_path
                ),
                data=binary,
            )

            table_id = uuid.UUID(
                str(
                    table.table_id
                )
            )

            headers = [
                str(value)
                for value
                in table.headers
            ]

            row_count = len(
                table.rows
            )

            column_count = max(
                (
                    len(row)
                    for row
                    in table.rows
                ),
                default=len(
                    headers
                ),
            )

            session.execute(
                text(
                    """
                    INSERT INTO knowledge.tables
                    (
                        table_id,
                        page_id,
                        table_index,
                        table_title,
                        table_type,
                        has_header,
                        bucket_name,
                        object_path,
                        storage_format,
                        row_count,
                        column_count,
                        column_headers,
                        table_summary,
                        bbox_x,
                        bbox_y,
                        bbox_width,
                        bbox_height,
                        extraction_engine,
                        extraction_confidence,
                        content_checksum,
                        table_status,
                        is_active
                    )
                    VALUES
                    (
                        :table_id,
                        :page_id,
                        :table_index,
                        :table_title,
                        'DATA_TABLE',
                        :has_header,
                        :bucket_name,
                        :object_path,
                        'JSON',
                        :row_count,
                        :column_count,
                        CAST(
                            :column_headers
                            AS JSONB
                        ),
                        :table_summary,
                        :bbox_x,
                        :bbox_y,
                        :bbox_width,
                        :bbox_height,
                        :extraction_engine,
                        :extraction_confidence,
                        :content_checksum,
                        'EXTRACTED',
                        TRUE
                    )
                    ON CONFLICT
                        (content_checksum)
                    DO NOTHING
                    """
                ),
                {
                    "table_id": (
                        table_id
                    ),
                    "page_id": (
                        page.page_id
                    ),
                    "table_index": max(
                        int(
                            table.table_index
                        ),
                        1,
                    ),
                    "table_title": (
                        table.title
                    ),
                    "has_header": bool(
                        headers
                    ),
                    "bucket_name": (
                        bucket_name
                    ),
                    "object_path": (
                        object_path
                    ),
                    "row_count": (
                        row_count
                    ),
                    "column_count": (
                        column_count
                    ),
                    "column_headers": (
                        json.dumps(
                            headers
                        )
                    ),
                    "table_summary": (
                        table.summary
                    ),
                    "bbox_x": max(
                        float(
                            table.bbox_x
                        ),
                        0.0,
                    ),
                    "bbox_y": max(
                        float(
                            table.bbox_y
                        ),
                        0.0,
                    ),
                    "bbox_width": max(
                        float(
                            table.bbox_width
                        ),
                        1.0,
                    ),
                    "bbox_height": max(
                        float(
                            table.bbox_height
                        ),
                        1.0,
                    ),
                    "extraction_engine": (
                        table.extraction_engine
                    ),
                    "extraction_confidence": (
                        table.extraction_confidence
                    ),
                    "content_checksum": (
                        checksum
                    ),
                },
            )

        session.flush()

    # ========================================================
    # Complete document persistence
    # ========================================================

    def _persist_document_ingestion(
        self,
        *,
        record: dict[
            str,
            Any,
        ],
        parsed: ParsedDocumentResult,
        saved_path: Path,
    ) -> tuple[
        bool,
        Document | None,
    ]:
        if self.minio_service is None:
            raise RuntimeError(
                "MinIO service is required "
                "for document persistence."
            )

        bucket_name = (
            record[
                "bucket_name"
            ]
        )

        object_path = (
            record[
                "object_path"
            ]
        )

        original_uploaded = False

        try:
            with (
                self.database_service
                .transaction()
                as session
            ):
                repository = (
                    DocumentRepository(
                        session
                    )
                )

                owner_user_id = (
                    record.get(
                        "owner_user_id"
                    )
                )

                if owner_user_id is not None:
                    self._ensure_owner_user(
                        session,
                        owner_user_id,
                    )

                checksum = record.get(
                    "checksum_sha256"
                )

                if checksum:
                    existing_document = (
                        repository
                        .get_by_checksum(
                            checksum
                        )
                    )

                    if (
                        existing_document
                        is not None
                        and str(
                            existing_document
                            .document_id
                        )
                        != str(
                            record.get(
                                "document_id"
                            )
                        )
                    ):
                        return (
                            False,
                            existing_document,
                        )

                # Original upload
                self._upload_file_to_minio(
                    bucket_name=(
                        bucket_name
                    ),
                    object_path=(
                        object_path
                    ),
                    path=saved_path,
                )

                original_uploaded = True

                document = (
                    repository
                    .create_document_from_record(
                        record
                    )
                )

                page_map = (
                    self._persist_pages(
                        session=session,
                        document=document,
                        pages=parsed.pages,
                        chunks=parsed.chunks,
                        images=parsed.images,
                        tables=parsed.tables,
                    )
                )

                self._persist_chunks(
                    session=session,
                    chunks=parsed.chunks,
                    page_map=page_map,
                )

                self._persist_images(
                    session=session,
                    document_id=str(
                        document.document_id
                    ),
                    images=parsed.images,
                    page_map=page_map,
                    bucket_name=(
                        bucket_name
                    ),
                )

                self._persist_tables(
                    session=session,
                    document_id=str(
                        document.document_id
                    ),
                    tables=parsed.tables,
                    page_map=page_map,
                    bucket_name=(
                        bucket_name
                    ),
                )

                session.flush()

                return (
                    True,
                    document,
                )

        except Exception:
            if (
                original_uploaded
                and self.minio_service
                is not None
            ):
                try:
                    self.minio_service.delete(
                        bucket_name,
                        object_path,
                    )

                except Exception as cleanup_error:
                    logger.exception(
                        "Failed to clean up "
                        "MinIO object %s/%s "
                        "after transaction failure",
                        bucket_name,
                        object_path,
                        exc_info=(
                            cleanup_error
                        ),
                    )

            raise

    # ========================================================
    # Qdrant verification
    # ========================================================

    def _verify_document_ready_for_index(
        self,
        *,
        document_id: str | None,
        expected_chunk_count: int,
        user_id: str,
    ) -> bool:
        if document_id is None:
            return False

        repository = (
            self.document_repository
        )

        if repository is None:
            with (
                self.database_service
                .transaction()
                as session
            ):
                repository = (
                    DocumentRepository(
                        session
                    )
                )

                return (
                    self._verify_document_ready(
                        repository=repository,
                        document_id=(
                            document_id
                        ),
                        expected_chunk_count=(
                            expected_chunk_count
                        ),
                        user_id=user_id,
                    )
                )

        return self._verify_document_ready(
            repository=repository,
            document_id=document_id,
            expected_chunk_count=(
                expected_chunk_count
            ),
            user_id=user_id,
        )

    def _verify_document_ready(
        self,
        *,
        repository: (
            DocumentRepository
        ),
        document_id: str,
        expected_chunk_count: int,
        user_id: str,
    ) -> bool:
        document = (
            repository.get_by_id(
                document_id
            )
        )

        if (
            document is None
            or self.minio_service
            is None
        ):
            return False

        if not (
            self.minio_service
            .object_exists(
                document.bucket_name,
                document.object_path,
            )
        ):
            return False

        if (
            document.chunk_count
            != expected_chunk_count
        ):
            return False

        # Image-only files can legitimately
        # contain zero text chunks.
        if expected_chunk_count == 0:
            return True

        if self.qdrant_service is None:
            return False

        return (
            self.qdrant_service
            .verify_document_index(
                user_id=user_id,
                document_id=(
                    document_id
                ),
                expected_count=(
                    expected_chunk_count
                ),
            )
        )

    # ========================================================
    # Main upload / ingestion
    # ========================================================

    async def process_upload(
        self,
        *,
        file: UploadFile,
        user_id: str,
    ) -> dict[str, Any]:
        (
            saved_path,
            original_filename,
        ) = await self.save_upload(
            file
        )

        document_id: (
            str | None
        ) = None

        try:
            # ----------------------------------------------
            # Parse ANY supported file
            # ----------------------------------------------

            parsed = parse_document(
                file_path=saved_path,

                display_filename=(
                    original_filename
                ),

                output_path=(
                    app_settings.OUTPUT_DIR
                ),

                chunk_size=2000,

                overlap=250,
            )

            document = (
                parsed.document
            )

            collection_id = (
                self
                ._ensure_default_collection()
            )

            document_id = str(
                document[
                    "document_id"
                ]
            )

            object_path = (
                "uploads/"
                f"{document_id}/"
                f"{original_filename}"
            )

            record = (
                self._build_document_record(
                    parsed_document=(
                        document
                    ),
                    saved_path=(
                        saved_path
                    ),
                    original_filename=(
                        original_filename
                    ),
                    bucket_name=(
                        app_settings
                        .MINIO_BUCKET
                    ),
                    object_path=(
                        object_path
                    ),
                    user_id=user_id,
                    collection_id=(
                        collection_id
                    ),
                )
            )

            (
                created_new,
                persisted_document,
            ) = (
                self
                ._persist_document_ingestion(
                    record=record,
                    parsed=parsed,
                    saved_path=(
                        saved_path
                    ),
                )
            )

            # ----------------------------------------------
            # Processing states
            # ----------------------------------------------

            self._mark_processing_status(
                document_id=(
                    document_id
                ),
                status="PARSING",
            )

            self._mark_processing_status(
                document_id=(
                    document_id
                ),
                status="CHUNKING",
            )

            self._mark_processing_status(
                document_id=(
                    document_id
                ),
                status="EMBEDDING",
            )

            indexed_points = 0

            # ----------------------------------------------
            # Qdrant only needs text chunks
            # ----------------------------------------------

            if (
                created_new
                and parsed.chunks
                and self.qdrant_service
                is not None
            ):
                try:
                    indexed_points = (
                        self.qdrant_service
                        .ingest_chunks(
                            parsed.chunks,
                            user_id=user_id,
                            original_filename=(
                                original_filename
                            ),
                        )
                    )

                except Exception as exc:
                    self._mark_processing_status(
                        document_id=(
                            document_id
                        ),
                        status="FAILED",
                        error=str(exc),
                    )

                    raise

            # ----------------------------------------------
            # Verify MinIO/Qdrant
            # ----------------------------------------------

            if created_new:
                if not (
                    self
                    ._verify_document_ready_for_index(
                        document_id=(
                            document_id
                        ),
                        expected_chunk_count=len(
                            parsed.chunks
                        ),
                        user_id=user_id,
                    )
                ):
                    raise RuntimeError(
                        "Document verification "
                        "failed before INDEXED "
                        "status. "
                        f"document_id="
                        f"{document_id}, "
                        f"expected_chunks="
                        f"{len(parsed.chunks)}, "
                        f"indexed_points="
                        f"{indexed_points}."
                    )

            self._mark_processing_status(
                document_id=(
                    document_id
                ),
                status="INDEXED",
            )

            if persisted_document is not None:
                final_document_id = str(
                    persisted_document
                    .document_id
                )

            else:
                final_document_id = (
                    document_id
                )

            return {
                "message": (
                    "File uploaded, parsed "
                    "and indexed."
                ),
                "document_id": (
                    final_document_id
                ),
                "filename": (
                    original_filename
                ),
                "page_count": len(
                    parsed.pages
                ),
                "chunk_count": len(
                    parsed.chunks
                ),
                "image_count": len(
                    parsed.images
                ),
                "table_count": len(
                    parsed.tables
                ),
                "indexed_points": (
                    indexed_points
                ),
                "document_type": (
                    document.get(
                        "document_type"
                    )
                ),
            }

        except Exception as exc:
            logger.exception(
                "File ingestion failed: %s",
                original_filename,
            )

            self._mark_processing_status(
                document_id=(
                    document_id
                ),
                status="FAILED",
                error=str(exc),
            )

            raise

        finally:
            saved_path.unlink(
                missing_ok=True
            )

    # ========================================================
    # Delete
    # ========================================================

    def delete_document(
        self,
        *,
        document_id: str,
        user_id: str,
    ) -> bool:
        with (
            self.database_service
            .transaction()
            as session
        ):
            repository = (
                DocumentRepository(
                    session
                )
            )

            document = (
                repository.get_by_id(
                    document_id
                )
            )

            owner_user_id = (
                self._resolve_user_id(
                    user_id
                )
            )

            if document is None:
                return False

            if (
                document.owner_user_id
                != owner_user_id
            ):
                raise (
                    DocumentAuthorizationError(
                        "Document deletion "
                        "is not authorized."
                    )
                )

            if (
                self.qdrant_service
                is not None
            ):
                self.qdrant_service.delete_document(
                    user_id=user_id,
                    document_id=document_id,
                )

            if (
                self.minio_service
                is not None
                and self.minio_service
                .object_exists(
                    document.bucket_name,
                    document.object_path,
                )
            ):
                self.minio_service.delete(
                    document.bucket_name,
                    document.object_path,
                )

            repository.delete(
                document
            )

            return True

    # ========================================================
    # Assign ownership
    # ========================================================

    def assign_document_owner(
        self,
        *,
        document_id: str,
        owner_user_id: str,
        assigning_user_id: str,
        auth_service,
    ) -> bool:
        if not auth_service.is_admin(
            assigning_user_id
        ):
            raise (
                DocumentAuthorizationError(
                    "Administrator "
                    "authorization is required."
                )
            )

        requested_owner = (
            self._resolve_user_id(
                owner_user_id
            )
        )

        with (
            self.database_service
            .transaction()
            as session
        ):
            repository = (
                DocumentRepository(
                    session
                )
            )

            document = (
                repository.get_by_id(
                    document_id
                )
            )

            if document is None:
                return False

            target_user = session.get(
                User,
                requested_owner,
            )

            if (
                target_user is None
                or not target_user.is_active
            ):
                raise ValueError(
                    "The requested owner "
                    "does not exist or "
                    "is inactive."
                )

            if (
                document.owner_user_id
                is not None
                and document.owner_user_id
                != requested_owner
            ):
                raise ValueError(
                    "An assigned document "
                    "owner cannot be "
                    "overwritten."
                )

            document.owner_user_id = (
                requested_owner
            )

            repository.update(
                document
            )

            logger.info(
                "Document ownership assigned: "
                "document_id=%s "
                "owner_user_id=%s "
                "assigned_by=%s",
                document_id,
                requested_owner,
                assigning_user_id,
            )

            return True