from __future__ import annotations

import json
import re
from typing import Any

from groq import Groq
from sqlalchemy import text

from app.core.app_config import settings
from app.database.database_service import (
    DatabaseService,
)


class SqlQueryService:
    """
    Read-only PostgreSQL query service.

    Converts a natural-language question into
    a SELECT query, validates it, executes it,
    and summarizes the result.
    """

    MAX_ROWS = 200

    # Add your actual historical-data schema here
    # when you create/import it.
    ALLOWED_SCHEMAS = {
        "knowledge",
        "structured",
        "query_engine",
        "public",
    }

    FORBIDDEN_KEYWORDS = {
        "insert",
        "update",
        "delete",
        "drop",
        "alter",
        "truncate",
        "create",
        "grant",
        "revoke",
        "copy",
        "vacuum",
        "comment",
        "merge",
        "call",
        "execute",
        "do",
    }

    def __init__(
        self,
        database_service: DatabaseService | None = None,
    ) -> None:
        if not settings.groq_api_key:
            raise RuntimeError(
                "GROQ_API_KEY is required "
                "for SqlQueryService."
            )

        self.database_service = (
            database_service
            or DatabaseService()
        )

        self.client = Groq(
            api_key=settings.groq_api_key
        )

        self.model = settings.groq_model

    def answer(
        self,
        *,
        question: str,
    ) -> dict[str, Any]:
        schema_context = (
            self._load_schema_context()
        )

        generated_sql = (
            self._generate_sql(
                question=question,
                schema_context=(
                    schema_context
                ),
            )
        )

        safe_sql = self._validate_sql(
            generated_sql
        )

        rows = self._execute_sql(
            safe_sql
        )

        answer = self._summarize(
            question=question,
            sql=safe_sql,
            rows=rows,
        )

        return {
            "answer": answer,
            "generated_sql": safe_sql,
            "rows": rows,
            "sources": [],
            "error": None,
        }

    def _load_schema_context(
        self,
    ) -> str:
        sql = """
        SELECT
            table_schema,
            table_name,
            column_name,
            data_type,
            ordinal_position

        FROM information_schema.columns

        WHERE table_schema = ANY(
            CAST(:schemas AS TEXT[])
        )

        ORDER BY
            table_schema,
            table_name,
            ordinal_position
        """

        schemas = sorted(
            self.ALLOWED_SCHEMAS
        )

        with (
            self.database_service.transaction()
            as session
        ):
            result = session.execute(
                text(sql),
                {
                    "schemas": schemas,
                },
            )

            rows = (
                result
                .mappings()
                .all()
            )

        grouped: dict[
            str,
            list[str],
        ] = {}

        for row in rows:
            full_table_name = (
                f"{row['table_schema']}."
                f"{row['table_name']}"
            )

            column = (
                f"{row['column_name']} "
                f"{row['data_type']}"
            )

            grouped.setdefault(
                full_table_name,
                [],
            ).append(
                column
            )

        schema_lines: list[str] = []

        for (
            table_name,
            columns,
        ) in grouped.items():
            schema_lines.append(
                (
                    f"{table_name}("
                    + ", ".join(columns)
                    + ")"
                )
            )

        return "\n".join(
            schema_lines
        )

    def _generate_sql(
        self,
        *,
        question: str,
        schema_context: str,
    ) -> str:
        prompt = f"""
You are OmniBrain's PostgreSQL query planner.

Generate exactly one read-only PostgreSQL query.

STRICT RULES:

1. SELECT only.

2. WITH ... SELECT is permitted.

3. Never generate INSERT, UPDATE, DELETE,
   CREATE, ALTER, DROP or TRUNCATE.

4. Use only tables and columns appearing
   in the supplied schema.

5. Always use schema-qualified table names.

6. Do not invent tables.

7. Do not invent columns.

8. Prefer SQL aggregation for analytical
   questions.

9. For large raw result queries, return no
   more than {self.MAX_ROWS} rows.

10. Return SQL only.

11. Do not include Markdown code fences.

Database schema:

{schema_context}

User question:

{question}
""".strip()

        response = (
            self.client
            .chat
            .completions
            .create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Generate safe read-only "
                            "PostgreSQL SELECT queries."
                        ),
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
                temperature=0,
                max_tokens=1000,
            )
        )

        generated_sql = (
            response
            .choices[0]
            .message
            .content
        )

        if not generated_sql:
            raise RuntimeError(
                "The SQL model returned "
                "an empty query."
            )

        return self._clean_sql(
            str(generated_sql)
        )

    @staticmethod
    def _clean_sql(
        sql: str,
    ) -> str:
        sql = sql.strip()

        sql = re.sub(
            r"^```sql\s*",
            "",
            sql,
            flags=re.IGNORECASE,
        )

        sql = re.sub(
            r"^```\s*",
            "",
            sql,
        )

        sql = re.sub(
            r"\s*```$",
            "",
            sql,
        )

        return (
            sql
            .strip()
            .rstrip(";")
            .strip()
        )

    def _validate_sql(
        self,
        sql: str,
    ) -> str:
        normalized = re.sub(
            r"\s+",
            " ",
            sql.lower(),
        ).strip()

        if not (
            normalized.startswith(
                "select "
            )
            or normalized.startswith(
                "with "
            )
        ):
            raise ValueError(
                "Only SELECT queries are allowed."
            )

        if ";" in sql:
            raise ValueError(
                "Multiple SQL statements "
                "are not allowed."
            )

        if "--" in sql or "/*" in sql:
            raise ValueError(
                "SQL comments are not allowed."
            )

        for keyword in (
            self.FORBIDDEN_KEYWORDS
        ):
            if re.search(
                rf"\b{re.escape(keyword)}\b",
                normalized,
            ):
                raise ValueError(
                    (
                        "Unsafe SQL keyword "
                        f"detected: {keyword}"
                    )
                )

        referenced_schemas = set(
            re.findall(
                (
                    r"\b"
                    r"([a-zA-Z_]"
                    r"[a-zA-Z0-9_]*)"
                    r"\."
                    r"[a-zA-Z_]"
                    r"[a-zA-Z0-9_]*"
                ),
                sql,
            )
        )

        disallowed = (
            referenced_schemas
            - self.ALLOWED_SCHEMAS
        )

        if disallowed:
            raise ValueError(
                (
                    "SQL references disallowed "
                    f"schemas: {sorted(disallowed)}"
                )
            )

        # Aggregate queries usually return only a few rows,
        # but a hard LIMIT is safe for normal SELECTs.
        if not re.search(
            r"\blimit\s+\d+\b",
            normalized,
        ):
            sql = (
                f"{sql}\n"
                f"LIMIT {self.MAX_ROWS}"
            )

        return sql

    def _execute_sql(
        self,
        sql: str,
    ) -> list[dict[str, Any]]:
        with (
            self.database_service.transaction()
            as session
        ):
            # PostgreSQL transaction-level protection.
            session.execute(
                text(
                    "SET TRANSACTION READ ONLY"
                )
            )

            result = session.execute(
                text(sql)
            )

            rows = [
                dict(row)
                for row
                in result.mappings().all()
            ]

            return rows

    def _summarize(
        self,
        *,
        question: str,
        sql: str,
        rows: list[
            dict[str, Any]
        ],
    ) -> str:
        if not rows:
            return (
                "The PostgreSQL query completed "
                "successfully but returned no "
                "matching rows."
            )

        serialized_rows = json.dumps(
            rows[:100],
            ensure_ascii=False,
            default=str,
        )

        prompt = f"""
You are OmniBrain's structured-data analyst.

Answer the user's question using only the
PostgreSQL result below.

Do not invent values.

Mention important totals, averages, rankings,
comparisons, or trends when present.

If the returned rows do not contain enough
information, say so.

Question:

{question}

SQL:

{sql}

Rows:

{serialized_rows}
""".strip()

        response = (
            self.client
            .chat
            .completions
            .create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Explain structured "
                            "PostgreSQL query results "
                            "accurately."
                        ),
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
                temperature=0.1,
                max_tokens=700,
            )
        )

        answer = (
            response
            .choices[0]
            .message
            .content
        )

        if not answer:
            return (
                "The query succeeded, but "
                "no explanation was produced."
            )

        return str(answer)