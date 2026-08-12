from __future__ import annotations

import unittest

from app.agents.routing import deterministic_route


class MidProjectRoutingAudit(unittest.TestCase):
    """Evidence for the mid-project vector-search versus SQL-routing review."""

    def test_document_summary_routes_to_vector_retrieval(self) -> None:
        self.assertEqual(
            deterministic_route("Summarize the uploaded annual report.", "document-123"),
            "document_agent",
        )

    def test_document_table_routes_to_vector_retrieval(self) -> None:
        self.assertEqual(
            deterministic_route("What does the revenue table in this PDF show?", "document-123"),
            "document_agent",
        )

    def test_historical_closing_price_routes_to_sql(self) -> None:
        self.assertEqual(
            deterministic_route("What was AAPL's closing price on 2025-01-10?", "document-123"),
            "sql_agent",
        )

    def test_market_volume_routes_to_sql_without_document(self) -> None:
        self.assertEqual(
            deterministic_route("Show MSFT trading volume on 2025-01-10.", None),
            "sql_agent",
        )


if __name__ == "__main__":
    unittest.main()
