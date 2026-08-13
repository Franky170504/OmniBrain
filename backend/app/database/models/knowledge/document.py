from __future__ import annotations

import uuid

from datetime import datetime

from sqlalchemy import BigInteger
from sqlalchemy import Boolean
from sqlalchemy import CHAR
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import func
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.database.base import Base
from app.database.mixins import TimestampMixin


class Document(Base, TimestampMixin):
    __tablename__ = 'documents'
    __table_args__ = {'schema': 'knowledge'}

    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.uuid_generate_v4(),
    )
    collection_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('knowledge.collections.collection_id', onupdate='CASCADE', ondelete='RESTRICT'),
        nullable=False,
    )
    owner_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('auth.users.user_id', onupdate='CASCADE', ondelete='RESTRICT'),
        nullable=True,
    )
    document_title: Mapped[str] = mapped_column(String(255), nullable=False)
    document_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_extension: Mapped[str] = mapped_column(String(20), nullable=False)
    document_type: Mapped[str] = mapped_column(String(20), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    bucket_name: Mapped[str] = mapped_column(String(100), nullable=False)
    object_path: Mapped[str] = mapped_column(Text, nullable=False)
    checksum_sha256: Mapped[str] = mapped_column(CHAR(64), nullable=False)
    processing_status: Mapped[str] = mapped_column(String(30), nullable=False, server_default=text("'UPLOADED'"))
    processing_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    last_processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('1'))
    language_code: Mapped[str | None] = mapped_column(CHAR(2), nullable=True)
    page_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    chunk_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    image_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    table_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('TRUE'))

    collection: Mapped['Collection'] = relationship('Collection', back_populates='documents')
    pages: Mapped[list['Page']] = relationship(
        'Page',
        back_populates='document',
        cascade='all, delete-orphan',
    )

    def __repr__(self) -> str:
        return f"<Document(document_id={self.document_id}, document_title={self.document_title})>"
