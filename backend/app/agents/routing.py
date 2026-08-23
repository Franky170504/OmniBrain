from __future__ import annotations

import re

from app.agents.state import AgentRoute


VISION_TERMS = {
    "table",
    "chart",
    "graph",
    "figure",
    "image",
    "picture",
    "diagram",
    "visual",
    "plot",
    "illustration",
    "screenshot",
    "bar chart",
    "line chart",
    "pie chart",
    "scatter plot",
    "flowchart",
}


SEARCH_TERMS = {
    "document",
    "report",
    "pdf",
    "book",
    "paper",
    "article",
    "chapter",
    "section",
    "paragraph",
    "text",
    "summary",
    "summarize",
    "policy",
    "contract",
    "mention",
    "mentioned",
    "according to",
    "find in",
}


SQL_TERMS = {
    "database",
    "sql",
    "historical",
    "history",
    "records",
    "rows",
    "average",
    "avg",
    "total",
    "sum",
    "count",
    "minimum",
    "maximum",
    "highest",
    "lowest",
    "monthly",
    "quarterly",
    "yearly",
    "annual",
    "year over year",
    "year-over-year",
    "yoy",
    "trend over time",
    "aggregate",
    "aggregation",
    "group by",
    "top 5",
    "top 10",
    "top five",
    "top ten",
    "opening price",
    "closing price",
    "close price",
    "historical price",
    "share price",
    "stock price",
    "trading volume",
}


def contains_any(
    question: str,
    terms: set[str],
) -> bool:
    normalized = question.lower()

    return any(
        term in normalized
        for term in terms
    )


def contains_page_reference(
    question: str,
) -> bool:
    return bool(
        re.search(
            r"\bpage\s+\d+\b",
            question,
            flags=re.IGNORECASE,
        )
    )


def contains_year(
    question: str,
) -> bool:
    return bool(
        re.search(
            r"\b(?:19|20)\d{2}\b",
            question,
        )
    )


def is_vision_question(
    question: str,
) -> bool:
    return contains_any(
        question,
        VISION_TERMS,
    )


def is_search_question(
    question: str,
) -> bool:
    return contains_any(
        question,
        SEARCH_TERMS,
    )


def is_sql_question(
    question: str,
) -> bool:
    normalized = question.lower()

    if contains_any(
        question,
        SQL_TERMS,
    ):
        return True

    if contains_year(question):
        analytical_terms = (
            "average",
            "total",
            "sum",
            "count",
            "compare",
            "trend",
            "highest",
            "lowest",
            "increase",
            "decrease",
            "growth",
        )

        if any(
            term in normalized
            for term in analytical_terms
        ):
            return True

    # Preserve old market/ticker behavior.
    has_ticker = bool(
        re.search(
            r"\b[A-Z]{1,5}\b",
            question,
        )
    )

    has_market_metric = any(
        term in normalized
        for term in (
            "open",
            "close",
            "high",
            "low",
            "price",
            "volume",
        )
    )

    return (
        has_ticker
        and has_market_metric
    )


def deterministic_route(
    question: str,
    document_id: str | None,
) -> AgentRoute | None:
    question = question.strip()

    if not question:
        return "end"

    # Visual interpretation has priority over generic
    # document routing.
    if (
        document_id
        and is_vision_question(question)
    ):
        return "vision_agent"

    if (
        document_id
        and contains_page_reference(question)
        and any(
            term in question.lower()
            for term in (
                "show",
                "describe",
                "explain",
                "visual",
                "what is shown",
            )
        )
    ):
        return "vision_agent"

    if is_sql_question(question):
        return "sql_agent"

    if (
        document_id
        and is_search_question(question)
    ):
        return "search_agent"

    return None