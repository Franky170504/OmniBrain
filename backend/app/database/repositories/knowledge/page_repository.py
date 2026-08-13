from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models.knowledge.page import Page
from app.database.repositories.base_repository import BaseRepository


class PageRepository(BaseRepository[Page]):
    def __init__(self, session: Session) -> None:
        super().__init__(session=session, model=Page)

    def get_by_id(self, page_id: str) -> Page | None:
        return super().get_by_id(page_id)

    def get_for_document(self, document_id: str) -> list[Page]:
        statement = select(self.model).where(self.model.document_id == document_id)
        return list(self.session.scalars(statement).all())
