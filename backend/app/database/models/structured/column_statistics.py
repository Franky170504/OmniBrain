from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import BigInteger
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import Numeric
from sqlalchemy import Text
from sqlalchemy import func
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.database.base import Base
from app.database.mixins import TimestampMixin


class ColumnStatistics(Base, TimestampMixin):
    __tablename__ = 'column_statistics'
    __table_args__ = {'schema': 'structured'}

    statistics_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text('gen_random_uuid()'),
    )
    column_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('structured.dataset_columns.column_id', ondelete='CASCADE'),
        nullable=False,
    )
    distinct_value_count: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        server_default=text('0'),
    )
    duplicate_value_count: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        server_default=text('0'),
    )
    unique_value_percentage: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    null_value_count: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        server_default=text('0'),
    )
    null_percentage: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    minimum_value: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    maximum_value: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    average_value: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    median_value: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    standard_deviation: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    minimum_length: Mapped[int | None] = mapped_column(Integer, nullable=True)
    maximum_length: Mapped[int | None] = mapped_column(Integer, nullable=True)
    average_length: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    sample_values: Mapped[dict | None] = mapped_column(Text, nullable=True)
    statistics_generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text('CURRENT_TIMESTAMP'),
    )

    column: Mapped['Column'] = relationship('Column', back_populates='column_statistics')

    def __repr__(self) -> str:
        return f"<ColumnStatistics(statistics_id={self.statistics_id}, column_id={self.column_id})>"
