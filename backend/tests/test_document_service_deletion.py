import unittest
import uuid
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from app.services.document_service import DocumentAuthorizationError, DocumentService


class FakeTransaction:
    def __init__(self, session, commit_error=None):
        self.session = session
        self.commit_error = commit_error

    def __enter__(self):
        return self.session

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None and self.commit_error is not None:
            raise self.commit_error
        return False


class FakeDatabaseService:
    def __init__(self, session, commit_error=None):
        self.session = session
        self.commit_error = commit_error

    def transaction(self):
        return FakeTransaction(self.session, self.commit_error)


class FakeRepository:
    def __init__(self, document):
        self.document = document
        self.deleted = []

    def get_by_id(self, document_id):
        if self.document is not None and self.document.document_id == document_id:
            return self.document
        return None

    def delete(self, document):
        self.deleted.append(document)

    def update(self, document):
        self.document = document
        return document


class TestDocumentServiceDeletion(unittest.TestCase):
    def setUp(self):
        self.document = SimpleNamespace(
            document_id="doc-1",
            owner_user_id=uuid.uuid5(uuid.NAMESPACE_URL, "user-1"),
            bucket_name="omnibrain-docs",
            object_path="uploads/doc-1/sample.pdf",
        )
        self.repository = FakeRepository(self.document)
        self.session = MagicMock()
        self.qdrant = MagicMock()
        self.minio = MagicMock()
        self.minio.object_exists.return_value = True
        self.database = FakeDatabaseService(self.session)
        self.service = DocumentService(
            qdrant_service=self.qdrant,
            database_service=self.database,
            minio_service=self.minio,
        )

    @patch("app.services.document_service.DocumentRepository")
    def test_success_deletes_exact_external_artifacts_and_database_row(self, repository_class):
        repository_class.return_value = self.repository

        self.assertTrue(self.service.delete_document(document_id="doc-1", user_id="user-1"))

        self.qdrant.delete_document.assert_called_once_with(user_id="user-1", document_id="doc-1")
        self.minio.object_exists.assert_called_once_with("omnibrain-docs", "uploads/doc-1/sample.pdf")
        self.minio.delete.assert_called_once_with("omnibrain-docs", "uploads/doc-1/sample.pdf")
        self.assertEqual(self.repository.deleted, [self.document])

    @patch("app.services.document_service.DocumentRepository")
    def test_database_delete_delegates_cascade_to_orm_repository(self, repository_class):
        repository_class.return_value = self.repository

        self.service.delete_document(document_id="doc-1", user_id="user-1")

        self.assertEqual(self.repository.deleted, [self.document])

    @patch("app.services.document_service.DocumentRepository")
    def test_missing_document_is_idempotent_and_does_not_cleanup_unrelated_data(self, repository_class):
        self.repository.document = None
        repository_class.return_value = self.repository

        self.assertFalse(self.service.delete_document(document_id="missing", user_id="user-1"))

        self.qdrant.delete_document.assert_not_called()
        self.minio.delete.assert_not_called()

    @patch("app.services.document_service.DocumentRepository")
    def test_missing_minio_object_is_safe(self, repository_class):
        repository_class.return_value = self.repository
        self.minio.object_exists.return_value = False

        self.assertTrue(self.service.delete_document(document_id="doc-1", user_id="user-1"))

        self.qdrant.delete_document.assert_called_once_with(user_id="user-1", document_id="doc-1")
        self.minio.delete.assert_not_called()
        self.assertEqual(self.repository.deleted, [self.document])

    @patch("app.services.document_service.DocumentRepository")
    def test_non_owner_cannot_delete_document(self, repository_class):
        repository_class.return_value = self.repository

        with self.assertRaises(DocumentAuthorizationError):
            self.service.delete_document(document_id="doc-1", user_id="other-user")

        self.qdrant.delete_document.assert_not_called()
        self.minio.object_exists.assert_not_called()
        self.assertEqual(self.repository.deleted, [])

    @patch("app.services.document_service.DocumentRepository")
    def test_unowned_legacy_document_cannot_be_deleted(self, repository_class):
        self.document.owner_user_id = None
        repository_class.return_value = self.repository

        with self.assertRaises(DocumentAuthorizationError):
            self.service.delete_document(document_id="doc-1", user_id="user-1")

        self.qdrant.delete_document.assert_not_called()
        self.minio.delete.assert_not_called()
        self.assertEqual(self.repository.deleted, [])

    @patch("app.services.document_service.DocumentRepository")
    def test_admin_can_assign_unowned_document(self, repository_class):
        self.document.owner_user_id = None
        repository_class.return_value = self.repository
        target_user = SimpleNamespace(user_id=uuid.uuid5(uuid.NAMESPACE_URL, "target-user"), is_active=True)
        self.session.get.return_value = target_user
        auth_service = MagicMock(is_admin=MagicMock(return_value=True))

        self.assertTrue(self.service.assign_document_owner(
            document_id="doc-1",
            owner_user_id="target-user",
            assigning_user_id="admin-user",
            auth_service=auth_service,
        ))

        self.assertEqual(self.document.owner_user_id, target_user.user_id)
        self.qdrant.delete_document.assert_not_called()
        self.minio.delete.assert_not_called()

    @patch("app.services.document_service.DocumentRepository")
    def test_non_admin_cannot_assign_owner(self, repository_class):
        repository_class.return_value = self.repository
        auth_service = MagicMock(is_admin=MagicMock(return_value=False))

        with self.assertRaises(DocumentAuthorizationError):
            self.service.assign_document_owner(
                document_id="doc-1",
                owner_user_id="target-user",
                assigning_user_id="viewer-user",
                auth_service=auth_service,
            )

        self.assertEqual(self.repository.deleted, [])

    @patch("app.services.document_service.DocumentRepository")
    def test_invalid_owner_is_rejected(self, repository_class):
        self.document.owner_user_id = None
        repository_class.return_value = self.repository
        self.session.get.return_value = None
        auth_service = MagicMock(is_admin=MagicMock(return_value=True))

        with self.assertRaises(ValueError):
            self.service.assign_document_owner(
                document_id="doc-1",
                owner_user_id="missing-user",
                assigning_user_id="admin-user",
                auth_service=auth_service,
            )

        self.assertIsNone(self.document.owner_user_id)

    @patch("app.services.document_service.DocumentRepository")
    def test_nonexistent_document_is_rejected(self, repository_class):
        self.repository.document = None
        repository_class.return_value = self.repository
        auth_service = MagicMock(is_admin=MagicMock(return_value=True))

        self.assertFalse(self.service.assign_document_owner(
            document_id="missing-document",
            owner_user_id="target-user",
            assigning_user_id="admin-user",
            auth_service=auth_service,
        ))

    @patch("app.services.document_service.DocumentRepository")
    def test_qdrant_failure_stops_deletion(self, repository_class):
        repository_class.return_value = self.repository
        self.qdrant.delete_document.side_effect = RuntimeError("qdrant unavailable")

        with self.assertRaisesRegex(RuntimeError, "qdrant unavailable"):
            self.service.delete_document(document_id="doc-1", user_id="user-1")

        self.minio.delete.assert_not_called()
        self.assertEqual(self.repository.deleted, [])

    @patch("app.services.document_service.DocumentRepository")
    def test_minio_failure_stops_database_deletion(self, repository_class):
        repository_class.return_value = self.repository
        self.minio.delete.side_effect = RuntimeError("minio unavailable")

        with self.assertRaisesRegex(RuntimeError, "minio unavailable"):
            self.service.delete_document(document_id="doc-1", user_id="user-1")

        self.qdrant.delete_document.assert_called_once_with(user_id="user-1", document_id="doc-1")
        self.assertEqual(self.repository.deleted, [])

    @patch("app.services.document_service.DocumentRepository")
    def test_database_failure_is_reported_after_external_cleanup(self, repository_class):
        repository_class.return_value = self.repository
        self.service.database_service = FakeDatabaseService(
            self.session,
            commit_error=RuntimeError("database unavailable"),
        )

        with self.assertRaisesRegex(RuntimeError, "database unavailable"):
            self.service.delete_document(document_id="doc-1", user_id="user-1")

        self.qdrant.delete_document.assert_called_once_with(user_id="user-1", document_id="doc-1")
        self.minio.delete.assert_called_once_with("omnibrain-docs", "uploads/doc-1/sample.pdf")
        self.assertEqual(self.repository.deleted, [self.document])

    @patch("app.services.document_service.DocumentRepository")
    def test_repeated_delete_is_safe(self, repository_class):
        repository_class.return_value = self.repository

        self.assertTrue(self.service.delete_document(document_id="doc-1", user_id="user-1"))
        self.repository.document = None
        self.assertFalse(self.service.delete_document(document_id="doc-1", user_id="user-1"))
        self.assertEqual(self.qdrant.delete_document.call_count, 1)
        self.assertEqual(self.minio.delete.call_count, 1)


if __name__ == "__main__":
    unittest.main()