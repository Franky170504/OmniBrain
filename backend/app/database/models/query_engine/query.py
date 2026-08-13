from __future__ import annotations

import uuid

from datetime import datetime

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
from app.database.mixins import TimestampMixin, SoftDeleteMixin


class Query(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = 'queries'
    __table_args__ = {'schema': 'query_engine'}

    query_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.uuid_generate_v4(),
    )

    turn_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('query_engine.conversation_turns.turn_id', onupdate='CASCADE', ondelete='CASCADE'),
        nullable=False,
    )

    parent_query_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('query_engine.queries.query_id', onupdate='CASCADE', ondelete='SET NULL'),
        nullable=True,
    )

    domain_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('knowledge.domains.domain_id', onupdate='CASCADE', ondelete='SET NULL'),
        nullable=True,
    )

    intent_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('query_engine.query_intents.intent_id', onupdate='CASCADE', ondelete='RESTRICT'),
        nullable=False,
    )
    status_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('query_engine.query_statuses.status_id', onupdate='CASCADE', ondelete='RESTRICT'),
        nullable=False,
    )
    strategy_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('query_engine.retrieval_strategies.strategy_id', onupdate='CASCADE', ondelete='RESTRICT'),
        nullable=False,
    )
    priority_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('query_engine.query_priorities.priority_id', onupdate='CASCADE', ondelete='RESTRICT'),
        nullable=False,
    )
    original_query: Mapped[str] = mapped_column(Text, nullable=False)
    rewritten_query: Mapped[str | None] = mapped_column(Text, nullable=True)
    normalized_query: Mapped[str | None] = mapped_column(Text, nullable=True)
    language_code: Mapped[str] = mapped_column(CHAR(2), nullable=False, server_default=text("'en'"))
    intent_confidence: Mapped[float | None] = mapped_column(Numeric(5, 4), nullable=True)
    domain_confidence: Mapped[float | None] = mapped_column(Numeric(5, 4), nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    metadata_json: Mapped[dict] = mapped_column('metadata', JSONB, nullable=False, server_default=text("'{}'::jsonb"))

    turn: Mapped["ConversationTurn"] = relationship('ConversationTurn', back_populates='queries')
    parent_query: Mapped["Query | None"] = relationship(
        'Query',
        remote_side='Query.query_id',
        back_populates='child_queries',
        foreign_keys=[parent_query_id],
    )
    child_queries: Mapped[list["Query"]] = relationship(
        'Query',
        back_populates='parent_query',
        cascade='all, delete-orphan',
        foreign_keys='[Query.parent_query_id]',
    )
    intent: Mapped["QueryIntent"] = relationship('QueryIntent', back_populates='queries', foreign_keys=[intent_id])
    status: Mapped["QueryStatus"] = relationship('QueryStatus', back_populates='queries', foreign_keys=[status_id])
    strategy: Mapped["RetrievalStrategy"] = relationship('RetrievalStrategy', back_populates='queries', foreign_keys=[strategy_id])
    priority: Mapped["QueryPriority"] = relationship('QueryPriority', back_populates='queries', foreign_keys=[priority_id])
    retrieved_contexts: Mapped[list["RetrievedContext"]] = relationship(
        'RetrievedContext',
        back_populates='query',
        cascade='all, delete-orphan',
    )
    agent_executions: Mapped[list["AgentExecution"]] = relationship(
        'AgentExecution',
        back_populates='query',
        cascade='all, delete-orphan',
    )
    responses: Mapped[list["Response"]] = relationship(
        'Response',
        back_populates='query',
        cascade='all, delete-orphan',
    )
    metrics: Mapped[list["Metrics"]] = relationship(
        'Metrics',
        back_populates='query',
        cascade='all, delete-orphan',
    )

    def __repr__(self) -> str:
        return f"<Query(query_id={self.query_id}, turn_id={self.turn_id}, status_id={self.status_id})>"
