from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models.query_engine.query import Query
from app.database.repositories.base_repository import BaseRepository


class QueryRepository(BaseRepository[Query]):
    def __init__(self, session: Session) -> None:
        super().__init__(session=session, model=Query)

    def get_by_id(self, query_id: str | bytes) -> Query | None:
        return super().get_by_id(query_id)

    def list_for_turn(self, turn_id: str | bytes) -> list[Query]:
        statement = select(self.model).where(self.model.turn_id == turn_id)
        return list(self.session.scalars(statement).all())
