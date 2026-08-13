import os
import sys
import unittest
import uuid
from pathlib import Path
from types import SimpleNamespace

os.environ.setdefault("QDRANT_API_KEY", "test")
os.environ.setdefault("GROQ_API_KEY", "test")
os.environ.setdefault("LANGSMITH_API_KEY", "test")

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services.document_service import DocumentService


class FakeRepository:
    def __init__(self) -> None:
        self.documents = {}
        self.history = []

    def get_by_id(self, document_id):
        return self.documents.get(document_id)

    def get_by_checksum(self, checksum_sha256: str):
        for document in self.documents.values():
            if getattr(document, "checksum_sha256", None) == checksum_sha256:
                return document
        return None

    def create_document_from_record(self, record):
        document = self.documents.get(record["document_id"])
        if document is None:
            document = FakeDocument(record["document_id"], chunk_count=record.get("chunk_count", 0))
            self.documents[document.document_id] = document
        document.processing_status = record.get("processing_status", "UPLOADED")
        document.bucket_name = record.get("bucket_name", document.bucket_name)
        document.object_path = record.get("object_path", document.object_path)
        document.chunk_count = record.get("chunk_count", document.chunk_count)
        document.checksum_sha256 = record.get("checksum_sha256", getattr(document, "checksum_sha256", ""))
        return document

    def update(self, document):
        self.documents[document.document_id] = document
        self.history.append(document.processing_status)


class FakeDocument:
    def __init__(self, document_id: str, *, chunk_count: int = 0) -> None:
        self.document_id = document_id
        self.processing_status = "UPLOADED"
        self.processing_error = None
        self.chunk_count = chunk_count
        self.bucket_name = "omnibrain-docs"
        self.object_path = f"uploads/{document_id}/sample.pdf"


class FakeMinioService:
    def object_exists(self, bucket_name: str, object_path: str) -> bool:
        return True


class FakeUploadFile:
    filename = "sample.pdf"

    async def read(self, size):
        return b""

    async def close(self):
        return None


