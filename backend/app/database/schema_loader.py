from __future__ import annotations

import logging
from enum import Enum
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.engine import Connection

from app.core.app_config import BASE_DIR
from app.database.session import engine

logger = logging.getLogger(__name__)

SCHEMA_DIRECTORY = BASE_DIR / "database" / "schema"

REQUIRED_SCHEMA_TABLES = [
    ("auth", "roles"),
    ("auth", "users"),
    ("auth", "token_sessions"),
    ("auth", "auth_rate_limit_events"),
    ("knowledge", "documents"),
    ("query_engine", "context_item_types"),
    ("query_engine", "context_items"),
    ("query_engine", "citations"),
]


SCHEMA_EXECUTION_ORDER = [
    "00_extensions.sql",
    "01_schemas.sql",
    "02_auth.sql",
    "03_auth_sessions.sql",
    "04_common_functions.sql",
    "05_knowledge.sql",
    "06_structured.sql",
]


class DatabaseSchemaState(str, Enum):
    EMPTY = "EMPTY"
    PARTIAL = "PARTIAL"
    COMPLETE = "COMPLETE"


def _get_existing_and_missing_required_tables() -> tuple[set[tuple[str, str]], list[str]]:
    query = text(
        """
        SELECT table_schema, table_name
        FROM information_schema.tables
        WHERE (table_schema = 'auth' AND table_name IN ('roles', 'users', 'token_sessions', 'auth_rate_limit_events'))
           OR (table_schema = 'knowledge' AND table_name = 'documents')
           OR (table_schema = 'query_engine' AND table_name IN ('context_item_types', 'context_items', 'citations'))
        ORDER BY table_schema, table_name;
        """
    )

    existing_tables: set[tuple[str, str]] = set()
    with engine.connect() as connection:
        for row in connection.execute(query):
            existing_tables.add((row.table_schema, row.table_name))

    missing_tables = [
        f"{schema}.{table}"
        for schema, table in REQUIRED_SCHEMA_TABLES
        if (schema, table) not in existing_tables
    ]

    return existing_tables, missing_tables


def _format_required_table_lists(existing_tables: set[tuple[str, str]]) -> tuple[str, str]:
    existing = ", ".join(
        sorted(f"{schema}.{table}" for schema, table in existing_tables)
    )
    missing = ", ".join(
        sorted(
            f"{schema}.{table}"
            for schema, table in REQUIRED_SCHEMA_TABLES
            if (schema, table) not in existing_tables
        )
    )

    return existing, missing


def get_database_schema_state() -> DatabaseSchemaState:
    """Return whether the PostgreSQL schema is empty, partial, or complete."""

    existing_tables, missing_tables = _get_existing_and_missing_required_tables()

    if not existing_tables:
        logger.info("Database appears empty. No required OmniBrain tables found.")
        return DatabaseSchemaState.EMPTY

    if missing_tables:
        logger.warning(
            "Partial database initialization detected. Existing tables: %s; missing required tables: %s",
            sorted([f"{schema}.{table}" for schema, table in existing_tables]),
            missing_tables,
        )
        return DatabaseSchemaState.PARTIAL

    logger.info(
        "Database appears fully initialized. Required OmniBrain tables present."
    )
    return DatabaseSchemaState.COMPLETE


def database_schema_exists() -> bool:
    """Return True only when the database is fully initialized."""

    return get_database_schema_state() == DatabaseSchemaState.COMPLETE


def get_schema_files() -> list[Path]:
    """Return ordered SQL schema files from the database schema directory."""

    if not SCHEMA_DIRECTORY.exists():
        raise FileNotFoundError(
            f"Database schema directory not found: {SCHEMA_DIRECTORY}"
        )

    available_files = {
        path.name: path
        for path in SCHEMA_DIRECTORY.iterdir()
        if path.is_file() and path.suffix == ".sql"
    }

    ordered_files: list[Path] = []

    for filename in SCHEMA_EXECUTION_ORDER:
        if filename in available_files:
            ordered_files.append(available_files.pop(filename))

    query_engine_dir = SCHEMA_DIRECTORY / "07_query_engine"
    if query_engine_dir.exists() and query_engine_dir.is_dir():
        ordered_files.extend(
            sorted(
                [child for child in query_engine_dir.iterdir() if child.is_file() and child.suffix == ".sql"]
            )
        )

    for remaining_file in sorted(available_files.values(), key=lambda p: p.name):
        ordered_files.append(remaining_file)

    logger.info(
        "Schema execution order: %s",
        [path.name for path in ordered_files],
    )

    return ordered_files


