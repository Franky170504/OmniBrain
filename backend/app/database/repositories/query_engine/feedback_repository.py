from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models.query_engine.feedback import Feedback
from app.database.repositories.base_repository import BaseRepository


class FeedbackRepository(BaseRepository[Feedback]):
    def __init__(self, session: Session) -> None:
        super().__init__(session=session, model=Feedback)

    def get_by_id(self, feedback_id: str | bytes) -> Feedback | None:
        return super().get_by_id(feedback_id)

    def list_for_response(self, response_id: str | bytes) -> list[Feedback]:
        statement = select(self.model).where(self.model.response_id == response_id).order_by(self.model.created_at)
        return list(self.session.scalars(statement).all())
