import io
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from app.services.document_service import DocumentService


class FakeDatabaseService:
    def __init__(self, transaction_session):
        self.transaction_session = transaction_session

    def transaction(self):
        class TransactionContext:
            def __init__(self, session):
                self.session = session

            def __enter__(self):
                return self.session

            def __exit__(self, exc_type, exc_value, traceback):
                return False

        return TransactionContext(self.transaction_session)


class TrackingSession:
    def __init__(self):
        self.added = []
        self.flush_count = 0

    def add(self, entity):
        self.added.append(entity)

    def flush(self):
        self.flush_count += 1


class FakeDocumentRepository:
    def __init__(self, existing_document=None, raise_on_create=False):
        self.existing_document = existing_document
        self.raise_on_create = raise_on_create
        self.created_records = []

    def get_by_checksum(self, checksum_sha256):
        return self.existing_document

    def create_document_from_record(self, record):
        if self.raise_on_create:
            raise RuntimeError("Failed to persist document")
        self.created_records.append(record)
        return MagicMock(document_id=record["document_id"])


class TestDocumentServiceMinIOIntegration(unittest.TestCase):
    def setUp(self) -> None:
        self.fake_minio = MagicMock()
        self.fake_minio.upload = MagicMock()
        self.fake_minio.delete = MagicMock()
        self.fake_minio.connect = MagicMock()
        self.service = DocumentService(
            qdrant_service=MagicMock(),
            document_repository=None,
            database_service=FakeDatabaseService(transaction_session=MagicMock()),
            minio_service=self.fake_minio,
        )

    @patch("app.services.document_service.DocumentRepository")
    def test_persist_document_ingestion_uploads_then_persists(self, mock_repo_class):
        fake_repo = FakeDocumentRepository()
        mock_repo_class.return_value = fake_repo

        record = {
            "document_id": "doc-1",
            "bucket_name": "omnibrain-docs",
            "object_path": "uploads/doc-1/sample.pdf",
            "checksum_sha256": "abc123",
            "document_title": "sample.pdf",
            "original_filename": "sample.pdf",
            "mime_type": "application/pdf",
            "file_extension": "pdf",
            "document_type": "PDF",
            "file_size_bytes": 10,
            "processing_status": "UPLOADED",
            "page_count": 1,
            "chunk_count": 1,
            "image_count": 0,
            "language_code": None,
            "document_description": None,
            "collection_id": None,
            "created_by": "user-1",
        }

        saved_path = MagicMock()
        saved_path.open.return_value.__enter__.return_value = io.BytesIO(b"file content")

        created_new, persisted_document = self.service._persist_document_ingestion(
            record=record,
            chunks=[],
            images=[],
            saved_path=saved_path,
        )

        self.assertTrue(created_new)
        self.fake_minio.upload.assert_called_once()
        self.assertEqual(len(fake_repo.created_records), 1)
        self.assertIsNotNone(persisted_document)

    @patch("app.services.document_service.DocumentRepository")
    def test_persist_document_ingestion_uses_transaction_session_for_all_rows(self, mock_repo_class):
        transaction_session = TrackingSession()
        self.service.database_service = FakeDatabaseService(transaction_session=transaction_session)
        mock_repo_class.return_value = FakeDocumentRepository()

        record = {
            "document_id": "doc-transaction",
            "bucket_name": "omnibrain-docs",
            "object_path": "uploads/doc-transaction/sample.pdf",
            "checksum_sha256": "transaction-checksum",
            "document_title": "sample.pdf",
            "original_filename": "sample.pdf",
            "mime_type": "application/pdf",
            "file_extension": "pdf",
            "document_type": "PDF",
            "file_size_bytes": 10,
            "processing_status": "UPLOADED",
            "page_count": 1,
            "chunk_count": 1,
            "image_count": 0,
            "language_code": None,
            "document_description": None,
            "collection_id": None,
            "created_by": "user-1",
        }
        saved_path = MagicMock()
        saved_path.open.return_value.__enter__.return_value = io.BytesIO(b"file content")
        chunk = SimpleNamespace(chunk_id="chunk-1", text="chunk text", chunk_index=1)

        self.service._persist_document_ingestion(
            record=record,
            chunks=[chunk],
            images=[],
            saved_path=saved_path,
        )

        mock_repo_class.assert_called_once_with(transaction_session)
        self.assertEqual([type(entity).__name__ for entity in transaction_session.added], ["Page", "Chunk"])
        self.assertGreaterEqual(transaction_session.flush_count, 2)

    @patch("app.services.document_service.DocumentRepository")
    def test_persist_document_ingestion_rolls_back_on_db_failure(self, mock_repo_class):
        fake_repo = FakeDocumentRepository(raise_on_create=True)
        mock_repo_class.return_value = fake_repo

        record = {
            "document_id": "doc-2",
            "bucket_name": "omnibrain-docs",
            "object_path": "uploads/doc-2/sample.pdf",
            "checksum_sha256": "abc123",
            "document_title": "sample.pdf",
            "original_filename": "sample.pdf",
            "mime_type": "application/pdf",
            "file_extension": "pdf",
            "document_type": "PDF",
            "file_size_bytes": 10,
            "processing_status": "UPLOADED",
            "page_count": 1,
            "chunk_count": 1,
            "image_count": 0,
            "language_code": None,
            "document_description": None,
            "collection_id": None,
            "created_by": "user-1",
        }

        saved_path = MagicMock()
        saved_path.open.return_value.__enter__.return_value = io.BytesIO(b"file content")

        with self.assertRaises(RuntimeError):
            self.service._persist_document_ingestion(
                record=record,
                chunks=[],
                images=[],
                saved_path=saved_path,
            )

        self.fake_minio.upload.assert_called_once()
        self.fake_minio.delete.assert_called_once_with("omnibrain-docs", "uploads/doc-2/sample.pdf")

    @patch("app.services.document_service.DocumentRepository")
    def test_persist_document_ingestion_reuses_existing_duplicate(self, mock_repo_class):
        existing_document = MagicMock(document_id="existing-doc")
        fake_repo = FakeDocumentRepository(existing_document=existing_document)
        mock_repo_class.return_value = fake_repo

        record = {
            "document_id": "doc-3",
            "bucket_name": "omnibrain-docs",
            "object_path": "uploads/doc-3/sample.pdf",
            "checksum_sha256": "abc123",
            "document_title": "sample.pdf",
            "original_filename": "sample.pdf",
            "mime_type": "application/pdf",
            "file_extension": "pdf",
            "document_type": "PDF",
            "file_size_bytes": 10,
            "processing_status": "UPLOADED",
            "page_count": 1,
            "chunk_count": 1,
            "image_count": 0,
            "language_code": None,
            "document_description": None,
            "collection_id": None,
            "created_by": "user-1",
        }

        saved_path = MagicMock()
        saved_path.open.return_value.__enter__.return_value = io.BytesIO(b"file content")

        created_new, persisted_document = self.service._persist_document_ingestion(
            record=record,
            chunks=[],
            images=[],
            saved_path=saved_path,
        )

        self.assertFalse(created_new)
        self.assertIs(persisted_document, existing_document)
        self.fake_minio.upload.assert_not_called()
