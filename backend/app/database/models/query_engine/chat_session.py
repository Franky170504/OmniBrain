from __future__ import annotations
from enum import Enum as PyEnum
import uuid
from sqlalchemy import Enum
from datetime import datetime

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

class SessionStatus(str, PyEnum):
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"
    COMPLETED = "COMPLETED"
    DELETED = "DELETED"

class ChatSession(Base, TimestampMixin):
    __tablename__ = 'chat_sessions'
    __table_args__ = {'schema': 'query_engine'}

    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.uuid_generate_v4(),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('auth.users.user_id', onupdate='CASCADE', ondelete='CASCADE'),
        nullable=False,
    )

    domain_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('knowledge.domains.domain_id', onupdate='CASCADE', ondelete='SET NULL'),
        nullable=True,
    )

    session_title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    active_model: Mapped[str | None] = mapped_column(String(100), nullable=True)
    system_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)

    status: Mapped[SessionStatus] = mapped_column(
        Enum(
             SessionStatus,
             name="session_status_enum",
             schema="query_engine",
             native_enum=True,
             create_type=False,
            ),
         nullable=False,
         server_default=text("'ACTIVE'::query_engine.session_status_enum"),
    )

    total_turns: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    total_queries: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    metadata_json: Mapped[dict] = mapped_column('metadata', JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    last_activity_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, server_default=func.now())
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    conversation_turns: Mapped[list["ConversationTurn"]] = relationship(
        'ConversationTurn',
        back_populates='session',
        cascade='all, delete-orphan',
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return f"<ChatSession(session_id={self.session_id}, user_id={self.user_id}, title={self.session_title})>"
