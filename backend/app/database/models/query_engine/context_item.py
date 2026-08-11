from __future__ import annotations

import uuid

from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import Numeric
from sqlalchemy import SmallInteger
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import func
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.database.base import Base
from app.database.mixins import TimestampMixin


class ContextItem(Base, TimestampMixin):
    __tablename__ = 'context_items'
    __table_args__ = {'schema': 'query_engine'}

    context_item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.uuid_generate_v4(),
    )

    retrieval_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('query_engine.retrieved_context.retrieval_id', onupdate='CASCADE', ondelete='CASCADE'),
        nullable=False,
    )

    item_type_id: Mapped[int] = mapped_column(
        SmallInteger,
        ForeignKey('query_engine.context_item_types.item_type_id', onupdate='CASCADE', ondelete='RESTRICT'),
        nullable=False,
    )

    chunk_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('knowledge.chunks.chunk_id', onupdate='CASCADE', ondelete='CASCADE'),
        nullable=True,
    )

    image_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('knowledge.images.image_id', onupdate='CASCADE', ondelete='CASCADE'),
        nullable=True,
    )

    table_entity_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('knowledge.tables.table_id', onupdate='CASCADE', ondelete='CASCADE'),
        nullable=True,
    )

    datasource_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('structured.data_sources.source_id', onupdate='CASCADE', ondelete='CASCADE'),
        nullable=True,
    )

    retrieval_rank: Mapped[int] = mapped_column(Integer, nullable=False)
    relevance_score: Mapped[float] = mapped_column(Numeric(6, 5), nullable=False)
    page_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    citation_label: Mapped[str | None] = mapped_column(String(100), nullable=True)
    highlight_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    metadata_json: Mapped[dict] = mapped_column('metadata', JSONB, nullable=False, server_default=text("'{}'::jsonb"))

    retrieval: Mapped['RetrievedContext'] = relationship('RetrievedContext', back_populates='context_items')
    item_type: Mapped['ContextItemType'] = relationship('ContextItemType', back_populates='context_items')

    def __repr__(self) -> str:
        return f"<ContextItem(context_item_id={self.context_item_id}, retrieval_id={self.retrieval_id}, rank={self.retrieval_rank})>"
