from __future__ import annotations

from app.agents.state import AgentState
from app.services.sql_query_service import (
    SqlQueryService,
)


class SqlAgentNode:
    """
    SQL Agent.

    Handles structured and historical
    PostgreSQL queries.
    """

    def __init__(
        self,
        sql_query_service: SqlQueryService,
    ) -> None:
        self.sql_query_service = (
            sql_query_service
        )

    def __call__(
        self,
        state: AgentState,
    ) -> dict:
        question = (
            state
            .get("question", "")
            .strip()
        )

        if not question:
            return {
                "answer": (
                    "Please enter a structured "
                    "data question."
                ),
                "sources": [],
                "generated_sql": None,
                "sql_rows": [],
                "error": "Missing question",
            }

        try:
            result = (
                self.sql_query_service.answer(
                    question=question
                )
            )

            return {
                "answer": result.get(
                    "answer",
                    "No SQL answer was produced.",
                ),
                "sources": result.get(
                    "sources",
                    [],
                ),
                "generated_sql": (
                    result.get(
                        "generated_sql"
                    )
                ),
                "sql_rows": result.get(
                    "rows",
                    [],
                ),
                "error": result.get(
                    "error"
                ),
            }

        except Exception as exc:
            return {
                "answer": (
                    "Structured-data query failed."
                ),
                "sources": [],
                "generated_sql": None,
                "sql_rows": [],
                "error": str(exc),
            }
