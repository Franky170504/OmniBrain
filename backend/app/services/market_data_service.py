from __future__ import annotations

import re
import sqlite3
from pathlib import Path
from typing import Any


class MarketDataService:
    """Read-only interface over the local market-data demonstration database."""

    def __init__(self, database_path: Path | None = None) -> None:
        root = Path(__file__).resolve().parents[3]
        self.database_path = database_path or root / "data" / "market_data.db"
        self._ensure_database()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _ensure_database(self) -> None:
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS market_prices (
                    ticker TEXT NOT NULL,
                    trade_date TEXT NOT NULL,
                    open REAL NOT NULL,
                    high REAL NOT NULL,
                    low REAL NOT NULL,
                    close REAL NOT NULL,
                    volume INTEGER NOT NULL,
                    PRIMARY KEY (ticker, trade_date)
                )
                """
            )
            count = connection.execute("SELECT COUNT(*) FROM market_prices").fetchone()[0]
            if count:
                return
            connection.executemany(
                "INSERT INTO market_prices VALUES (?, ?, ?, ?, ?, ?, ?)",
                [
                    ("AAPL", "2025-01-08", 241.92, 243.71, 240.05, 242.70, 37628900),
                    ("AAPL", "2025-01-09", 243.98, 245.15, 241.50, 242.43, 40234800),
                    ("AAPL", "2025-01-10", 240.01, 240.74, 233.00, 236.85, 61710900),
                    ("MSFT", "2025-01-08", 423.46, 426.44, 421.60, 424.56, 18813200),
                    ("MSFT", "2025-01-09", 425.18, 427.20, 421.60, 424.56, 19760900),
                    ("MSFT", "2025-01-10", 421.65, 422.00, 414.64, 418.95, 26197500),
                ],
            )

    def answer(self, question: str) -> dict[str, Any]:
        ticker = self._ticker_from(question)
        if not ticker:
            return self._unsupported("Specify a supported ticker, for example AAPL or MSFT.")
        date_match = re.search(r"\b(20\d{2}-\d{2}-\d{2})\b", question)
        normalized = question.lower()
        with self._connect() as connection:
            if date_match:
                row = connection.execute(
                    "SELECT * FROM market_prices WHERE ticker = ? AND trade_date = ?",
                    (ticker, date_match.group(1)),
                ).fetchone()
                if not row:
                    return self._unsupported(f"No seeded market data exists for {ticker} on {date_match.group(1)}.")
                return self._single_day_answer(dict(row), normalized)
            if "average" in normalized:
                row = connection.execute(
                    "SELECT AVG(close) AS average_close FROM market_prices WHERE ticker = ?",
                    (ticker,),
                ).fetchone()
                return self._result(
                    f"The average closing price for {ticker} in the local sample is ${row['average_close']:.2f}.",
                    {"ticker": ticker, "average_close": round(row["average_close"], 2)},
                )
            rows = connection.execute(
                "SELECT * FROM market_prices WHERE ticker = ? ORDER BY trade_date",
                (ticker,),
            ).fetchall()
        return self._result(
            f"The local market-data sample contains {len(rows)} trading days for {ticker}. Ask for a date, close, open, high, low, volume, or average.",
            {"ticker": ticker, "rows": len(rows)},
        )

    @staticmethod
    def _ticker_from(question: str) -> str | None:
        supported = {"AAPL", "MSFT"}
        for value in re.findall(r"\b[A-Z]{1,5}\b", question):
            if value in supported:
                return value
        return None

    def _single_day_answer(self, row: dict[str, Any], question: str) -> dict[str, Any]:
        field = next((name for name in ("open", "high", "low", "close", "volume") if name in question), "close")
        value = row[field]
        display = f"{value:,}" if field == "volume" else f"${value:.2f}"
        return self._result(
            f"{row['ticker']} {field} on {row['trade_date']} was {display}.",
            row,
        )

    @staticmethod
    def _result(answer: str, record: dict[str, Any]) -> dict[str, Any]:
        return {
            "answer": answer,
            "sources": [{"filename": "market_data.db", "page_start": None, "page_end": None, "score": None, "record": record}],
            "error": None,
        }

    @staticmethod
    def _unsupported(answer: str) -> dict[str, Any]:
        return {"answer": answer, "sources": [], "error": "Unsupported SQL market-data query"}
