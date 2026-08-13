from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime
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


class Dataset(Base, TimestampMixin):
    __tablename__ = 'datasets'
    __table_args__ = {'schema': 'structured'}

    dataset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text('gen_random_uuid()'),
    )
    source_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('structured.data_sources.source_id', ondelete='CASCADE'),
        nullable=False,
    )
    dataset_name: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    database_name: Mapped[str] = mapped_column(String(255), nullable=False)
    database_schema: Mapped[str] = mapped_column(String(255), nullable=False)
    dataset_type: Mapped[str] = mapped_column(String(50), nullable=False)
    database_engine: Mapped[str] = mapped_column(String(50), nullable=False)
    dataset_status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        server_default=text("'active'"),
    )
    dataset_version: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        server_default=text("'1.0'"),
    )
    last_synced_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    remarks: Mapped[str | None] = mapped_column(Text, nullable=True)

    source: Mapped['DataSource'] = relationship('DataSource', back_populates='datasets')
    tables: Mapped[list['Table']] = relationship(
        'Table',
        back_populates='dataset',
        cascade='all, delete-orphan',
    )
    statistics: Mapped['DatasetStatistics'] = relationship(
        'DatasetStatistics',
        back_populates='dataset',
        uselist=False,
        cascade='all, delete-orphan',
    )
    refresh_history: Mapped[list['DatasetRefreshHistory']] = relationship(
        'DatasetRefreshHistory',
        back_populates='dataset',
        cascade='all, delete-orphan',
    )

    def __repr__(self) -> str:
        return f"<Dataset(dataset_id={self.dataset_id}, dataset_name={self.dataset_name})>"
