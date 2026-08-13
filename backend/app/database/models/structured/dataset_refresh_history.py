from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import BigInteger
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
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


class DatasetRefreshHistory(Base, TimestampMixin):
    __tablename__ = 'dataset_refresh_history'
    __table_args__ = {'schema': 'structured'}

    refresh_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text('gen_random_uuid()'),
    )
    dataset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('structured.datasets.dataset_id', ondelete='CASCADE'),
        nullable=False,
    )
    execution_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        server_default=text('gen_random_uuid()'),
    )
    refresh_type: Mapped[str] = mapped_column(String(20), nullable=False)
    refresh_mode: Mapped[str] = mapped_column(String(20), nullable=False)
    refresh_status: Mapped[str] = mapped_column(String(20), nullable=False)
    retry_number: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        server_default=text('0'),
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text('CURRENT_TIMESTAMP'),
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    duration_ms: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    rows_read: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    rows_processed: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    rows_inserted: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    rows_updated: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    rows_deleted: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    rows_failed: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    error_code: Mapped[str | None] = mapped_column(String(100), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    triggered_by: Mapped[str | None] = mapped_column(String(100), nullable=True)

    dataset: Mapped['Dataset'] = relationship('Dataset', back_populates='refresh_history')

    def __repr__(self) -> str:
        return f"<DatasetRefreshHistory(refresh_id={self.refresh_id}, dataset_id={self.dataset_id})>"
