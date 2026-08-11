import uuid

from datetime import datetime
from sqlalchemy import DateTime
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.database.base import Base


class AuthRateLimitEvent(Base):
    __tablename__ = 'auth_rate_limit_events'
    __table_args__ = {'schema': 'auth'}

    event_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )

    endpoint: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    request_key: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
