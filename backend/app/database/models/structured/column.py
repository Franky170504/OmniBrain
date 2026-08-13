from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import BigInteger
from sqlalchemy import Boolean
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import func
from sqlalchemy import Numeric
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.database.base import Base
from app.database.mixins import TimestampMixin


class Column(Base, TimestampMixin):
    __tablename__ = 'dataset_columns'
    __table_args__ = {'schema': 'structured'}

    column_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )
    table_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('structured.dataset_tables.table_id', ondelete='CASCADE'),
        nullable=False,
    )
    column_name: Mapped[str] = mapped_column(String(255), nullable=False)
    column_display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    ordinal_position: Mapped[int] = mapped_column(Integer, nullable=False)
    logical_data_type: Mapped[str] = mapped_column(String(50), nullable=False)
    physical_data_type: Mapped[str] = mapped_column(String(128), nullable=False)
    character_maximum_length: Mapped[int | None] = mapped_column(Integer, nullable=True)
    numeric_precision: Mapped[int | None] = mapped_column(Integer, nullable=True)
    numeric_scale: Mapped[int | None] = mapped_column(Integer, nullable=True)
    datetime_precision: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_nullable: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text('TRUE'),
    )
    is_primary_key: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text('FALSE'),
    )
    is_foreign_key: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text('FALSE'),
    )
    is_unique: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text('FALSE'),
    )
    is_indexed: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text('FALSE'),
    )
    column_default: Mapped[str | None] = mapped_column(Text, nullable=True)
    semantic_role: Mapped[str | None] = mapped_column(String(50), nullable=True)
    sample_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_searchable: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text('TRUE'),
    )
    is_filterable: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text('TRUE'),
    )
    is_sortable: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text('TRUE'),
    )
    column_status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default=text("'ACTIVE'"),
    )
    last_synced_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    table: Mapped['Table'] = relationship('Table', back_populates='columns')
    source_relationship_columns: Mapped[list['DatasetRelationshipColumn']] = relationship(
        'DatasetRelationshipColumn',
        back_populates='source_column',
        foreign_keys='DatasetRelationshipColumn.source_column_id',
        cascade='all, delete-orphan',
    )
    target_relationship_columns: Mapped[list['DatasetRelationshipColumn']] = relationship(
        'DatasetRelationshipColumn',
        back_populates='target_column',
        foreign_keys='DatasetRelationshipColumn.target_column_id',
        cascade='all, delete-orphan',
    )
    column_statistics: Mapped['ColumnStatistics'] = relationship(
        'ColumnStatistics',
        back_populates='column',
        uselist=False,
        cascade='all, delete-orphan',
    )

    def __repr__(self) -> str:
        return f"<Column(column_id={self.column_id}, column_name={self.column_name})>"
