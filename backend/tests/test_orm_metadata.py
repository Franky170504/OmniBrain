import re
import sys
import unittest
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.database.base import Base
import app.database.models  # noqa: F401


class TestOrmMetadata(unittest.TestCase):
    def test_expected_orm_tables_are_registered(self):
        expected_tables = sorted([
            'auth.roles',
            'auth.users',
            'knowledge.chunks',
            'knowledge.collections',
            'knowledge.documents',
            'knowledge.domains',
            'knowledge.images',
            'knowledge.pages',
            'knowledge.tables',
            'query_engine.agent_executions',
            'query_engine.chat_sessions',
            'query_engine.citations',
            'query_engine.context_item_types',
            'query_engine.context_items',
            'query_engine.conversation_turns',
            'query_engine.feedback',
            'query_engine.metrics',
            'query_engine.queries',
            'query_engine.query_intents',
            'query_engine.query_priorities',
            'query_engine.query_statuses',
            'query_engine.responses',
            'query_engine.retrieval_strategies',
            'query_engine.retrieved_context',
            'structured.data_sources',
            'structured.dataset_columns',
            'structured.dataset_refresh_history',
            'structured.dataset_relationship_columns',
            'structured.dataset_relationships',
            'structured.dataset_statistics',
            'structured.dataset_tables',
            'structured.datasets',
            'structured.column_statistics',
            'structured.resource_tags',
            'structured.table_statistics',
            'structured.tags',
        ])

        actual_tables = sorted(
            f"{table.schema}.{table.name}"
            for table in Base.metadata.tables.values()
        )

        self.assertEqual(
            expected_tables,
            actual_tables,
            "ORM metadata must include all expected ORM tables",
        )


if __name__ == "__main__":
    unittest.main()
