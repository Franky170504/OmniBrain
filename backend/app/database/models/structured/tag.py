from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean
from sqlalchemy import CHAR
from sqlalchemy import Computed
from sqlalchemy import DateTime
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


class Tag(Base, TimestampMixin):
    __tablename__ = 'tags'
    __table_args__ = {'schema': 'structured'}

    tag_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text('gen_random_uuid()'),
    )
    tag_name: Mapped[str] = mapped_column(String(100), nullable=False)
    tag_name_normalized: Mapped[str] = mapped_column(
        String(100),
        Computed("LOWER(BTRIM(tag_name))", persisted=True),
        nullable=False,
    )
    tag_category: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    color_code: Mapped[str | None] = mapped_column(
        CHAR(7),
        nullable=True,
        server_default=text("'#808080'"),
    )
    is_system_tag: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text('FALSE'),
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text('TRUE'),
    )
    created_by: Mapped[str | None] = mapped_column(String(100), nullable=True)

    resource_tags: Mapped[list['ResourceTag']] = relationship(
        'ResourceTag',
        back_populates='tag',
        cascade='all, delete-orphan',
    )

    def __repr__(self) -> str:
        return f"<Tag(tag_id={self.tag_id}, tag_name={self.tag_name})>"
