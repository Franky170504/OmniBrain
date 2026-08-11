import io
import unittest
from unittest.mock import MagicMock, patch

from app.storage.minio_service import MinioService


class TestMinioService(unittest.TestCase):
    def setUp(self) -> None:
        self.service = MinioService(
            endpoint="localhost:9000",
            access_key="access",
            secret_key="secret",
            secure=False,
        )

    @patch("app.storage.minio_service.Minio")
    def test_connect_initializes_client(self, mock_minio):
        client = MagicMock()
        mock_minio.return_value = client
        client.list_buckets.return_value = []

        result = self.service.connect()

        self.assertIs(result, client)
        mock_minio.assert_called_once_with(
            endpoint="localhost:9000",
            access_key="access",
            secret_key="secret",
            secure=False,
        )
        client.list_buckets.assert_called_once()

    @patch("app.storage.minio_service.Minio")
    def test_upload_calls_put_object(self, mock_minio):
        client = MagicMock()
        mock_minio.return_value = client
        client.list_buckets.return_value = []

        stream = io.BytesIO(b"data")
        self.service.upload("bucket", "object.txt", stream, length=4, content_type="text/plain")

        client.put_object.assert_called_once_with(
            bucket_name="bucket",
            object_name="object.txt",
            data=stream,
            length=4,
            content_type="text/plain",
        )

    @patch("app.storage.minio_service.Minio")
    def test_download_returns_bytes(self, mock_minio):
        client = MagicMock()
        mock_minio.return_value = client
        mock_bucket = MagicMock()
        mock_bucket.read.return_value = b"data"
        client.get_object.return_value = mock_bucket
        client.list_buckets.return_value = []

        result = self.service.download("bucket", "object.txt")

        self.assertEqual(result, b"data")
        client.get_object.assert_called_once_with(bucket_name="bucket", object_name="object.txt")
        mock_bucket.close.assert_called_once()
        mock_bucket.release_conn.assert_called_once()

    @patch("app.storage.minio_service.Minio")
    def test_delete_calls_remove_object(self, mock_minio):
        client = MagicMock()
        mock_minio.return_value = client
        client.list_buckets.return_value = []

        self.service.delete("bucket", "object.txt")

        client.remove_object.assert_called_once_with(bucket_name="bucket", object_name="object.txt")

    @patch("app.storage.minio_service.Minio")
    def test_object_exists_returns_true_when_found(self, mock_minio):
        client = MagicMock()
        mock_minio.return_value = client
        client.list_buckets.return_value = []
        client.stat_object.return_value = MagicMock()

        result = self.service.object_exists("bucket", "object.txt")

        self.assertTrue(result)
        client.stat_object.assert_called_once_with(bucket_name="bucket", object_name="object.txt")

    @patch("app.storage.minio_service.Minio")
    def test_object_exists_returns_false_when_missing(self, mock_minio):
        from minio.error import S3Error

        client = MagicMock()
        mock_minio.return_value = client
        client.list_buckets.return_value = []
        error = S3Error(None, "NoSuchKey", "The specified key does not exist.", None, None, None)
        client.stat_object.side_effect = error

        result = self.service.object_exists("bucket", "object.txt")

        self.assertFalse(result)
