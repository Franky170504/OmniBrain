import uuid

from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.database.base import Base


class Role(Base):
    __tablename__ = 'roles'
    __table_args__ = {'schema': 'auth'}

    role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )

    role_name: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    users: Mapped[list['User']] = relationship(
        'User',
        back_populates='role',
        cascade='all, delete-orphan',
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return f"<Role(role_id={self.role_id}, role_name={self.role_name})>"
