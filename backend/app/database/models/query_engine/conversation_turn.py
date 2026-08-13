from __future__ import annotations

import uuid

from datetime import datetime

from sqlalchemy import Boolean
from sqlalchemy import CHAR
from sqlalchemy import Computed
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


class ConversationTurn(Base, TimestampMixin):
    __tablename__ = 'conversation_turns'
    __table_args__ = {'schema': 'query_engine'}

    turn_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.uuid_generate_v4(),
    )

    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('query_engine.chat_sessions.session_id', onupdate='CASCADE', ondelete='CASCADE'),
        nullable=False,
    )

    parent_turn_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('query_engine.conversation_turns.turn_id', onupdate='CASCADE', ondelete='SET NULL'),
        nullable=True,
    )

    turn_number: Mapped[int] = mapped_column(Integer, nullable=False)
    sender_type: Mapped[str] = mapped_column(String(20), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    model_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    prompt_tokens: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    completion_tokens: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    total_tokens: Mapped[int | None] = mapped_column(
        Integer,
        Computed('prompt_tokens + completion_tokens', persisted=True),
        nullable=True,
    )
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_edited: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('FALSE'))
    is_regenerated: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('FALSE'))
    metadata_json: Mapped[dict] = mapped_column('metadata', JSONB, nullable=False, server_default=text("'{}'::jsonb"))

    session: Mapped["ChatSession"] = relationship(
        'ChatSession',
        back_populates='conversation_turns',
    )

    parent_turn: Mapped["ConversationTurn | None"] = relationship(
        'ConversationTurn',
        remote_side='ConversationTurn.turn_id',
        back_populates='child_turns',
    )

    child_turns: Mapped[list["ConversationTurn"]] = relationship(
        'ConversationTurn',
        back_populates='parent_turn',
        cascade='all, delete-orphan',
    )

    queries: Mapped[list["Query"]] = relationship(
        'Query',
        back_populates='turn',
        cascade='all, delete-orphan',
    )

    def __repr__(self) -> str:
        return f"<ConversationTurn(turn_id={self.turn_id}, session_id={self.session_id}, turn_number={self.turn_number})>"
