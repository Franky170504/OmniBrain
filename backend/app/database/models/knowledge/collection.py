from __future__ import annotations

import uuid

from sqlalchemy import Boolean
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


class Collection(Base, TimestampMixin):
    __tablename__ = 'collections'
    __table_args__ = {'schema': 'knowledge'}

    collection_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.uuid_generate_v4(),
    )
    domain_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('knowledge.domains.domain_id', onupdate='CASCADE', ondelete='RESTRICT'),
        nullable=False,
    )
    collection_name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    slug: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('TRUE'))

    domain: Mapped['Domain'] = relationship('Domain', back_populates='collections')
    documents: Mapped[list['Document']] = relationship(
        'Document',
        back_populates='collection',
        cascade='all, delete-orphan',
    )

    def __repr__(self) -> str:
        return f"<Collection(collection_id={self.collection_id}, collection_name={self.collection_name})>"
