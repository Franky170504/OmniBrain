from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models.query_engine.chat_session import ChatSession
from app.database.repositories.base_repository import BaseRepository


class ChatSessionRepository(BaseRepository[ChatSession]):
    def __init__(self, session: Session) -> None:
        super().__init__(session=session, model=ChatSession)

    def get_by_id(self, session_id: str | bytes) -> ChatSession | None:
        return super().get_by_id(session_id)

    def list_by_user(self, user_id: str | bytes) -> list[ChatSession]:
        statement = select(self.model).where(self.model.user_id == user_id)
        return list(self.session.scalars(statement).all())

    def get_active_sessions(self) -> list[ChatSession]:
        statement = select(self.model).where(self.model.status == 'ACTIVE')
        return list(self.session.scalars(statement).all())
