from __future__ import annotations

import uuid

from sqlalchemy import Boolean
from sqlalchemy import DateTime
from sqlalchemy import Double
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import func
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.database.base import Base
from app.database.mixins import TimestampMixin


class TableEntity(Base, TimestampMixin):
    __tablename__ = 'tables'
    __table_args__ = {'schema': 'knowledge'}

    table_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.uuid_generate_v4(),
    )
    page_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('knowledge.pages.page_id', onupdate='CASCADE', ondelete='CASCADE'),
        nullable=False,
    )
    table_index: Mapped[int] = mapped_column(Integer, nullable=False)
    table_title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    table_type: Mapped[str] = mapped_column(String(30), nullable=False, server_default=text("'DATA_TABLE'"))
    has_header: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('TRUE'))
    bucket_name: Mapped[str] = mapped_column(String(100), nullable=False)
    object_path: Mapped[str] = mapped_column(Text, nullable=False)
    storage_format: Mapped[str] = mapped_column(String(20), nullable=False)
    row_count: Mapped[int] = mapped_column(Integer, nullable=False)
    column_count: Mapped[int] = mapped_column(Integer, nullable=False)
    column_headers: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    table_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    bbox_x: Mapped[float] = mapped_column(Double, nullable=False)
    bbox_y: Mapped[float] = mapped_column(Double, nullable=False)
    bbox_width: Mapped[float] = mapped_column(Double, nullable=False)
    bbox_height: Mapped[float] = mapped_column(Double, nullable=False)
    extraction_engine: Mapped[str | None] = mapped_column(String(100), nullable=True)
    extraction_confidence: Mapped[float | None] = mapped_column(None, nullable=True)
    vector_point_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    embedding_model: Mapped[str | None] = mapped_column(Text, nullable=True)
    embedding_dimension: Mapped[int | None] = mapped_column(Integer, nullable=True)
    embedding_generated_at: Mapped[object | None] = mapped_column(DateTime(timezone=True), nullable=True)
    content_checksum: Mapped[str] = mapped_column(String(64), nullable=False)
    table_status: Mapped[str] = mapped_column(String(30), nullable=False, server_default=text("'EXTRACTED'"))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('TRUE'))

    page: Mapped['Page'] = relationship('Page', back_populates='tables')

    def __repr__(self) -> str:
        return f"<TableEntity(table_id={self.table_id}, page_id={self.page_id}, table_index={self.table_index})>"
