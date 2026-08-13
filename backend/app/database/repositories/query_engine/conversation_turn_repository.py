from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models.query_engine.conversation_turn import ConversationTurn
from app.database.repositories.base_repository import BaseRepository


class ConversationTurnRepository(BaseRepository[ConversationTurn]):
    def __init__(self, session: Session) -> None:
        super().__init__(session=session, model=ConversationTurn)

    def get_by_id(self, turn_id: str | bytes) -> ConversationTurn | None:
        return super().get_by_id(turn_id)

    def list_for_session(self, session_id: str | bytes) -> list[ConversationTurn]:
        statement = select(self.model).where(self.model.session_id == session_id).order_by(self.model.turn_number)
        return list(self.session.scalars(statement).all())