class TestDocumentServiceLifecycle(unittest.TestCase):
    def test_new_document_starts_uploaded_and_valid_transitions_follow_sequence(self):
        repo = FakeRepository()
        repo.documents["doc-123"] = FakeDocument("doc-123")

        async def fake_save_upload(self, file):
            return Path("/tmp/sample.pdf"), "sample.pdf"

        def fake_persist(*, record, chunks, images, saved_path):
            document = repo.documents.get(record["document_id"])
            if document is None:
                document = FakeDocument(record["document_id"], chunk_count=len(chunks))
                repo.documents[document.document_id] = document
            else:
                document.chunk_count = len(chunks)
            return True, document

        def fake_parse_pdf(*, pdf_path, output_path, chunk_size, overlap):
            parsed_document = {
                "document_id": "doc-123",
                "page_count": 1,
                "chunk_count": 1,
                "sha256": "abc",
                "metadata": {},
            }
            return parsed_document, [{"text": "chunk"}], []

        class FakeQdrantService:
            def ingest_chunks(self, chunks, **kwargs):
                return len(chunks)

            def verify_document_index(self, *, user_id, document_id, expected_count):
                return expected_count == 1

        service = DocumentService(
            qdrant_service=FakeQdrantService(),
            document_repository=repo,
            database_service=None,
            minio_service=FakeMinioService(),
        )
        service._ensure_default_collection = lambda: uuid.UUID(int=0)

        service.save_upload = fake_save_upload.__get__(service, DocumentService)
        service._persist_document_ingestion = fake_persist

        import app.services.document_service as document_service_module

        document_service_module.parse_pdf = fake_parse_pdf

        import asyncio

        asyncio.run(service.process_upload(file=FakeUploadFile(), user_id="user-1"))

        self.assertEqual(
            repo.history,
            ["PARSING", "CHUNKING", "EMBEDDING", "INDEXED"],
        )

        document = repo.documents["doc-123"]
        self.assertEqual(document.processing_status, "INDEXED")

    def test_uploaded_to_embedding_is_rejected(self):
        class FakeQdrantService:
            pass

        service = DocumentService(
            qdrant_service=FakeQdrantService(),
            document_repository=FakeRepository(),
            database_service=None,
            minio_service=FakeMinioService(),
        )

        record = FakeDocument("doc-999")
        service._update_status(record, "PARSING", None, FakeRepository())
        with self.assertRaises(RuntimeError):
            service._update_status(record, "EMBEDDING", None, FakeRepository())

    def test_valid_status_sequence_is_preserved(self):
        repo = FakeRepository()
        doc = FakeDocument("doc-10")
        repo.documents[doc.document_id] = doc

        service = DocumentService(
            qdrant_service=None,
            document_repository=repo,
            database_service=None,
            minio_service=FakeMinioService(),
        )

        service._update_status(doc, "PARSING", None, repo)
        service._update_status(doc, "CHUNKING", None, repo)
        service._update_status(doc, "EMBEDDING", None, repo)
        service._update_status(doc, "INDEXED", None, repo)

        self.assertEqual(doc.processing_status, "INDEXED")

    def test_process_upload_rejects_indexed_when_qdrant_count_is_too_low(self):
        repo = FakeRepository()
        repo.documents["doc-456"] = FakeDocument("doc-456")

        async def fake_save_upload(self, file):
            return Path("/tmp/sample.pdf"), "sample.pdf"

        def fake_persist(*, record, chunks, images, saved_path):
            document = repo.documents.get(record["document_id"])
            if document is None:
                document = FakeDocument(record["document_id"], chunk_count=len(chunks))
                repo.documents[document.document_id] = document
            else:
                document.chunk_count = len(chunks)
            return True, document

        def fake_parse_pdf(*, pdf_path, output_path, chunk_size, overlap):
            parsed_document = {
                "document_id": "doc-456",
                "page_count": 1,
                "chunk_count": 2,
                "sha256": "abc123",
                "metadata": {},
            }
            return parsed_document, [{"text": "a"}, {"text": "b"}], []

        class FakeQdrantService:
            def ingest_chunks(self, chunks, **kwargs):
                return 1

            def verify_document_index(self, *, user_id, document_id, expected_count):
                return False

        service = DocumentService(
            qdrant_service=FakeQdrantService(),
            document_repository=repo,
            database_service=None,
            minio_service=FakeMinioService(),
        )
        service._ensure_default_collection = lambda: uuid.UUID(int=0)
        service.save_upload = fake_save_upload.__get__(service, DocumentService)
        service._persist_document_ingestion = fake_persist

        import app.services.document_service as document_service_module
        document_service_module.parse_pdf = fake_parse_pdf

        with self.assertRaises(RuntimeError):
            import asyncio
            asyncio.run(service.process_upload(file=FakeUploadFile(), user_id="user-1"))

        self.assertEqual(repo.history[-1], "FAILED")

    def test_process_upload_rejects_indexed_when_qdrant_returns_zero_for_expected_chunks(self):
        repo = FakeRepository()
        repo.documents["doc-789"] = FakeDocument("doc-789")

        async def fake_save_upload(self, file):
            return Path("/tmp/sample.pdf"), "sample.pdf"

        def fake_persist(*, record, chunks, images, saved_path):
            document = repo.documents.get(record["document_id"])
            if document is None:
                document = FakeDocument(record["document_id"], chunk_count=len(chunks))
                repo.documents[document.document_id] = document
            else:
                document.chunk_count = len(chunks)
            return True, document

        def fake_parse_pdf(*, pdf_path, output_path, chunk_size, overlap):
            parsed_document = {
                "document_id": "doc-789",
                "page_count": 1,
                "chunk_count": 3,
                "sha256": "def456",
                "metadata": {},
            }
            return parsed_document, [{"text": "a"}, {"text": "b"}, {"text": "c"}], []

        class FakeQdrantService:
            def ingest_chunks(self, chunks, **kwargs):
                return 0

            def verify_document_index(self, *, user_id, document_id, expected_count):
                return False

        service = DocumentService(
            qdrant_service=FakeQdrantService(),
            document_repository=repo,
            database_service=None,
            minio_service=FakeMinioService(),
        )
        service._ensure_default_collection = lambda: uuid.UUID(int=0)
        service.save_upload = fake_save_upload.__get__(service, DocumentService)
        service._persist_document_ingestion = fake_persist

        import app.services.document_service as document_service_module
        document_service_module.parse_pdf = fake_parse_pdf

        with self.assertRaises(RuntimeError):
            import asyncio
            asyncio.run(service.process_upload(file=FakeUploadFile(), user_id="user-1"))

        self.assertEqual(repo.history[-1], "FAILED")

    def test_process_upload_marks_failed_when_qdrant_ingest_raises(self):
        repo = FakeRepository()
        repo.documents["doc-000"] = FakeDocument("doc-000")

        async def fake_save_upload(self, file):
            return Path("/tmp/sample.pdf"), "sample.pdf"

        def fake_persist(*, record, chunks, images, saved_path):
            document = repo.documents.get(record["document_id"])
            if document is None:
                document = FakeDocument(record["document_id"], chunk_count=len(chunks))
                repo.documents[document.document_id] = document
            else:
                document.chunk_count = len(chunks)
            return True, document

        def fake_parse_pdf(*, pdf_path, output_path, chunk_size, overlap):
            parsed_document = {
                "document_id": "doc-000",
                "page_count": 1,
                "chunk_count": 1,
                "sha256": "zzz",
                "metadata": {},
            }
            return parsed_document, [{"text": "chunk"}], []

        class FakeQdrantService:
            def ingest_chunks(self, chunks, **kwargs):
                raise RuntimeError("Qdrant is down")

        service = DocumentService(
            qdrant_service=FakeQdrantService(),
            document_repository=repo,
            database_service=None,
            minio_service=FakeMinioService(),
        )
        service._ensure_default_collection = lambda: uuid.UUID(int=0)
        service.save_upload = fake_save_upload.__get__(service, DocumentService)
        service._persist_document_ingestion = fake_persist

        import app.services.document_service as document_service_module
        document_service_module.parse_pdf = fake_parse_pdf

        with self.assertRaises(RuntimeError):
            import asyncio
            asyncio.run(service.process_upload(file=FakeUploadFile(), user_id="user-1"))

        self.assertEqual(repo.history[-1], "FAILED")


if __name__ == "__main__":
    unittest.main()
