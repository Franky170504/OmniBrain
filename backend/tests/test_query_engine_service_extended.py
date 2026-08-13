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


class TestQueryEngineServiceExtended(unittest.TestCase):
    def test_persist_chat_request_creates_retrieval_and_citation_records(self):
        database_service = FakeDatabaseService()
        service = QueryEngineService(database_service=database_service)

        service.persist_chat_request(
            question="What is this?",
            user_id="user-1",
            document_id="doc-1",
            result={
                "answer": "A response",
                "sources": [{"chunk_id": "chunk-1", "filename": "doc.pdf", "page_start": 1, "page_end": 2, "score": 0.99}],
            },
        )

        added_types = [entity.__class__.__name__ for entity in database_service.session.added]
        self.assertIn("RetrievedContext", added_types)
        self.assertIn("Citation", added_types)

        citation_entities = [entity for entity in database_service.session.added if entity.__class__.__name__ == "Citation"]
        self.assertTrue(citation_entities)
        self.assertEqual(citation_entities[0].citation_order, 1)

    def test_persist_chat_request_creates_feedback_and_metrics_records(self):
        database_service = FakeDatabaseService()
        service = QueryEngineService(database_service=database_service)

        service.persist_chat_request(
            question="What is this?",
            user_id="user-1",
            document_id="doc-1",
            result={
                "answer": "A response",
                "feedback": {
                    "source": "USER",
                    "type": "thumbs_up",
                    "rating": 5,
                    "is_helpful": True,
                    "comment": "Great",
                    "metadata": {"origin": "ui"},
                },
                "metrics": {
                    "scope": "request",
                    "provider_name": "groq",
                    "model_name": "llama-3.1",
                    "execution_duration_ms": 120,
                    "input_tokens": 100,
                    "output_tokens": 50,
                    "cost_usd": 0.02,
                    "retrieved_documents": 3,
                    "reranked_documents": 2,
                    "metadata": {"latency_bucket": "fast"},
                },
            },
        )

        added_types = [entity.__class__.__name__ for entity in database_service.session.added]
        self.assertIn("Feedback", added_types)
        self.assertIn("Metrics", added_types)


if __name__ == "__main__":
    unittest.main()
