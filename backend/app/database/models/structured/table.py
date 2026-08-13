from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean
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


class Table(Base, TimestampMixin):
    __tablename__ = 'dataset_tables'
    __table_args__ = {'schema': 'structured'}

    table_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )
    dataset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('structured.datasets.dataset_id', ondelete='CASCADE'),
        nullable=False,
    )
    table_name: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    table_schema: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    table_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        server_default=text("'BASE_TABLE'"),
    )
    storage_engine: Mapped[str | None] = mapped_column(String(100), nullable=True)
    table_status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default=text("'ACTIVE'"),
    )
    last_synced_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    dataset: Mapped['Dataset'] = relationship('Dataset', back_populates='tables')
    columns: Mapped[list['Column']] = relationship(
        'Column',
        back_populates='table',
        cascade='all, delete-orphan',
    )
    source_relationships: Mapped[list['DatasetRelationship']] = relationship(
        'DatasetRelationship',
        back_populates='source_table',
        foreign_keys='DatasetRelationship.source_table_id',
        cascade='all, delete-orphan',
    )
    target_relationships: Mapped[list['DatasetRelationship']] = relationship(
        'DatasetRelationship',
        back_populates='target_table',
        foreign_keys='DatasetRelationship.target_table_id',
        cascade='all, delete-orphan',
    )
    statistics: Mapped['TableStatistics'] = relationship(
        'TableStatistics',
        back_populates='table',
        uselist=False,
        cascade='all, delete-orphan',
    )

    def __repr__(self) -> str:
        return f"<Table(table_id={self.table_id}, table_name={self.table_name})>"
