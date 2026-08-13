import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from sqlalchemy import create_engine, text

from app.database.schema_loader import (
    DatabaseSchemaState,
    get_database_schema_state,
    load_database_schema,
    _strip_top_level_transaction_wrappers,
)

DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+psycopg://postgres:postgres@postgres:5432/omnibrain",
)
engine = create_engine(DATABASE_URL, future=True)


class TestSchemaLoader(unittest.TestCase):
    def setUp(self) -> None:
        try:
            with engine.connect() as connection:
                connection.execute(text("DROP SCHEMA IF EXISTS auth CASCADE"))
                connection.execute(text("DROP SCHEMA IF EXISTS knowledge CASCADE"))
                connection.execute(text("DROP SCHEMA IF EXISTS query_engine CASCADE"))
                connection.commit()
        except Exception as exc:
            raise unittest.SkipTest(f"Database connection unavailable: {exc}")

    def test_strip_top_level_transaction_wrappers(self) -> None:
        sql = "\n-- comment\nBEGIN;\nCREATE TABLE test_a(id INT);\nCOMMIT;\n"
        stripped = _strip_top_level_transaction_wrappers(sql)

        self.assertNotIn("BEGIN;", stripped)
        self.assertNotIn("COMMIT;", stripped)
        self.assertIn("CREATE TABLE test_a", stripped)

    def test_strip_top_level_transaction_wrappers_with_block_comment(self) -> None:
        sql = (
            "/*\n"
            "Block comment at the top.\n"
            "*/\n"
            "BEGIN;\n"
            "CREATE TABLE test_a(id INT);\n"
            "COMMIT;\n"
        )
        stripped = _strip_top_level_transaction_wrappers(sql)

        self.assertNotIn("BEGIN;", stripped)
        self.assertNotIn("COMMIT;", stripped)
        self.assertIn("CREATE TABLE test_a", stripped)

    def test_strip_top_level_transaction_wrappers_with_plpgsql(self) -> None:
        sql = (
            "CREATE FUNCTION test_fn()\n"
            "RETURNS void\n"
            "AS $$\n"
            "BEGIN\n"
            "    NULL;\n"
            "END;\n"
            "$$ LANGUAGE plpgsql;\n"
        )
        stripped = _strip_top_level_transaction_wrappers(sql)

        self.assertEqual(sql, stripped)

    def test_strip_top_level_transaction_wrappers_no_wrapper(self) -> None:
        sql = "CREATE TABLE test_a(id INT);\n"
        stripped = _strip_top_level_transaction_wrappers(sql)

        self.assertEqual(sql, stripped)

    def test_strip_top_level_transaction_wrappers_top_level_wrapper(self) -> None:
        sql = (
            "BEGIN;\n"
            "CREATE TABLE test_a(id INT);\n"
            "COMMIT;\n"
        )
        stripped = _strip_top_level_transaction_wrappers(sql)

        self.assertNotIn("BEGIN;", stripped)
        self.assertNotIn("COMMIT;", stripped)
        self.assertIn("CREATE TABLE test_a(id INT);", stripped)
        self.assertEqual(stripped, "CREATE TABLE test_a(id INT);\n")

    def test_empty_database_schema_state(self) -> None:
        state = get_database_schema_state()
        self.assertEqual(state, DatabaseSchemaState.EMPTY)

    def test_partial_database_schema_state(self) -> None:
        with engine.begin() as connection:
            connection.execute(text("CREATE SCHEMA IF NOT EXISTS auth"))
            connection.execute(text("CREATE TABLE IF NOT EXISTS auth.roles (role_id UUID PRIMARY KEY)"))
            connection.execute(text("CREATE TABLE IF NOT EXISTS auth.users (user_id UUID PRIMARY KEY, role_id UUID)"))

        state = get_database_schema_state()
        self.assertEqual(state, DatabaseSchemaState.PARTIAL)

    def test_transactional_bootstrap_rolls_back_on_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            bad_sql_path = Path(tmpdir) / "00_bad.sql"
            bad_sql_path.write_text(
                "CREATE SCHEMA IF NOT EXISTS auth;\n"
                "SET search_path TO auth;\n"
                "CREATE TABLE roles (role_id UUID PRIMARY KEY);\n"
                "CREATE TABLE users (user_id UUID PRIMARY KEY, role_id UUID);\n"
                "SELECT 1 / 0;\n"
            )

            with patch("app.database.schema_loader.get_schema_files", return_value=[bad_sql_path]):
                with self.assertRaises(Exception):
                    load_database_schema()

        state = get_database_schema_state()
        self.assertEqual(state, DatabaseSchemaState.EMPTY)

    def test_load_database_schema_executes_percent_regex_sql(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            sql_path = Path(tmpdir) / "00_percent_regex.sql"
            sql_path.write_text(
                "CREATE TABLE IF NOT EXISTS percent_test (\n"
                "    email TEXT CHECK (\n"
                "        email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'\n"
                "    )\n"
                ");\n"
            )

            with patch("app.database.schema_loader.get_schema_files", return_value=[sql_path]), \
                 patch("app.database.schema_loader._validate_required_schema_tables", return_value=None):
                load_database_schema()

            with engine.connect() as connection:
                connection.execute(text("DROP TABLE IF EXISTS percent_test"))

    def test_load_database_schema_executes_normal_sql(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            sql_path = Path(tmpdir) / "00_normal.sql"
            sql_path.write_text(
                "CREATE TABLE IF NOT EXISTS normal_test (id INT PRIMARY KEY);\n"
            )

            with patch("app.database.schema_loader.get_schema_files", return_value=[sql_path]), \
                 patch("app.database.schema_loader._validate_required_schema_tables", return_value=None):
                load_database_schema()

            with engine.connect() as connection:
                connection.execute(text("DROP TABLE IF EXISTS normal_test"))

    def test_successful_bootstrap_then_skip(self) -> None:
        load_database_schema()
        state = get_database_schema_state()
        self.assertEqual(state, DatabaseSchemaState.COMPLETE)

        load_database_schema()
        state_after = get_database_schema_state()
        self.assertEqual(state_after, DatabaseSchemaState.COMPLETE)


if __name__ == "__main__":
    unittest.main()
