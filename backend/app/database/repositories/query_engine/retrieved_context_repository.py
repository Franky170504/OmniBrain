from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models.query_engine.retrieved_context import RetrievedContext
from app.database.repositories.base_repository import BaseRepository


class RetrievedContextRepository(BaseRepository[RetrievedContext]):
    def __init__(self, session: Session) -> None:
        super().__init__(session=session, model=RetrievedContext)

    def get_by_id(self, retrieval_id: str | bytes) -> RetrievedContext | None:
        return super().get_by_id(retrieval_id)

    def list_for_query(self, query_id: str | bytes) -> list[RetrievedContext]:
        statement = select(self.model).where(self.model.query_id == query_id).order_by(self.model.created_at)
        return list(self.session.scalars(statement).all())
