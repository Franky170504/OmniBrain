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


class QueryIntent(Base, TimestampMixin):
    __tablename__ = 'query_intents'
    __table_args__ = {'schema': 'query_engine'}

    intent_id: Mapped[int] = mapped_column(
        SmallInteger,
        primary_key=True,
    )

    intent_code: Mapped[str] = mapped_column(
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

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text('TRUE'),
    )

    is_system: Mapped[bool] = mapped_column(
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

    queries: Mapped[list['Query']] = relationship(
        'Query',
        back_populates='intent',
        foreign_keys='[Query.intent_id]',
    )

    def __repr__(self) -> str:
        return f"<QueryIntent(intent_id={self.intent_id}, intent_code={self.intent_code})>"
