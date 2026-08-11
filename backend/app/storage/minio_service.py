from __future__ import annotations

import logging
from typing import BinaryIO

from minio import Minio
from minio.error import S3Error

logger = logging.getLogger(__name__)


class MinioService:
    """Storage service for MinIO operations."""

    def __init__(
        self,
        endpoint: str,
        access_key: str | None,
        secret_key: str | None,
        secure: bool = False,
    ) -> None:
        self.endpoint = endpoint
        self.access_key = access_key
        self.secret_key = secret_key
        self.secure = secure
        self.client: Minio | None = None

    def connect(self) -> Minio:
        if self.client is not None:
            return self.client

        if not self.endpoint:
            raise ValueError("MINIO_ENDPOINT must be configured.")

        if not self.access_key or not self.secret_key:
            raise ValueError("MINIO_ACCESS_KEY and MINIO_SECRET_KEY must be configured.")

        logger.info("Initializing MinIO client for %s", self.endpoint)
        self.client = Minio(
            endpoint=self.endpoint,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=self.secure,
        )

        self.client.list_buckets()
        logger.info("Connected to MinIO at %s", self.endpoint)
        return self.client

    def bucket_exists(self, bucket_name: str) -> bool:
        client = self.connect()
        try:
            return client.bucket_exists(bucket_name)
        except S3Error:
            logger.exception("Unable to verify bucket existence: %s", bucket_name)
            raise

    def upload(
        self,
        bucket_name: str,
        object_name: str,
        data: BinaryIO,
        length: int | None = None,
        content_type: str | None = None,
    ) -> None:
        client = self.connect()
        logger.info("Uploading %s to bucket %s", object_name, bucket_name)
        try:
            if length is None:
                current = data.tell()
                data.seek(0, 2)
                end = data.tell()
                data.seek(current)
                length = end - current

            client.put_object(
                bucket_name=bucket_name,
                object_name=object_name,
                data=data,
                length=length,
                content_type=content_type,
            )
            logger.info("Upload succeeded for %s in bucket %s", object_name, bucket_name)
        except S3Error:
            logger.exception("Failed to upload %s to bucket %s", object_name, bucket_name)
            raise

    def download(self, bucket_name: str, object_name: str) -> bytes:
        client = self.connect()
        logger.info("Downloading %s from bucket %s", object_name, bucket_name)
        try:
            response = client.get_object(bucket_name=bucket_name, object_name=object_name)
            data = response.read()
            response.close()
            response.release_conn()
            logger.info("Downloaded %s from bucket %s", object_name, bucket_name)
            return data
        except S3Error:
            logger.exception("Failed to download %s from bucket %s", object_name, bucket_name)
            raise

    def delete(self, bucket_name: str, object_name: str) -> None:
        client = self.connect()
        logger.info("Deleting %s from bucket %s", object_name, bucket_name)
        try:
            client.remove_object(bucket_name=bucket_name, object_name=object_name)
            logger.info("Deleted %s from bucket %s", object_name, bucket_name)
        except S3Error:
            logger.exception("Failed to delete %s from bucket %s", object_name, bucket_name)
            raise

    def object_exists(self, bucket_name: str, object_name: str) -> bool:
        client = self.connect()
        logger.info("Checking existence of %s in bucket %s", object_name, bucket_name)
        try:
            client.stat_object(bucket_name=bucket_name, object_name=object_name)
            return True
        except S3Error as exc:
            if exc.code in {"NoSuchKey", "NoSuchBucket", "NotFound"}:
                return False
            logger.exception("Failed to check existence for %s in bucket %s", object_name, bucket_name)
            raise

    def stat_object(self, bucket_name: str, object_name: str):
        client = self.connect()
        logger.info("Reading metadata for %s in bucket %s", object_name, bucket_name)
        try:
            return client.stat_object(bucket_name=bucket_name, object_name=object_name)
        except S3Error:
            logger.exception("Failed to stat object %s in bucket %s", object_name, bucket_name)
            raise

    def presigned_get_object(self, bucket_name: str, object_name: str, expires: int = 3600) -> str:
        client = self.connect()
        logger.info("Generating presigned URL for %s in bucket %s", object_name, bucket_name)
        try:
            return client.presigned_get_object(bucket_name=bucket_name, object_name=object_name, expires=expires)
        except S3Error:
            logger.exception("Failed to generate presigned URL for %s in bucket %s", object_name, bucket_name)
            raise

    def health(self) -> dict[str, str | bool | None]:
        try:
            self.connect()
            return {
                "status": "healthy",
                "endpoint": self.endpoint,
                "error": None,
            }
        except Exception as exc:
            return {
                "status": "unhealthy",
                "endpoint": self.endpoint,
                "error": str(exc),
            }
