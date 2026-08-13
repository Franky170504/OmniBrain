import os
import sys
import unittest
import uuid
from pathlib import Path

os.environ.setdefault("QDRANT_API_KEY", "test")
os.environ.setdefault("GROQ_API_KEY", "test")
os.environ.setdefault("LANGSMITH_API_KEY", "test")

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services.query_engine_service import QueryEngineService


class FakeExecuteResult:
    def __init__(self, value):
        self._value = value

    def scalar_one_or_none(self):
        return self._value


class RecordingSession:
    def __init__(self) -> None:
        self.added = []

    def execute(self, statement):
        query_text = str(statement).lower()
        if "auth.users" in query_text or "users" in query_text:
            return FakeExecuteResult(None)
        if "auth.roles" in query_text or "roles" in query_text:
            return FakeExecuteResult(uuid.uuid4())
        if "context_item_types" in query_text:
            return FakeExecuteResult(1)
        return FakeExecuteResult(None)

    def add(self, entity):
        self.added.append(entity)

    def add_all(self, entities):
        self.added.extend(entities)

    def get(self, model, primary_key):
        return None

    def merge(self, entity):
        return entity

    def flush(self):
        return None

    def commit(self):
        return None

    def rollback(self):
        return None

    def close(self):
        return None


class FakeDatabaseService:
    def __init__(self) -> None:
        self.session = RecordingSession()

    def transaction(self):
        class _Tx:
            def __enter__(self):
                return self.session

            def __exit__(self, exc_type, exc, tb):
                return False

            session = None

        tx = _Tx()
        tx.session = self.session
        return tx


class TestQueryEngineService(unittest.TestCase):
    def test_persist_chat_request_creates_root_records(self):
        database_service = FakeDatabaseService()
        service = QueryEngineService(database_service=database_service)

        service.persist_chat_request(
            question="What is this?",
            user_id="user-1",
            document_id="doc-1",
            result={"answer": "A response", "sources": []},
        )

        self.assertEqual(len(database_service.session.added), 5)
        self.assertEqual(database_service.session.added[0].__class__.__name__, "User")
        self.assertEqual(database_service.session.added[1].__class__.__name__, "ChatSession")
        self.assertEqual(database_service.session.added[2].__class__.__name__, "ConversationTurn")
        self.assertEqual(database_service.session.added[3].__class__.__name__, "Query")
        self.assertEqual(database_service.session.added[4].__class__.__name__, "Response")


if __name__ == "__main__":
    unittest.main()
