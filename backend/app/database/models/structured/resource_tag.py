from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import func
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.database.base import Base
from app.database.mixins import TimestampMixin


class ResourceTag(Base, TimestampMixin):
    __tablename__ = 'resource_tags'
    __table_args__ = {'schema': 'structured'}

    resource_tag_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text('gen_random_uuid()'),
    )
    tag_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('structured.tags.tag_id', ondelete='RESTRICT'),
        nullable=False,
    )
    resource_type: Mapped[str] = mapped_column(String(30), nullable=False)
    resource_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    assigned_by: Mapped[str | None] = mapped_column(String(100), nullable=True)
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text('CURRENT_TIMESTAMP'),
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text('TRUE'),
    )

    tag: Mapped['Tag'] = relationship('Tag', back_populates='resource_tags')

    def __repr__(self) -> str:
        return f"<ResourceTag(resource_tag_id={self.resource_tag_id}, resource_type={self.resource_type})>"
