from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean
from sqlalchemy import DateTime
from sqlalchemy import SmallInteger
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import func
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.database.base import Base
from app.database.mixins import TimestampMixin


class ContextItemType(Base, TimestampMixin):
    __tablename__ = 'context_item_types'
    __table_args__ = {'schema': 'query_engine'}

    item_type_id: Mapped[int] = mapped_column(
        SmallInteger,
        primary_key=True,
    )

    item_type_code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
    )

    display_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    color_code: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True,
    )

    icon_name: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    display_order: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
        unique=True,
    )

    is_system: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text('TRUE'),
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text('TRUE'),
    )

    version: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
        server_default=text('1'),
    )

    metadata_json: Mapped[dict] = mapped_column(
        'metadata',
        JSONB,
        nullable=False,
        server_default=text("'{}'::jsonb"),
    )

    context_items: Mapped[list['ContextItem']] = relationship(
        'ContextItem',
        back_populates='item_type',
    )

    def __repr__(self) -> str:
        return f"<ContextItemType(item_type_id={self.item_type_id}, item_type_code={self.item_type_code})>"
