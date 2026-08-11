from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import Numeric
from sqlalchemy import Text
from sqlalchemy import func
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.database.models.query_engine.response import Response


class Citation(Base):
    __tablename__ = 'citations'
    __table_args__ = {'schema': 'query_engine'}

    citation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.uuid_generate_v4(),
    )

    response_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('query_engine.responses.response_id', onupdate='CASCADE', ondelete='CASCADE'),
        nullable=False,
    )

    context_item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('query_engine.context_items.context_item_id', onupdate='CASCADE', ondelete='CASCADE'),
        nullable=False,
    )

    citation_order: Mapped[int] = mapped_column(Integer, nullable=False)
    citation_type: Mapped[str] = mapped_column(Text, nullable=False, server_default=text("'DIRECT'"))
    support_confidence: Mapped[float | None] = mapped_column(Numeric(5, 4), nullable=True)
    is_primary: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('FALSE'))
    quoted_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[dict] = mapped_column('metadata', JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    citation_text: Mapped[str] = mapped_column(Text, nullable=False)

    response: Mapped["Response"] = relationship('Response', back_populates='citations')

    def __repr__(self) -> str:
        return f"<Citation(citation_id={self.citation_id}, response_id={self.response_id})>"
