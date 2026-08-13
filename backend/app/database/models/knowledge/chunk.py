from __future__ import annotations

import uuid

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


class Chunk(Base, TimestampMixin):
    __tablename__ = 'chunks'
    __table_args__ = {'schema': 'knowledge'}

    chunk_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.uuid_generate_v4(),
    )
    page_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('knowledge.pages.page_id', onupdate='CASCADE', ondelete='CASCADE'),
        nullable=False,
    )
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    chunk_text: Mapped[str] = mapped_column(Text, nullable=False)
    chunk_type: Mapped[str] = mapped_column(String(30), nullable=False, server_default=text("'TEXT'"))
    character_start: Mapped[int] = mapped_column(Integer, nullable=False)
    character_end: Mapped[int] = mapped_column(Integer, nullable=False)
    token_count: Mapped[int] = mapped_column(Integer, nullable=False)
    vector_point_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    embedding_model: Mapped[str | None] = mapped_column(Text, nullable=True)
    embedding_dimension: Mapped[int | None] = mapped_column(Integer, nullable=True)
    embedding_generated_at: Mapped[object | None] = mapped_column(DateTime(timezone=True), nullable=True)
    content_checksum: Mapped[str] = mapped_column(CHAR(64), nullable=False)
    chunk_status: Mapped[str] = mapped_column(String(20), nullable=False, server_default=text("'CREATED'"))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('TRUE'))

    page: Mapped['Page'] = relationship('Page', back_populates='chunks')

    def __repr__(self) -> str:
        return f"<Chunk(chunk_id={self.chunk_id}, page_id={self.page_id}, chunk_index={self.chunk_index})>"
