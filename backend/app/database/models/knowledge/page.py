from __future__ import annotations

import uuid

from sqlalchemy import Boolean
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import func
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.database.base import Base
from app.database.mixins import TimestampMixin


class Page(Base, TimestampMixin):
    __tablename__ = 'pages'
    __table_args__ = {'schema': 'knowledge'}

    page_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.uuid_generate_v4(),
    )
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('knowledge.documents.document_id', onupdate='CASCADE', ondelete='CASCADE'),
        nullable=False,
    )
    page_number: Mapped[int] = mapped_column(Integer, nullable=False)
    page_label: Mapped[str | None] = mapped_column(String(50), nullable=True)
    page_type: Mapped[str] = mapped_column(String(20), nullable=False, server_default=text("'DOCUMENT'"))
    ocr_applied: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('FALSE'))
    character_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    word_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    chunk_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    image_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    table_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('TRUE'))

    document: Mapped['Document'] = relationship('Document', back_populates='pages')
    chunks: Mapped[list['Chunk']] = relationship(
        'Chunk',
        back_populates='page',
        cascade='all, delete-orphan',
    )
    images: Mapped[list['Image']] = relationship(
        'Image',
        back_populates='page',
        cascade='all, delete-orphan',
    )
    tables: Mapped[list['TableEntity']] = relationship(
        'TableEntity',
        back_populates='page',
        cascade='all, delete-orphan',
    )

    def __repr__(self) -> str:
        return f"<Page(page_id={self.page_id}, document_id={self.document_id}, page_number={self.page_number})>"
