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
from sqlalchemy import SmallInteger
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.database.base import Base
from app.database.mixins import TimestampMixin


class AgentExecution(Base, TimestampMixin):
    __tablename__ = 'agent_executions'
    __table_args__ = {'schema': 'query_engine'}

    agent_execution_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.uuid_generate_v4(),
    )

    query_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('query_engine.queries.query_id', onupdate='CASCADE', ondelete='CASCADE'),
        nullable=False,
    )

    parent_execution_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('query_engine.agent_executions.agent_execution_id', onupdate='CASCADE', ondelete='SET NULL'),
        nullable=True,
    )

    agent_name: Mapped[str] = mapped_column(Text, nullable=False)
    agent_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    execution_role: Mapped[str] = mapped_column(String(30), nullable=False)
    execution_status: Mapped[str] = mapped_column(String(30), nullable=False, server_default=text("'PENDING'"))
    execution_sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    tool_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    tool_call_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    input_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    output_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_code: Mapped[str | None] = mapped_column(String(100), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(SmallInteger, nullable=False, server_default=text('0'))
    metadata_json: Mapped[dict] = mapped_column('metadata', JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('1'))

    query: Mapped['Query'] = relationship('Query', back_populates='agent_executions')
    parent_execution: Mapped['AgentExecution | None'] = relationship(
        'AgentExecution',
        remote_side='AgentExecution.agent_execution_id',
        back_populates='child_executions',
    )
    child_executions: Mapped[list['AgentExecution']] = relationship(
        'AgentExecution',
        back_populates='parent_execution',
        cascade='all, delete-orphan',
    )
    responses: Mapped[list['Response']] = relationship(
        'Response',
        back_populates='agent_execution',
    )
    metrics: Mapped[list['Metrics']] = relationship(
        'Metrics',
        back_populates='agent_execution',
    )

    def __repr__(self) -> str:
        return f"<AgentExecution(agent_execution_id={self.agent_execution_id}, query_id={self.query_id}, status={self.execution_status})>"
