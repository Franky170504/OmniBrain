from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Numeric
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


class DatasetRelationship(Base, TimestampMixin):
    __tablename__ = 'dataset_relationships'
    __table_args__ = {'schema': 'structured'}

    relationship_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text('gen_random_uuid()'),
    )
    source_table_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('structured.dataset_tables.table_id', ondelete='CASCADE'),
        nullable=False,
    )
    target_table_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('structured.dataset_tables.table_id', ondelete='CASCADE'),
        nullable=False,
    )
    relationship_name: Mapped[str] = mapped_column(String(255), nullable=False)
    constraint_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    relationship_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        server_default=text("'FOREIGN_KEY'"),
    )
    cardinality: Mapped[str] = mapped_column(String(20), nullable=False)
    on_update_action: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default=text("'NO_ACTION'"),
    )
    on_delete_action: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default=text("'NO_ACTION'"),
    )
    discovery_method: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default=text("'CATALOG'"),
    )
    confidence_score: Mapped[float] = mapped_column(
        Numeric(5, 4),
        nullable=False,
        server_default=text('1.0000'),
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text('FALSE'),
    )
    last_verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    relationship_status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default=text("'ACTIVE'"),
    )

    source_table: Mapped['Table'] = relationship(
        'Table',
        back_populates='source_relationships',
        foreign_keys='DatasetRelationship.source_table_id',
    )
    target_table: Mapped['Table'] = relationship(
        'Table',
        back_populates='target_relationships',
        foreign_keys='DatasetRelationship.target_table_id',
    )
    relationship_columns: Mapped[list['DatasetRelationshipColumn']] = relationship(
        'DatasetRelationshipColumn',
        back_populates='dataset_relationship',
        cascade='all, delete-orphan',
    )

    def __repr__(self) -> str:
        return f"<DatasetRelationship(relationship_id={self.relationship_id}, relationship_name={self.relationship_name})>"