def _strip_top_level_transaction_wrappers(sql: str) -> str:
    """Remove an outer BEGIN/COMMIT wrapper from a schema script if present."""

    lines = sql.splitlines()
    begin_index = None
    in_block_comment = False

    for index, line in enumerate(lines):
        stripped = line.strip()
        if in_block_comment:
            if "*/" in stripped:
                in_block_comment = False
            continue

        if not stripped or stripped.startswith("--"):
            continue

        if stripped.startswith("/*"):
            if "*/" not in stripped:
                in_block_comment = True
            continue

        if stripped.lower() == "begin;":
            begin_index = index
        break

    commit_index = None
    in_block_comment = False
    for index in range(len(lines) - 1, -1, -1):
        stripped = lines[index].strip()
        if in_block_comment:
            if "/*" in stripped:
                in_block_comment = False
            continue

        if not stripped or stripped.startswith("--"):
            continue

        if stripped.endswith("*/"):
            if "/*" not in stripped:
                in_block_comment = True
            continue

        if stripped.lower() == "commit;":
            commit_index = index
        break

    if begin_index is not None and commit_index is not None and commit_index > begin_index:
        logger.debug(
            "Removing top-level BEGIN/COMMIT wrapper from SQL script."
        )
        stripped_lines = [
            line
            for index, line in enumerate(lines)
            if index not in {begin_index, commit_index}
        ]
        return "\n".join(stripped_lines)

    return sql


def _validate_required_schema_tables(connection: Connection) -> None:
    missing_tables: list[str] = []

    for schema_name, table_name in REQUIRED_SCHEMA_TABLES:
        query = text(
            """
            SELECT EXISTS (
                SELECT 1
                FROM information_schema.tables
                WHERE table_schema = :schema_name
                  AND table_name = :table_name
            );
            """
        )
        exists = connection.execute(
            query,
            {
                "schema_name": schema_name,
                "table_name": table_name,
            },
        ).scalar()

        if exists is not True:
            missing_tables.append(f"{schema_name}.{table_name}")

    if missing_tables:
        raise RuntimeError(
            "Database bootstrap failed: missing expected schema tables: "
            + ", ".join(missing_tables)
        )


def load_database_schema() -> None:
    """Execute SQL schema scripts against the configured PostgreSQL database."""

    logger.info("Initializing PostgreSQL schema from %s", SCHEMA_DIRECTORY)

    schema_state = get_database_schema_state()
    if schema_state == DatabaseSchemaState.COMPLETE:
        logger.info(
            "PostgreSQL schema already exists; skipping SQL bootstrap."
        )
        return

    if schema_state == DatabaseSchemaState.PARTIAL:
        existing_tables, missing_tables = _get_existing_and_missing_required_tables()
        existing, missing = _format_required_table_lists(existing_tables)
        logger.warning(
            "PostgreSQL schema is partially initialized. Existing required tables: %s; missing required tables: %s",
            existing,
            missing,
        )
        logger.info("Attempting to apply schema scripts to complete missing tables.")

    schema_files = get_schema_files()
    if not schema_files:
        raise RuntimeError(
            f"No SQL schema files found in {SCHEMA_DIRECTORY}."
        )

    try:
        for schema_file in schema_files:
            logger.info("Applying schema file: %s", schema_file.name)
            sql = schema_file.read_text(encoding="utf-8")
            sql = _strip_top_level_transaction_wrappers(sql)

            try:
                with engine.begin() as connection:
                    connection.execute(text(sql))
            except Exception:
                logger.exception(
                    "Failed to apply SQL schema file %s. Earlier schema files remain committed.",
                    schema_file.name,
                )
                raise

        with engine.begin() as connection:
            _validate_required_schema_tables(connection)

    except Exception:
        logger.exception("Failed to apply SQL schema files.")
        raise

    logger.info("Database schema bootstrap completed successfully.")
