from __future__ import annotations

import uuid

from datetime import datetime

from sqlalchemy import BigInteger
from sqlalchemy import Boolean
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


class Metrics(Base, TimestampMixin):
    __tablename__ = 'metrics'
    __table_args__ = {'schema': 'query_engine'}

    metric_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.uuid_generate_v4(),
    )

    query_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('query_engine.queries.query_id', onupdate='CASCADE', ondelete='CASCADE'),
        nullable=False,
    )

    agent_execution_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('query_engine.agent_executions.agent_execution_id', onupdate='CASCADE', ondelete='SET NULL'),
        nullable=True,
    )

    response_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('query_engine.responses.response_id', onupdate='CASCADE', ondelete='SET NULL'),
        nullable=True,
    )

    metric_scope: Mapped[str] = mapped_column(String(20), nullable=False)
    provider_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    model_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    execution_duration_ms: Mapped[int] = mapped_column(BigInteger, nullable=False)
    input_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    output_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cost_usd: Mapped[float | None] = mapped_column(Numeric(18, 8), nullable=True)
    cache_hit: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    cache_lookup_ms: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    retrieved_documents: Mapped[int | None] = mapped_column(Integer, nullable=True)
    reranked_documents: Mapped[int | None] = mapped_column(Integer, nullable=True)
    metadata_json: Mapped[dict] = mapped_column('metadata', JSONB, nullable=False, server_default=text("'{}'::jsonb"))

    query: Mapped["Query"] = relationship('Query', back_populates='metrics')
    agent_execution: Mapped["AgentExecution | None"] = relationship('AgentExecution', back_populates='metrics')
    response: Mapped["Response | None"] = relationship('Response', back_populates='metrics')

    def __repr__(self) -> str:
        return f"<Metrics(metric_id={self.metric_id}, query_id={self.query_id}, scope={self.metric_scope})>"
