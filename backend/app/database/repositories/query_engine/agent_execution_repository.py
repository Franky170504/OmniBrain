from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models.query_engine.agent_execution import AgentExecution
from app.database.repositories.base_repository import BaseRepository


class AgentExecutionRepository(BaseRepository[AgentExecution]):
    def __init__(self, session: Session) -> None:
        super().__init__(session=session, model=AgentExecution)

    def get_by_id(self, agent_execution_id: str | bytes) -> AgentExecution | None:
        return super().get_by_id(agent_execution_id)

    def list_for_query(self, query_id: str | bytes) -> list[AgentExecution]:
        statement = select(self.model).where(self.model.query_id == query_id).order_by(self.model.execution_sequence)
        return list(self.session.scalars(statement).all())
