from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models.query_engine.response import Response
from app.database.repositories.base_repository import BaseRepository


class ResponseRepository(BaseRepository[Response]):
    def __init__(self, session: Session) -> None:
        super().__init__(session=session, model=Response)

    def get_by_id(self, response_id: str | bytes) -> Response | None:
        return super().get_by_id(response_id)

    def list_for_query(self, query_id: str | bytes) -> list[Response]:
        statement = select(self.model).where(self.model.query_id == query_id).order_by(self.model.created_at)
        return list(self.session.scalars(statement).all())
