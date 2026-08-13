from __future__ import annotations

import uuid

from sqlalchemy import BigInteger
from sqlalchemy import Boolean
from sqlalchemy import CHAR
from sqlalchemy import DateTime
from sqlalchemy import Double
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


class Image(Base, TimestampMixin):
    __tablename__ = 'images'
    __table_args__ = {'schema': 'knowledge'}

    image_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.uuid_generate_v4(),
    )
    page_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('knowledge.pages.page_id', onupdate='CASCADE', ondelete='CASCADE'),
        nullable=False,
    )
    image_index: Mapped[int] = mapped_column(Integer, nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    image_format: Mapped[str] = mapped_column(String(20), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    bucket_name: Mapped[str] = mapped_column(String(100), nullable=False)
    object_path: Mapped[str] = mapped_column(Text, nullable=False)
    width_px: Mapped[int] = mapped_column(Integer, nullable=False)
    height_px: Mapped[int] = mapped_column(Integer, nullable=False)
    bbox_x: Mapped[float] = mapped_column(Double, nullable=False)
    bbox_y: Mapped[float] = mapped_column(Double, nullable=False)
    bbox_width: Mapped[float] = mapped_column(Double, nullable=False)
    bbox_height: Mapped[float] = mapped_column(Double, nullable=False)
    caption: Mapped[str | None] = mapped_column(Text, nullable=True)
    alt_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    ocr_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    vector_point_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    embedding_model: Mapped[str | None] = mapped_column(Text, nullable=True)
    embedding_dimension: Mapped[int | None] = mapped_column(Integer, nullable=True)
    embedding_generated_at: Mapped[object | None] = mapped_column(DateTime(timezone=True), nullable=True)
    content_checksum: Mapped[str] = mapped_column(CHAR(64), nullable=False)
    image_status: Mapped[str] = mapped_column(String(30), nullable=False, server_default=text("'EXTRACTED'"))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('TRUE'))

    page: Mapped['Page'] = relationship('Page', back_populates='images')

    def __repr__(self) -> str:
        return f"<Image(image_id={self.image_id}, page_id={self.page_id}, image_index={self.image_index})>"
