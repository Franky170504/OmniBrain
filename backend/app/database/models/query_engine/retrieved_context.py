from __future__ import annotations

import uuid

from datetime import datetime

from sqlalchemy import Boolean
from sqlalchemy import CHAR
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import Numeric
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


class RetrievedContext(Base, TimestampMixin):
    __tablename__ = 'retrieved_context'
    __table_args__ = {'schema': 'query_engine'}

    retrieval_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.uuid_generate_v4(),
    )

    query_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('query_engine.queries.query_id', onupdate='CASCADE', ondelete='CASCADE'),
        nullable=False,
    )

    retriever_name: Mapped[str] = mapped_column(Text, nullable=False)
    retriever_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    reranker_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    reranker_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    search_namespace: Mapped[str] = mapped_column(String(150), nullable=False)
    retrieval_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    cache_key: Mapped[str | None] = mapped_column(String(255), nullable=True)
    cache_hit: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('FALSE'))
    retrieval_source: Mapped[str] = mapped_column(String(20), nullable=False, server_default=text("'LIVE'"))
    candidate_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    returned_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    filtered_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    retrieval_confidence: Mapped[float | None] = mapped_column(Numeric(5, 4), nullable=True)
    metadata_json: Mapped[dict] = mapped_column('metadata', JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('1'))

    query: Mapped['Query'] = relationship('Query', back_populates='retrieved_contexts')
    context_items: Mapped[list['ContextItem']] = relationship(
        'ContextItem',
        back_populates='retrieval',
        cascade='all, delete-orphan',
    )

    def __repr__(self) -> str:
        return f"<RetrievedContext(retrieval_id={self.retrieval_id}, query_id={self.query_id})>"
