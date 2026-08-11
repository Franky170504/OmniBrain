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


class RetrievalStrategy(Base, TimestampMixin):
    __tablename__ = 'retrieval_strategies'
    __table_args__ = {'schema': 'query_engine'}

    strategy_id: Mapped[int] = mapped_column(
        SmallInteger,
        primary_key=True,
    )

    strategy_code: Mapped[str] = mapped_column(
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

    category: Mapped[str | None] = mapped_column(
        String(50),
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

    supports_vector: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text('FALSE'),
    )

    supports_keyword: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text('FALSE'),
    )

    supports_sql: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text('FALSE'),
    )

    supports_graph: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text('FALSE'),
    )

    supports_multimodal: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text('FALSE'),
    )

    supports_agents: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text('FALSE'),
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
        back_populates='strategy',
        foreign_keys='[Query.strategy_id]',
    )

    def __repr__(self) -> str:
        return f"<RetrievalStrategy(strategy_id={self.strategy_id}, strategy_code={self.strategy_code})>"
