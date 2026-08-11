from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models.query_engine.citation import Citation
from app.database.repositories.base_repository import BaseRepository


class CitationRepository(BaseRepository[Citation]):
    def __init__(self, session: Session) -> None:
        super().__init__(session=session, model=Citation)

    def get_by_id(self, citation_id: str | bytes) -> Citation | None:
        return super().get_by_id(citation_id)

    def list_for_response(self, response_id: str | bytes) -> list[Citation]:
        statement = select(self.model).where(self.model.response_id == response_id).order_by(self.model.citation_order)
        return list(self.session.scalars(statement).all())
