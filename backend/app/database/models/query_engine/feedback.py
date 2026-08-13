from __future__ import annotations

import uuid

from datetime import datetime

from sqlalchemy import Boolean
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
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


class Feedback(Base, TimestampMixin):
    __tablename__ = 'feedback'
    __table_args__ = {'schema': 'query_engine'}

    feedback_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.uuid_generate_v4(),
    )

    response_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('query_engine.responses.response_id', onupdate='CASCADE', ondelete='CASCADE'),
        nullable=False,
    )

    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('auth.users.user_id', onupdate='CASCADE', ondelete='SET NULL'),
        nullable=True,
    )

    feedback_source: Mapped[str] = mapped_column(String(20), nullable=False)
    feedback_type: Mapped[str] = mapped_column(String(30), nullable=False)
    rating: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    is_helpful: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    evaluation_label: Mapped[str | None] = mapped_column(String(30), nullable=True)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[dict] = mapped_column('metadata', JSONB, nullable=False, server_default=text("'{}'::jsonb"))

    response: Mapped['Response'] = relationship('Response', back_populates='feedback')

    def __repr__(self) -> str:
        return f"<Feedback(feedback_id={self.feedback_id}, response_id={self.response_id}, type={self.feedback_type})>"
