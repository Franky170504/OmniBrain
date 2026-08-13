from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import BigInteger
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import func
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.database.base import Base
from app.database.mixins import TimestampMixin


class TableStatistics(Base, TimestampMixin):
    __tablename__ = 'table_statistics'
    __table_args__ = {'schema': 'structured'}

    table_statistics_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text('gen_random_uuid()'),
    )
    table_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('structured.dataset_tables.table_id', ondelete='CASCADE'),
        nullable=False,
    )
    row_count: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        server_default=text('0'),
    )
    live_row_count: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        server_default=text('0'),
    )
    dead_row_count: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        server_default=text('0'),
    )
    column_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text('0'),
    )
    primary_key_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text('0'),
    )
    foreign_key_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text('0'),
    )
    unique_constraint_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text('0'),
    )
    check_constraint_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text('0'),
    )
    index_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text('0'),
    )
    table_size_bytes: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        server_default=text('0'),
    )
    index_size_bytes: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        server_default=text('0'),
    )
    toast_size_bytes: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        server_default=text('0'),
    )
    total_size_bytes: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        server_default=text('0'),
    )
    statistics_generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text('CURRENT_TIMESTAMP'),
    )

    table: Mapped['Table'] = relationship('Table', back_populates='statistics')

    def __repr__(self) -> str:
        return f"<TableStatistics(table_statistics_id={self.table_statistics_id}, table_id={self.table_id})>"
