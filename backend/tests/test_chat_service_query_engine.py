import os
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

os.environ.setdefault("QDRANT_API_KEY", "test")
os.environ.setdefault("GROQ_API_KEY", "test")
os.environ.setdefault("LANGSMITH_API_KEY", "test")

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services.chat_service import ChatService


class RecordingQueryEngineService:
    def __init__(self) -> None:
        self.calls = []

    def persist_chat_request(self, **kwargs):
        self.calls.append(kwargs)
        return None


class FakeAgentGraph:
    def invoke(self, **kwargs):
        return {
            "answer": "hello",
            "sources": [{"filename": "doc.pdf"}],
            "route": "document_agent",
            "route_reason": "matched",
        }


class TestChatServiceQueryEngine(unittest.TestCase):
    def test_chat_service_persists_query_engine_lifecycle(self):
        query_engine_service = RecordingQueryEngineService()
        chat_service = ChatService(
            agent_graph=FakeAgentGraph(),
            query_engine_service=query_engine_service,
        )

        result = chat_service.ask(question="hi", user_id="user-1", document_id="doc-1")

        self.assertEqual(result["answer"], "hello")
        self.assertEqual(len(query_engine_service.calls), 1)
        self.assertEqual(query_engine_service.calls[0]["question"], "hi")
        self.assertEqual(query_engine_service.calls[0]["user_id"], "user-1")
        self.assertEqual(query_engine_service.calls[0]["document_id"], "doc-1")


if __name__ == "__main__":
    unittest.main()
