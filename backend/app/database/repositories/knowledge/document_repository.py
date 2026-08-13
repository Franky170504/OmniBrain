from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models.knowledge.document import Document
from app.database.repositories.base_repository import BaseRepository


class DocumentRepository(BaseRepository[Document]):
    def __init__(self, session: Session) -> None:
        super().__init__(session=session, model=Document)

    def get_by_id(self, document_id: str | Any) -> Document | None:
        return super().get_by_id(document_id)

    def get_by_checksum(self, checksum_sha256: str) -> Document | None:
        statement = select(self.model).where(
            self.model.checksum_sha256 == checksum_sha256
        )
        return self.session.scalar(statement)

    def get_by_original_filename(self, original_filename: str) -> list[Document]:
        statement = select(self.model).where(
            self.model.original_filename == original_filename
        )
        return list(self.session.scalars(statement).all())

    def create_document(self, document: Document) -> Document:
        return self.create(document)

    def create_document_from_record(self, record: dict[str, Any]) -> Document | None:
        checksum_sha256 = record.get("checksum_sha256")
        if checksum_sha256:
            existing = self.get_by_checksum(checksum_sha256)
            if existing is not None:
                return existing

        document = Document(
            document_id=record["document_id"],
            collection_id=record["collection_id"],
            document_title=record["document_title"],
            owner_user_id=record.get("owner_user_id"),
            document_description=record["document_description"],
            original_filename=record["original_filename"],
            mime_type=record["mime_type"],
            file_extension=record["file_extension"],
            document_type=record["document_type"],
            file_size_bytes=record["file_size_bytes"],
            bucket_name=record["bucket_name"],
            object_path=record["object_path"],
            checksum_sha256=record["checksum_sha256"],
            processing_status=record["processing_status"],
            page_count=record["page_count"],
            chunk_count=record["chunk_count"],
            image_count=record["image_count"],
            language_code=record["language_code"],
            table_count=0,
            is_active=True,
        )
        self.create(document)
        self.session.flush()
        return document
