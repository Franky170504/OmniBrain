from __future__ import annotations

from app.agents.state import AgentState
from app.services.market_data_service import MarketDataService


class SqlAgentNode:
    """Answers supported market-data questions through a parameterized SQLite service."""

    def __init__(self, market_data_service: MarketDataService) -> None:
        self.market_data_service = market_data_service

    def __call__(self, state: AgentState) -> dict:
        return self.market_data_service.answer(state.get("question", "").strip())
