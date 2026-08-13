from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import SmallInteger
from sqlalchemy import Text
from sqlalchemy import func
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.database.base import Base
from app.database.mixins import TimestampMixin


class DatasetRelationshipColumn(Base, TimestampMixin):
    __tablename__ = 'dataset_relationship_columns'
    __table_args__ = {'schema': 'structured'}

    relationship_column_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text('gen_random_uuid()'),
    )
    relationship_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('structured.dataset_relationships.relationship_id', ondelete='CASCADE'),
        nullable=False,
    )
    source_column_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('structured.dataset_columns.column_id', ondelete='RESTRICT'),
        nullable=False,
    )
    target_column_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('structured.dataset_columns.column_id', ondelete='RESTRICT'),
        nullable=False,
    )
    column_sequence: Mapped[int] = mapped_column(SmallInteger, nullable=False)

    dataset_relationship: Mapped['DatasetRelationship'] = relationship(
        'DatasetRelationship',
        back_populates='relationship_columns',
    )
    source_column: Mapped['Column'] = relationship(
        'Column',
        back_populates='source_relationship_columns',
        foreign_keys='DatasetRelationshipColumn.source_column_id',
    )
    target_column: Mapped['Column'] = relationship(
        'Column',
        back_populates='target_relationship_columns',
        foreign_keys='DatasetRelationshipColumn.target_column_id',
    )

    def __repr__(self) -> str:
        return f"<DatasetRelationshipColumn(relationship_column_id={self.relationship_column_id}, column_sequence={self.column_sequence})>"
