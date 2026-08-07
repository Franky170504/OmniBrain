from __future__ import annotations

import logging
import uuid
from dataclasses import asdict, is_dataclass
from typing import Any,Iterable
from pathlib import Path

from qdrant_client import QdrantClient, models

from config.settings import settings
from config.path_config import *

LOGGER = logging.getLogger("omnibrain.qdrant")

class QdrantService:
    def __init__(self) -> None:
        self.qdrant_url = settings.qdrant_url
        self.qdrant_api_key = settings.qdrant_api_key or None
        self.collection_name = settings.collection_name
        self.embedding_model = settings.embedding_model
        self.embedding_batch_size = settings.embedding_batch_size
        self.client : QdrantClient | None = None
        self.ensure_collection()

    def connect(self) -> QdrantClient:
        if self.client is not None:
            return self.client
        LOGGER.info("Connecting to Qdrant at %s", self.qdrant_url)

        self.client = QdrantClient(url=self.qdrant_url,api_key=self.qdrant_api_key,timeout=120)
        self.client.get_collections()

        LOGGER.info("Connected to Qdrant")
        return self.client

    def close(self) -> None:
        if self.client is not None:
            self.client.close()
            self.client = None

    def get_client(self) -> QdrantClient:
        return self.connect()

    def ensure_collection(self) -> None:
        client = self.get_client()
        if client.collection_exists(self.collection_name):
            LOGGER.info(
                "Using existing Qdrant collection: %s",
                self.collection_name,
            )
            return

        vector_size = self.client.get_embedding_size(self.embedding_model)
        client.create_collection(
            collection_name=self.collection_name,
            vectors_config=models.VectorParams(
                size=vector_size,
                distance=models.Distance.COSINE,
            ),
            on_disk_payload=True
        )
        self._create_payload_indexes()

        LOGGER.info(
            "Created collection %s with vector size %s", self.collection_name,vector_size)

    def _create_payload_indexes(self) -> None:
        client = self.get_client()
        indexes = (
            ("chunk_id", models.PayloadSchemaType.KEYWORD),
            ("document_id", models.PayloadSchemaType.KEYWORD),
            ("user_id", models.PayloadSchemaType.KEYWORD),
            ("filename", models.PayloadSchemaType.KEYWORD),
            ("file_sha256", models.PayloadSchemaType.KEYWORD),
            ("page_start", models.PayloadSchemaType.INTEGER),
            ("page_end", models.PayloadSchemaType.INTEGER),
            ("chunk_index", models.PayloadSchemaType.INTEGER),
        )

        for field_name, schema in indexes:
            try:
                client.create_payload_index(
                    collection_name=self.collection_name,
                    field_name=field_name,
                    field_schema=schema,
                    wait=True,
                )
            except Exception as exc:
                LOGGER.debug("Payload index %s was not created: %s",field_name,exc)

    @staticmethod
    def make_point_id( *, user_id: str, document_id: str, chunk_id: str) -> str:
        source = (f"omnibrain:{user_id}:{document_id}:{chunk_id}")
        return str( uuid.uuid5(uuid.NAMESPACE_URL,source))

    @staticmethod
    def _record_to_dict(chunk: Any) -> dict[str, Any]:
        if isinstance(chunk, dict):
            return chunk

        if is_dataclass(chunk):
            return asdict(chunk)

        if hasattr(chunk, "__dict__"):
            return vars(chunk)

        raise TypeError(
            f"Unsupported chunk type: {type(chunk).__name__}"
        )

    @staticmethod
    def _json_value(value: Any) -> Any:
        if value is None:
            return None

        if isinstance(value, Path):
            return str(value)

        if isinstance(value, dict):
            return {
                str(key): QdrantService._json_value(item)
                for key, item in value.items()
                if item is not None
            }

        if isinstance(value, (list, tuple, set)):
            return [
                QdrantService._json_value(item)
                for item in value
                if item is not None
            ]

        if isinstance(value, (str, int, float, bool)):
            return value

        return str(value)

    def build_payload(self, record: dict[str, Any], *, user_id: str, original_filename: str | None = None) -> dict[str, Any]:
        metadata = record.get("metadata")

        if not isinstance(metadata, dict):
            metadata = {}

        filename = (original_filename or metadata.get("filename")or Path(str(record.get("source_file", ""))).name or None)
        payload = {
            "chunk_id": str(record["chunk_id"]),
            "document_id": str(record["document_id"]),
            "user_id": user_id,
            "source_file": record.get("source_file"),
            "filename": filename,
            "chunk_index": int(record["chunk_index"]),
            "page_start": int(record["page_start"]),
            "page_end": int(record["page_end"]),
            "text": str(record["text"]).strip(),
            "character_count": record.get("character_count"),
            "title": metadata.get("title"),
            "author": metadata.get("author"),
            "subject": metadata.get("subject"),
            "keywords": metadata.get("keywords"),
            "file_sha256": metadata.get("file_sha256"),
            "metadata": metadata,
        }
        return {
            key: self._json_value(value)
            for key, value in payload.items()
            if value is not None
        }

    def ingest_chunks(self,chunks: Iterable[Any], *, user_id: str,original_filename: str | None = None) -> int:
        """Embed and upload chunks produced by your parser."""
        self.ensure_collection()
        records = [self._record_to_dict(chunk)for chunk in chunks]
        if not records:
            return 0
        uploaded = 0
        for start in range(0, len(records), self.embedding_batch_size):
            batch = records[start : start + self.embedding_batch_size]
            ids: list[str] = []
            documents: list[models.Document] = []
            payloads: list[dict[str, Any]] = []
            for record in batch:
                text = str(record.get("text", "")).strip()
                if not text:
                    continue
                chunk_id = str(record["chunk_id"])
                document_id = str(record["document_id"])
                ids.append(
                    self.make_point_id(
                        user_id=user_id,
                        document_id=document_id,
                        chunk_id=chunk_id,
                    )
                )
                documents.append(
                    models.Document(
                        text=text,
                        model=self.embedding_model,
                    )
                )
                payloads.append(
                    self.build_payload(
                        record,
                        user_id=user_id,
                        original_filename=original_filename,
                    )
                )
            if not ids:
                continue

            self.get_client().upload_collection(
                collection_name=self.collection_name,
                ids=ids,
                vectors=documents,
                payload=payloads,
                batch_size=self.embedding_batch_size,
                parallel=1,
                max_retries=3,
                wait=True,
            )
            uploaded += len(ids)
        return uploaded

    def search(self,question: str, *, user_id: str, document_id: str | None = None,limit: int | None = None,score_threshold: float | None = None) -> list[dict[str, Any]]:
        """Search chunks belonging to the current user/document."""
        self.ensure_collection()
        conditions: list[models.Condition] = [models.FieldCondition(key="user_id",match=models.MatchValue(value=user_id))]

        if document_id:
            conditions.append(models.FieldCondition(key="document_id",match=models.MatchValue(value=document_id)))

        response = self.get_client().query_points(
            collection_name=self.collection_name,
            query=models.Document(text=question,model=self.embedding_model),
            query_filter=models.Filter(must=conditions),
            limit=limit or settings.qdrant_search_limit,
            score_threshold=(
                settings.qdrant_score_threshold
                if score_threshold is None
                else score_threshold
            ),
            with_payload=True,
            with_vectors=False,
        )
        results: list[dict[str, Any]] = []
        for point in response.points:
            payload = point.payload or {}
            results.append({
                    "point_id": str(point.id),
                    "score": float(point.score),
                    "chunk_id": payload.get("chunk_id"),
                    "document_id": payload.get("document_id"),
                    "filename": payload.get("filename"),
                    "page_start": payload.get("page_start"),
                    "page_end": payload.get("page_end"),
                    "text": payload.get("text", ""),
                })
        return results

    def delete_document(self, *, user_id: str, document_id: str) -> None:
        self.get_client().delete(
            collection_name=self.collection_name,
            points_selector=models.FilterSelector(
                filter=models.Filter(
                    must=[
                        models.FieldCondition(key="user_id",match=models.MatchValue(value=user_id)),
                        models.FieldCondition(key="document_id",match=models.MatchValue(value=document_id)),
                    ]
                )
            ),
            wait=True,
        )

    def exact_point_count(self) -> int:
        if not self.get_client().collection_exists(self.collection_name):
            return 0
        return self.get_client().count(collection_name=self.collection_name,exact=True).count

    def health(self) -> dict:
        try:
            client = self.get_client()

            collection_exists = client.collection_exists(
                collection_name=self.collection_name
            )

            points_count: int | None = None

            if collection_exists:
                collection = client.get_collection(
                    collection_name=self.collection_name
                )

                points_count = collection.points_count

            return {
                "status": "healthy",
                "collection_name": self.collection_name,
                "collection_exists": collection_exists,
                "points_count": points_count,
                "error": None,
            }

        except Exception as exc:
            return {
                "status": "unhealthy",
                "collection_name": self.collection_name,
                "collection_exists": False,
                "points_count": None,
                "error": str(exc),
            }
            client = self.get_client()
            collections = client.get_collections()
            exists = client.collection_exists(self.collection_name)
            status_value: str | None = None

            if exists:
                info = client.get_collection(self.collection_name)
                status_value = str(info.status)

            return {
                "connected": True,
                "available_collections": [item.name for item in collections.collections],
                "collection": self.collection_name,
                "collection_exists": exists,
                "collection_status": status_value,
                "point_count": self.exact_point_count(),
            }