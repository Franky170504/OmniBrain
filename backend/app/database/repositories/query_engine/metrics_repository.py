from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models.query_engine.metrics import Metrics
from app.database.repositories.base_repository import BaseRepository


class MetricsRepository(BaseRepository[Metrics]):
    def __init__(self, session: Session) -> None:
        super().__init__(session=session, model=Metrics)

    def get_by_id(self, metric_id: str | bytes) -> Metrics | None:
        return super().get_by_id(metric_id)

    def list_for_query(self, query_id: str | bytes) -> list[Metrics]:
        statement = select(self.model).where(self.model.query_id == query_id).order_by(self.model.created_at)
        return list(self.session.scalars(statement).all())
