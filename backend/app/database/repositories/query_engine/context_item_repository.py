from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models.query_engine.context_item import ContextItem
from app.database.repositories.base_repository import BaseRepository


class ContextItemRepository(BaseRepository[ContextItem]):
    def __init__(self, session: Session) -> None:
        super().__init__(session=session, model=ContextItem)

    def get_by_id(self, context_item_id: str | bytes) -> ContextItem | None:
        return super().get_by_id(context_item_id)

    def list_for_retrieval(self, retrieval_id: str | bytes) -> list[ContextItem]:
        statement = select(self.model).where(self.model.retrieval_id == retrieval_id).order_by(self.model.retrieval_rank)
        return list(self.session.scalars(statement).all())
