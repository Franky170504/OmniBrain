from __future__ import annotations

import uuid

from datetime import datetime

from sqlalchemy import Boolean
from sqlalchemy import CHAR
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
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


class Response(Base, TimestampMixin):
    __tablename__ = 'responses'
    __table_args__ = {'schema': 'query_engine'}

    response_id: Mapped[uuid.UUID] = mapped_column(
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

    response_text: Mapped[str] = mapped_column(Text, nullable=False)
    response_format: Mapped[str] = mapped_column(String(20), nullable=False, server_default=text("'MARKDOWN'"))
    finish_reason: Mapped[str] = mapped_column(String(30), nullable=False, server_default=text("'STOP'"))
    is_streamed: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('FALSE'))
    stream_completed: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('TRUE'))
    is_final: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('TRUE'))
    response_language: Mapped[str] = mapped_column(CHAR(2), nullable=False, server_default=text("'en'"))
    response_hash: Mapped[str | None] = mapped_column(CHAR(64), nullable=True)
    metadata_json: Mapped[dict] = mapped_column('metadata', JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('1'))

    query: Mapped["Query"] = relationship('Query', back_populates='responses')
    agent_execution: Mapped["AgentExecution | None"] = relationship('AgentExecution', back_populates='responses')
    citations: Mapped[list["Citation"]] = relationship(
        'Citation',
        back_populates='response',
        cascade='all, delete-orphan',
    )
    feedback: Mapped[list["Feedback"]] = relationship(
        'Feedback',
        back_populates='response',
        cascade='all, delete-orphan',
    )
    metrics: Mapped[list["Metrics"]] = relationship(
        'Metrics',
        back_populates='response',
        cascade='all, delete-orphan',
    )

    def __repr__(self) -> str:
        return f"<Response(response_id={self.response_id}, query_id={self.query_id}, is_final={self.is_final})>"
