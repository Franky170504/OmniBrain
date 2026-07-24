from __future__ import annotations

import os
import uuid
from typing import Any

from dotenv import load_dotenv
from qdrant_client import QdrantClient, models

load_dotenv()


class QdrantService:
    def __init__(self) -> None:
        self.url = os.getenv("QDRANT_URL", "http://localhost:6333")
        self.api_key = os.getenv("QDRANT_API_KEY") or None
        self.collection_name = os.getenv(
            "QDRANT_COLLECTION",
            "pdf_chunks",
        )
        self.embedding_model = os.getenv(
            "EMBEDDING_MODEL",
            "BAAI/bge-small-en-v1.5",
        )

        self.client = QdrantClient(
            url=self.url,
            api_key=self.api_key,
            timeout=120,
        )

        self.ensure_collection()

    def ensure_collection(self) -> None:
        if self.client.collection_exists(self.collection_name):
            return

        vector_size = self.client.get_embedding_size(
            self.embedding_model
        )

        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=models.VectorParams(
                size=vector_size,
                distance=models.Distance.COSINE,
            ),
        )

        self.client.create_payload_index(
            collection_name=self.collection_name,
            field_name="document_id",
            field_schema=models.PayloadSchemaType.KEYWORD,
        )

        self.client.create_payload_index(
            collection_name=self.collection_name,
            field_name="user_id",
            field_schema=models.PayloadSchemaType.KEYWORD,
        )

    @staticmethod
    def make_point_id(chunk_id: str) -> str:
        return str(
            uuid.uuid5(
                uuid.NAMESPACE_URL,
                f"omnibrain:{chunk_id}",
            )
        )

    def ingest_chunks(
        self,
        chunks: list[Any],
        *,
        user_id: str,
    ) -> int:
        if not chunks:
            return 0

        ids: list[str] = []
        documents: list[models.Document] = []
        payloads: list[dict[str, Any]] = []

        for chunk in chunks:
            # Supports either dataclass objects or dictionaries.
            if isinstance(chunk, dict):
                record = chunk
            else:
                record = vars(chunk)

            metadata = record.get("metadata") or {}

            chunk_id = str(record["chunk_id"])
            text = str(record["text"]).strip()

            ids.append(self.make_point_id(chunk_id))

            documents.append(
                models.Document(
                    text=text,
                    model=self.embedding_model,
                )
            )

            payloads.append(
                {
                    "chunk_id": chunk_id,
                    "document_id": str(record["document_id"]),
                    "user_id": user_id,
                    "source_file": str(
                        record.get("source_file", "")
                    ),
                    "filename": metadata.get("filename"),
                    "title": metadata.get("title"),
                    "page_start": int(record["page_start"]),
                    "page_end": int(record["page_end"]),
                    "chunk_index": int(record["chunk_index"]),
                    "text": text,
                }
            )

        self.client.upload_collection(
            collection_name=self.collection_name,
            ids=ids,
            vectors=documents,
            payload=payloads,
            batch_size=64,
            parallel=1,
            max_retries=3,
            wait=True,
        )

        return len(ids)

    def search(
        self,
        question: str,
        *,
        user_id: str,
        document_id: str | None = None,
        limit: int = 5,
        score_threshold: float | None = 0.35,
    ) -> list[dict[str, Any]]:
        conditions: list[models.Condition] = [
            models.FieldCondition(
                key="user_id",
                match=models.MatchValue(value=user_id),
            )
        ]

        if document_id:
            conditions.append(
                models.FieldCondition(
                    key="document_id",
                    match=models.MatchValue(
                        value=document_id
                    ),
                )
            )

        response = self.client.query_points(
            collection_name=self.collection_name,
            query=models.Document(
                text=question,
                model=self.embedding_model,
            ),
            query_filter=models.Filter(must=conditions),
            limit=limit,
            score_threshold=score_threshold,
            with_payload=True,
            with_vectors=False,
        )

        results: list[dict[str, Any]] = []

        for point in response.points:
            payload = point.payload or {}

            results.append(
                {
                    "score": float(point.score),
                    "chunk_id": payload.get("chunk_id"),
                    "document_id": payload.get("document_id"),
                    "filename": payload.get("filename"),
                    "page_start": payload.get("page_start"),
                    "page_end": payload.get("page_end"),
                    "text": payload.get("text", ""),
                }
            )

        return results