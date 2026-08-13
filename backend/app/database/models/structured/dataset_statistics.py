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


class DatasetStatistics(Base, TimestampMixin):
    __tablename__ = 'dataset_statistics'
    __table_args__ = {'schema': 'structured'}

    statistics_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text('gen_random_uuid()'),
    )
    dataset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('structured.datasets.dataset_id', ondelete='CASCADE'),
        nullable=False,
    )
    row_count: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        server_default=text('0'),
    )
    table_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text('0'),
    )
    view_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text('0'),
    )
    materialized_view_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text('0'),
    )
    total_storage_bytes: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        server_default=text('0'),
    )
    largest_table_size_bytes: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        server_default=text('0'),
    )
    statistics_generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text('CURRENT_TIMESTAMP'),
    )

    dataset: Mapped['Dataset'] = relationship('Dataset', back_populates='statistics')

    def __repr__(self) -> str:
        return f"<DatasetStatistics(statistics_id={self.statistics_id}, dataset_id={self.dataset_id})>"
