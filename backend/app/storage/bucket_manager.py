from __future__ import annotations

import logging
import time
from typing import Any

from minio.error import S3Error

from app.storage.minio_service import MinioService

logger = logging.getLogger(__name__)


class BucketManager:
    """Bucket management utilities for storage service."""

    def __init__(self, minio_service: MinioService) -> None:
        self.service = minio_service

    def ensure_bucket(self, bucket_name: str, retries: int = 3, backoff_seconds: int = 2) -> None:
        if self.service.bucket_exists(bucket_name):
            logger.info("Bucket %s already exists", bucket_name)
            return

        last_exception: Exception | None = None
        for attempt in range(1, retries + 1):
            try:
                logger.info("Creating bucket %s (attempt %s)", bucket_name, attempt)
                self.service.connect().make_bucket(bucket_name)
                logger.info("Created bucket %s", bucket_name)
                return
            except Exception as exc:
                logger.warning("Bucket creation attempt %s failed for %s: %s", attempt, bucket_name, exc)
                last_exception = exc
                if attempt < retries:
                    time.sleep(backoff_seconds)
                    continue
                raise

    def list_buckets(self) -> list[dict[str, Any]]:
        client = self.service.connect()
        buckets = client.list_buckets()
        return [
            {"name": bucket.name, "created": bucket.creation_date}
            for bucket in buckets
        ]
