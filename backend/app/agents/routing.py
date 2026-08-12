from __future__ import annotations

import re

from app.agents.state import AgentRoute


SQL_INTENT_TERMS = {
    "adjusted close",
    "closing price",
    "close price",
    "historical price",
    "market data",
    "opening price",
    "share price",
    "stock price",
    "trading volume",
}


def is_sql_market_question(question: str) -> bool:
    """Return whether a question requires structured market-data lookup.

    The deterministic pre-router makes the supervisor's database decision
    auditable and prevents document context from overriding a time-series
    request such as a closing price on a known date.
    """
    normalized = question.lower()
    has_market_term = any(term in normalized for term in SQL_INTENT_TERMS)
    has_ticker = bool(re.search(r"\b[A-Z]{1,5}\b", question))
    has_market_metric = any(
        term in normalized
        for term in ("close", "open", "high", "low", "volume", "price")
    )
    return has_market_term or (has_ticker and has_market_metric)


def deterministic_route(question: str, document_id: str | None) -> AgentRoute | None:
    """Resolve intents that have a safe, unambiguous route before the LLM."""
    if not question.strip():
        return "clarify_agent"
    if is_sql_market_question(question):
        return "sql_agent"
    if document_id and any(
        term in question.lower()
        for term in ("document", "report", "pdf", "table", "chapter", "summary")
    ):
        return "document_agent"
    return None
