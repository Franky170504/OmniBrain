from __future__ import annotations

from typing import Any
from uuid import UUID, uuid4

from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer

from app.core.app_config import app_settings


class QdrantService:
    def __init__(self) -> None:
        self.collection_name = app_settings.QDRANT_COLLECTION
        self.embedding_model_name = app_settings.EMBEDDING_MODEL
        self.embedding_dimension = app_settings.EMBEDDING_DIMENSION
        self.client = QdrantClient(
            url=app_settings.QDRANT_URL,
            api_key=app_settings.QDRANT_API_KEY,
        )
        self.embedding_model = SentenceTransformer(self.embedding_model_name)
        self.ensure_collection()

    def ensure_collection(self) -> None:
        if self.client.collection_exists(self.collection_name):
            return
        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=models.VectorParams(
                size=self.embedding_dimension,
                distance=models.Distance.COSINE,
            ),
        )

    def health(self) -> dict[str, Any]:
        try:
            exists = self.client.collection_exists(self.collection_name)
            points_count = None
            if exists:
                info = self.client.get_collection(self.collection_name)
                points_count = int(info.points_count or 0)
            return {
                "status": "healthy",
                "collection_name": self.collection_name,
                "collection_exists": exists,
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

    def _embed(self, texts: list[str]) -> list[list[float]]:
        vectors = self.embedding_model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return [vector.tolist() for vector in vectors]

    def ingest_chunks(
        self,
        chunks: list[dict[str, Any]],
        *,
        user_id: str,
        document_id: str,
        original_filename: str,
    ) -> list[dict[str, Any]]:
        if not chunks:
            return []

        normalized: list[dict[str, Any]] = []
        texts: list[str] = []
        for item in chunks:
            chunk = dict(item)
            text_value = str(chunk.get("text") or chunk.get("chunk_text") or "").strip()
            if not text_value:
                continue

            raw_id = chunk.get("chunk_id") or chunk.get("point_id")
            try:
                point_id = UUID(str(raw_id)) if raw_id else uuid4()
            except ValueError:
                point_id = uuid4()

            chunk["chunk_id"] = str(point_id)
            chunk["point_id"] = str(point_id)
            chunk["vector_point_id"] = str(point_id)
            chunk["text"] = text_value
            chunk["document_id"] = document_id
            chunk["user_id"] = user_id
            chunk["filename"] = original_filename
            normalized.append(chunk)
            texts.append(text_value)

        vectors = self._embed(texts)
        points: list[models.PointStruct] = []
        for chunk, vector in zip(normalized, vectors, strict=True):
            point_id = chunk["point_id"]
            payload = {
                "chunk_id": chunk["chunk_id"],
                "document_id": document_id,
                "user_id": user_id,
                "filename": original_filename,
                "page_number": chunk.get("page_number") or chunk.get("page_start") or chunk.get("page") or 1,
                "page_start": chunk.get("page_start") or chunk.get("page_number") or chunk.get("page") or 1,
                "page_end": chunk.get("page_end") or chunk.get("page_number") or chunk.get("page") or 1,
                "text": chunk["text"],
            }
            points.append(
                models.PointStruct(
                    id=point_id,
                    vector=vector,
                    payload=payload,
                )
            )

        self.client.upsert(
            collection_name=self.collection_name,
            points=points,
            wait=True,
        )
        return normalized

    def search(
        self,
        question: str,
        *,
        user_id: str,
        document_id: str | None,
        limit: int | None = None,
        score_threshold: float | None = None,
    ) -> list[dict[str, Any]]:
        query_vector = self._embed([question])[0]
        must: list[models.FieldCondition] = [
            models.FieldCondition(
                key="user_id",
                match=models.MatchValue(value=user_id),
            )
        ]
        if document_id:
            must.append(
                models.FieldCondition(
                    key="document_id",
                    match=models.MatchValue(value=document_id),
                )
            )

        result = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            query_filter=models.Filter(must=must),
            limit=limit or app_settings.QDRANT_SEARCH_LIMIT,
            score_threshold=(
                score_threshold
                if score_threshold is not None
                else app_settings.QDRANT_SCORE_THRESHOLD
            ),
            with_payload=True,
            with_vectors=False,
        )

        items: list[dict[str, Any]] = []
        for point in result.points:
            payload = dict(point.payload or {})
            items.append(
                {
                    "point_id": str(point.id),
                    "qdrant_point_id": str(point.id),
                    "chunk_id": payload.get("chunk_id"),
                    "document_id": payload.get("document_id"),
                    "filename": payload.get("filename"),
                    "page_number": payload.get("page_number"),
                    "page_start": payload.get("page_start"),
                    "page_end": payload.get("page_end"),
                    "text": payload.get("text") or "",
                    "score": float(point.score),
                    "was_used_in_prompt": True,
                }
            )
        return items

    def delete_document(self, *, user_id: str, document_id: str) -> None:
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=models.FilterSelector(
                filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="user_id",
                            match=models.MatchValue(value=user_id),
                        ),
                        models.FieldCondition(
                            key="document_id",
                            match=models.MatchValue(value=document_id),
                        ),
                    ]
                )
            ),
            wait=True,
        )
