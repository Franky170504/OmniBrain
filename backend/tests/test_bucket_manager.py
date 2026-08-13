import unittest
from unittest.mock import MagicMock, patch

from app.storage.bucket_manager import BucketManager
from app.storage.minio_service import MinioService


class TestBucketManager(unittest.TestCase):
    def setUp(self) -> None:
        mock_service = MagicMock(spec=MinioService)
        self.manager = BucketManager(minio_service=mock_service)
        self.service = mock_service

    def test_ensure_bucket_uses_existing_bucket(self):
        self.service.bucket_exists.return_value = True

        self.manager.ensure_bucket("existing-bucket")

        self.service.connect.assert_not_called()

    @patch("app.storage.bucket_manager.time.sleep", return_value=None)
    def test_ensure_bucket_retries_and_creates(self, sleep_mock):
        self.service.bucket_exists.return_value = False
        client = MagicMock()
        self.service.connect.return_value = client
        client.make_bucket.side_effect = [Exception("fail"), None]

        self.manager.ensure_bucket("new-bucket", retries=2, backoff_seconds=0)

        self.assertEqual(client.make_bucket.call_count, 2)
        sleep_mock.assert_called_once()
