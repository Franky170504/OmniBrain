from __future__ import annotations

import json
from collections import defaultdict
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


_JSON = lambda value: json.dumps(value or {})


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def resolve_user(self, user_key: str) -> UUID:
        """Resolve a UUID/email/dev alias into auth.users.user_id.

        Existing frontend values such as ``local-user`` are supported by
        creating a deterministic local account keyed by email.
        """
        user_key = user_key.strip()
        if not user_key:
            raise ValueError("user_id cannot be blank")

        try:
            candidate = UUID(user_key)
        except ValueError:
            candidate = None

        if candidate is not None:
            result = await self.session.execute(
                text(
                    """
                    SELECT user_id
                    FROM auth.users
                    WHERE user_id = :user_id
                      AND is_active = TRUE
                    """
                ),
                {"user_id": candidate},
            )
            row = result.scalar_one_or_none()
            if row is None:
                raise ValueError(f"Unknown or inactive user: {user_key}")
            return row

        if "@" in user_key:
            email = user_key.lower()
            full_name = user_key.split("@", 1)[0].replace(".", " ").title()
        else:
            safe = "".join(ch for ch in user_key.lower() if ch.isalnum() or ch in "-_")
            email = f"{safe or 'local-user'}@omnibrain.local"
            full_name = user_key.replace("-", " ").replace("_", " ").title() or "Local User"

        result = await self.session.execute(
            text("SELECT user_id FROM auth.users WHERE lower(email) = lower(:email)"),
            {"email": email},
        )
        existing = result.scalar_one_or_none()
        if existing is not None:
            return existing

        role_result = await self.session.execute(
            text(
                """
                SELECT role_id
                FROM auth.roles
                WHERE role_name = 'Viewer'
                LIMIT 1
                """
            )
        )
        role_id = role_result.scalar_one_or_none()
        if role_id is None:
            raise RuntimeError("Viewer role is missing. Re-run 02_auth.sql.")

        user_id = uuid4()
        await self.session.execute(
            text(
                """
                INSERT INTO auth.users (
                    user_id, role_id, email, full_name, is_active
                )
                VALUES (
                    :user_id, :role_id, :email, :full_name, TRUE
                )
                """
            ),
            {
                "user_id": user_id,
                "role_id": role_id,
                "email": email,
                "full_name": full_name,
            },
        )
        return user_id


class KnowledgeRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def ensure_default_collection(self) -> UUID:
        domain_result = await self.session.execute(
            text(
                """
                INSERT INTO knowledge.domains (
                    domain_name, description, slug, is_active
                )
                VALUES (
                    'OmniBrain Local',
                    'Default local OmniBrain knowledge domain.',
                    'omnibrain-local',
                    TRUE
                )
                ON CONFLICT (slug)
                DO UPDATE SET is_active = TRUE
                RETURNING domain_id
                """
            )
        )
        domain_id = domain_result.scalar_one()

        collection_result = await self.session.execute(
            text(
                """
                INSERT INTO knowledge.collections (
                    domain_id,
                    collection_name,
                    description,
                    slug,
                    is_active
                )
                VALUES (
                    :domain_id,
                    'Uploaded Documents',
                    'Documents uploaded through OmniBrain.',
                    'uploaded-documents',
                    TRUE
                )
                ON CONFLICT (domain_id, slug)
                DO UPDATE SET is_active = TRUE
                RETURNING collection_id
                """
            ),
            {"domain_id": domain_id},
        )
        return collection_result.scalar_one()

    async def find_document_by_checksum(self, checksum_sha256: str) -> dict[str, Any] | None:
        result = await self.session.execute(
            text(
                """
                SELECT *
                FROM knowledge.documents
                WHERE checksum_sha256 = :checksum
                  AND is_active = TRUE
                LIMIT 1
                """
            ),
            {"checksum": checksum_sha256},
        )
        row = result.mappings().first()
        return dict(row) if row else None

    async def grant_document_access(
        self,
        *,
        document_id: UUID,
        user_id: UUID,
        access_level: str = "OWNER",
    ) -> None:
        await self.session.execute(
            text(
                """
                INSERT INTO knowledge.document_user_access (
                    document_id, user_id, access_level
                )
                VALUES (
                    :document_id, :user_id, :access_level
                )
                ON CONFLICT (document_id, user_id)
                DO UPDATE SET access_level = EXCLUDED.access_level
                """
            ),
            {
                "document_id": document_id,
                "user_id": user_id,
                "access_level": access_level,
            },
        )

    async def user_can_access_document(self, *, user_id: UUID, document_id: UUID) -> bool:
        result = await self.session.execute(
            text(
                """
                SELECT EXISTS (
                    SELECT 1
                    FROM knowledge.document_user_access
                    WHERE user_id = :user_id
                      AND document_id = :document_id
                )
                """
            ),
            {"user_id": user_id, "document_id": document_id},
        )
        return bool(result.scalar_one())

    async def create_document(
        self,
        *,
        document_id: UUID,
        collection_id: UUID,
        document_title: str,
        original_filename: str,
        file_size_bytes: int,
        checksum_sha256: str,
    ) -> None:
        await self.session.execute(
            text(
                """
                INSERT INTO knowledge.documents (
                    document_id,
                    collection_id,
                    document_title,
                    original_filename,
                    file_size_bytes,
                    bucket_name,
                    checksum_sha256,
                    processing_status
                )
                VALUES (
                    :document_id,
                    :collection_id,
                    :document_title,
                    :original_filename,
                    :file_size_bytes,
                    'local-filesystem',
                    :checksum_sha256,
                    'UPLOADED'
                )
                """
            ),
            {
                "document_id": document_id,
                "collection_id": collection_id,
                "document_title": document_title,
                "original_filename": original_filename,
                "file_size_bytes": file_size_bytes,
                "checksum_sha256": checksum_sha256,
            },
        )

    async def update_document_status(
        self,
        *,
        document_id: UUID,
        status: str,
        error: str | None = None,
        page_count: int | None = None,
        chunk_count: int | None = None,
        image_count: int | None = None,
        table_count: int | None = None,
    ) -> None:
        await self.session.execute(
            text(
                """
                UPDATE knowledge.documents
                SET
                    processing_status = :status,
                    processing_error = :error,
                    page_count = COALESCE(:page_count, page_count),
                    chunk_count = COALESCE(:chunk_count, chunk_count),
                    image_count = COALESCE(:image_count, image_count),
                    table_count = COALESCE(:table_count, table_count),
                    last_processed_at = CASE
                        WHEN :status IN ('INDEXED', 'FAILED')
                        THEN CURRENT_TIMESTAMP
                        ELSE last_processed_at
                    END
                WHERE document_id = :document_id
                """
            ),
            {
                "document_id": document_id,
                "status": status,
                "error": error,
                "page_count": page_count,
                "chunk_count": chunk_count,
                "image_count": image_count,
                "table_count": table_count,
            },
        )

    async def replace_page_and_chunk_metadata(
        self,
        *,
        document_id: UUID,
        chunks: list[dict[str, Any]],
        page_count: int,
        embedding_model: str,
        embedding_dimension: int,
    ) -> None:
        """Persist page/chunk metadata for a parsed PDF.

        This method intentionally stores vectors in Qdrant only. PostgreSQL
        stores text + metadata + optional Qdrant point identifiers.
        """
        await self.session.execute(
            text("DELETE FROM knowledge.pages WHERE document_id = :document_id"),
            {"document_id": document_id},
        )

        grouped: dict[int, list[dict[str, Any]]] = defaultdict(list)
        for chunk in chunks:
            page_number = int(
                chunk.get("page_number")
                or chunk.get("page_start")
                or chunk.get("page")
                or 1
            )
            grouped[page_number].append(chunk)

        for page_number in range(1, max(page_count, 1) + 1):
            page_chunks = grouped.get(page_number, [])
            page_text = "\n".join(str(item.get("text") or item.get("chunk_text") or "") for item in page_chunks)
            page_id = uuid4()
            await self.session.execute(
                text(
                    """
                    INSERT INTO knowledge.pages (
                        page_id,
                        document_id,
                        page_number,
                        page_type,
                        ocr_applied,
                        character_count,
                        word_count,
                        chunk_count,
                        image_count,
                        table_count
                    )
                    VALUES (
                        :page_id,
                        :document_id,
                        :page_number,
                        'DOCUMENT',
                        FALSE,
                        :character_count,
                        :word_count,
                        :chunk_count,
                        0,
                        0
                    )
                    """
                ),
                {
                    "page_id": page_id,
                    "document_id": document_id,
                    "page_number": page_number,
                    "character_count": len(page_text),
                    "word_count": len(page_text.split()),
                    "chunk_count": len(page_chunks),
                },
            )

            running_offset = 0
            for chunk_index, chunk in enumerate(page_chunks, start=1):
                chunk_text = str(chunk.get("text") or chunk.get("chunk_text") or "").strip()
                if not chunk_text:
                    continue
                checksum = str(chunk.get("content_checksum") or chunk.get("checksum") or "")
                if len(checksum) != 64:
                    import hashlib
                    checksum = hashlib.sha256(chunk_text.encode("utf-8")).hexdigest()

                raw_point_id = chunk.get("vector_point_id") or chunk.get("point_id")
                try:
                    point_id = UUID(str(raw_point_id)) if raw_point_id else None
                except ValueError:
                    point_id = None

                char_start = int(chunk.get("character_start") or running_offset)
                char_end = int(chunk.get("character_end") or (char_start + len(chunk_text)))
                running_offset = char_end
                token_count = int(chunk.get("token_count") or max(1, len(chunk_text.split())))

                raw_chunk_id = chunk.get("chunk_id")
                try:
                    chunk_id = UUID(str(raw_chunk_id)) if raw_chunk_id else uuid4()
                except ValueError:
                    chunk_id = uuid4()

                await self.session.execute(
                    text(
                        """
                        INSERT INTO knowledge.chunks (
                            chunk_id,
                            page_id,
                            chunk_index,
                            chunk_text,
                            chunk_type,
                            character_start,
                            character_end,
                            token_count,
                            vector_point_id,
                            embedding_model,
                            embedding_dimension,
                            embedding_generated_at,
                            content_checksum,
                            chunk_status,
                            is_active
                        )
                        VALUES (
                            :chunk_id,
                            :page_id,
                            :chunk_index,
                            :chunk_text,
                            'TEXT',
                            :character_start,
                            :character_end,
                            :token_count,
                            :vector_point_id,
                            :embedding_model,
                            :embedding_dimension,
                            CASE WHEN :vector_point_id IS NOT NULL THEN CURRENT_TIMESTAMP ELSE NULL END,
                            :content_checksum,
                            CASE WHEN :vector_point_id IS NOT NULL THEN 'INDEXED' ELSE 'CREATED' END,
                            TRUE
                        )
                        """
                    ),
                    {
                        "chunk_id": chunk_id,
                        "page_id": page_id,
                        "chunk_index": chunk_index,
                        "chunk_text": chunk_text,
                        "character_start": char_start,
                        "character_end": char_end,
                        "token_count": token_count,
                        "vector_point_id": point_id,
                        "embedding_model": embedding_model,
                        "embedding_dimension": embedding_dimension,
                        "content_checksum": checksum,
                    },
                )

    async def list_documents_for_user(self, user_id: UUID) -> list[dict[str, Any]]:
        result = await self.session.execute(
            text(
                """
                SELECT
                    d.document_id,
                    d.document_title,
                    d.original_filename,
                    d.processing_status,
                    d.page_count,
                    d.chunk_count,
                    d.image_count,
                    d.table_count,
                    d.created_at,
                    dua.access_level
                FROM knowledge.documents d
                JOIN knowledge.document_user_access dua
                  ON dua.document_id = d.document_id
                WHERE dua.user_id = :user_id
                  AND d.is_active = TRUE
                ORDER BY d.created_at DESC
                """
            ),
            {"user_id": user_id},
        )
        return [dict(row) for row in result.mappings().all()]


class ChatRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_session(
        self,
        *,
        user_id: UUID,
        selected_document_id: UUID | None,
        title: str,
        metadata: dict[str, Any] | None = None,
    ) -> UUID:
        session_id = uuid4()
        await self.session.execute(
            text(
                """
                INSERT INTO query_engine.chat_sessions (
                    session_id,
                    user_id,
                    selected_document_id,
                    title,
                    metadata
                )
                VALUES (
                    :session_id,
                    :user_id,
                    :selected_document_id,
                    :title,
                    CAST(:metadata AS jsonb)
                )
                """
            ),
            {
                "session_id": session_id,
                "user_id": user_id,
                "selected_document_id": selected_document_id,
                "title": title[:255],
                "metadata": _JSON(metadata),
            },
        )
        return session_id

    async def validate_session_owner(self, *, session_id: UUID, user_id: UUID) -> bool:
        result = await self.session.execute(
            text(
                """
                SELECT EXISTS (
                    SELECT 1
                    FROM query_engine.chat_sessions
                    WHERE session_id = :session_id
                      AND user_id = :user_id
                      AND session_status = 'ACTIVE'
                )
                """
            ),
            {"session_id": session_id, "user_id": user_id},
        )
        return bool(result.scalar_one())

    async def add_message(
        self,
        *,
        session_id: UUID,
        user_id: UUID,
        role: str,
        content: str,
        document_id: UUID | None,
        metadata: dict[str, Any] | None = None,
    ) -> UUID:
        next_result = await self.session.execute(
            text(
                """
                SELECT COALESCE(MAX(sequence_number), 0) + 1
                FROM query_engine.chat_messages
                WHERE session_id = :session_id
                """
            ),
            {"session_id": session_id},
        )
        sequence_number = int(next_result.scalar_one())
        message_id = uuid4()

        await self.session.execute(
            text(
                """
                INSERT INTO query_engine.chat_messages (
                    message_id,
                    session_id,
                    user_id,
                    document_id,
                    role,
                    content,
                    sequence_number,
                    metadata
                )
                VALUES (
                    :message_id,
                    :session_id,
                    :user_id,
                    :document_id,
                    :role,
                    :content,
                    :sequence_number,
                    CAST(:metadata AS jsonb)
                )
                """
            ),
            {
                "message_id": message_id,
                "session_id": session_id,
                "user_id": user_id,
                "document_id": document_id,
                "role": role.upper(),
                "content": content,
                "sequence_number": sequence_number,
                "metadata": _JSON(metadata),
            },
        )

        await self.session.execute(
            text(
                """
                UPDATE query_engine.chat_sessions
                SET last_message_at = CURRENT_TIMESTAMP,
                    selected_document_id = COALESCE(:document_id, selected_document_id)
                WHERE session_id = :session_id
                """
            ),
            {"session_id": session_id, "document_id": document_id},
        )
        return message_id

    async def create_agent_run(
        self,
        *,
        session_id: UUID,
        user_message_id: UUID,
        route: str,
        route_reason: str | None,
        model_name: str,
        latency_ms: int,
        metadata: dict[str, Any] | None = None,
    ) -> UUID:
        agent_run_id = uuid4()
        await self.session.execute(
            text(
                """
                INSERT INTO query_engine.agent_runs (
                    agent_run_id,
                    session_id,
                    user_message_id,
                    route,
                    route_reason,
                    status,
                    model_provider,
                    model_name,
                    started_at,
                    completed_at,
                    latency_ms,
                    metadata
                )
                VALUES (
                    :agent_run_id,
                    :session_id,
                    :user_message_id,
                    :route,
                    :route_reason,
                    'COMPLETED',
                    'groq',
                    :model_name,
                    CURRENT_TIMESTAMP,
                    CURRENT_TIMESTAMP,
                    :latency_ms,
                    CAST(:metadata AS jsonb)
                )
                """
            ),
            {
                "agent_run_id": agent_run_id,
                "session_id": session_id,
                "user_message_id": user_message_id,
                "route": route,
                "route_reason": route_reason,
                "model_name": model_name,
                "latency_ms": latency_ms,
                "metadata": _JSON(metadata),
            },
        )
        return agent_run_id

    async def record_failed_run(
        self,
        *,
        session_id: UUID,
        user_message_id: UUID,
        model_name: str,
        latency_ms: int,
        error: Exception,
    ) -> UUID:
        agent_run_id = uuid4()
        await self.session.execute(
            text(
                """
                INSERT INTO query_engine.agent_runs (
                    agent_run_id,
                    session_id,
                    user_message_id,
                    route,
                    status,
                    model_provider,
                    model_name,
                    started_at,
                    completed_at,
                    latency_ms,
                    error_type,
                    error_message
                )
                VALUES (
                    :agent_run_id,
                    :session_id,
                    :user_message_id,
                    NULL,
                    'FAILED',
                    'groq',
                    :model_name,
                    CURRENT_TIMESTAMP,
                    CURRENT_TIMESTAMP,
                    :latency_ms,
                    :error_type,
                    :error_message
                )
                """
            ),
            {
                "agent_run_id": agent_run_id,
                "session_id": session_id,
                "user_message_id": user_message_id,
                "model_name": model_name,
                "latency_ms": latency_ms,
                "error_type": type(error).__name__,
                "error_message": str(error),
            },
        )
        return agent_run_id

    async def attach_assistant_message(
        self,
        *,
        agent_run_id: UUID,
        assistant_message_id: UUID,
    ) -> None:
        await self.session.execute(
            text(
                """
                UPDATE query_engine.agent_runs
                SET assistant_message_id = :assistant_message_id
                WHERE agent_run_id = :agent_run_id
                """
            ),
            {
                "agent_run_id": agent_run_id,
                "assistant_message_id": assistant_message_id,
            },
        )

    async def create_retrieval_run(
        self,
        *,
        agent_run_id: UUID,
        user_id: UUID,
        document_id: UUID | None,
        query_text: str,
        collection_name: str,
        embedding_model: str,
        search_limit: int,
        score_threshold: float | None,
        context_items: list[dict[str, Any]],
        store_text: bool,
        latency_ms: int | None = None,
    ) -> UUID:
        import hashlib

        retrieval_run_id = uuid4()
        await self.session.execute(
            text(
                """
                INSERT INTO query_engine.retrieval_runs (
                    retrieval_run_id,
                    agent_run_id,
                    user_id,
                    document_id,
                    query_text,
                    collection_name,
                    embedding_model,
                    search_limit,
                    score_threshold,
                    result_count,
                    latency_ms,
                    completed_at
                )
                VALUES (
                    :retrieval_run_id,
                    :agent_run_id,
                    :user_id,
                    :document_id,
                    :query_text,
                    :collection_name,
                    :embedding_model,
                    :search_limit,
                    :score_threshold,
                    :result_count,
                    :latency_ms,
                    CURRENT_TIMESTAMP
                )
                """
            ),
            {
                "retrieval_run_id": retrieval_run_id,
                "agent_run_id": agent_run_id,
                "user_id": user_id,
                "document_id": document_id,
                "query_text": query_text,
                "collection_name": collection_name,
                "embedding_model": embedding_model,
                "search_limit": search_limit,
                "score_threshold": score_threshold,
                "result_count": len(context_items),
                "latency_ms": latency_ms,
            },
        )

        for rank, item in enumerate(context_items, start=1):
            raw_chunk_id = item.get("chunk_id")
            try:
                chunk_id = UUID(str(raw_chunk_id)) if raw_chunk_id else None
            except ValueError:
                chunk_id = None

            raw_point = item.get("point_id") or item.get("qdrant_point_id")
            try:
                point_id = UUID(str(raw_point)) if raw_point else None
            except ValueError:
                point_id = None

            item_document = item.get("document_id")
            try:
                item_document_id = UUID(str(item_document)) if item_document else document_id
            except ValueError:
                item_document_id = document_id

            snapshot = str(item.get("text") or item.get("chunk_text") or "")
            checksum = hashlib.sha256(snapshot.encode("utf-8")).hexdigest() if snapshot else None

            await self.session.execute(
                text(
                    """
                    INSERT INTO query_engine.context_items (
                        retrieval_run_id,
                        rank,
                        qdrant_point_id,
                        chunk_id,
                        document_id,
                        filename,
                        page_start,
                        page_end,
                        score,
                        text_snapshot,
                        text_checksum,
                        token_count,
                        was_used_in_prompt,
                        metadata
                    )
                    VALUES (
                        :retrieval_run_id,
                        :rank,
                        :qdrant_point_id,
                        :chunk_id,
                        :document_id,
                        :filename,
                        :page_start,
                        :page_end,
                        :score,
                        :text_snapshot,
                        :text_checksum,
                        :token_count,
                        :was_used_in_prompt,
                        CAST(:metadata AS jsonb)
                    )
                    """
                ),
                {
                    "retrieval_run_id": retrieval_run_id,
                    "rank": rank,
                    "qdrant_point_id": point_id,
                    "chunk_id": chunk_id,
                    "document_id": item_document_id,
                    "filename": item.get("filename") or item.get("original_filename"),
                    "page_start": item.get("page_start") or item.get("page_number") or item.get("page"),
                    "page_end": item.get("page_end") or item.get("page_number") or item.get("page"),
                    "score": item.get("score"),
                    "text_snapshot": snapshot if store_text else None,
                    "text_checksum": checksum,
                    "token_count": item.get("token_count") or (len(snapshot.split()) if snapshot else None),
                    "was_used_in_prompt": bool(item.get("was_used_in_prompt", True)),
                    "metadata": _JSON(item.get("metadata")),
                },
            )
        return retrieval_run_id

    async def get_messages(self, *, session_id: UUID, user_id: UUID) -> list[dict[str, Any]]:
        result = await self.session.execute(
            text(
                """
                SELECT
                    m.message_id,
                    m.role,
                    m.content,
                    m.document_id,
                    m.sequence_number,
                    m.metadata,
                    m.created_at
                FROM query_engine.chat_messages m
                JOIN query_engine.chat_sessions s
                  ON s.session_id = m.session_id
                WHERE m.session_id = :session_id
                  AND s.user_id = :user_id
                ORDER BY m.sequence_number
                """
            ),
            {"session_id": session_id, "user_id": user_id},
        )
        return [dict(row) for row in result.mappings().all()]

    async def list_sessions(self, *, user_id: UUID) -> list[dict[str, Any]]:
        result = await self.session.execute(
            text(
                """
                SELECT
                    session_id,
                    selected_document_id,
                    title,
                    session_status,
                    created_at,
                    updated_at,
                    last_message_at
                FROM query_engine.chat_sessions
                WHERE user_id = :user_id
                  AND session_status <> 'DELETED'
                ORDER BY COALESCE(last_message_at, created_at) DESC
                """
            ),
            {"user_id": user_id},
        )
        return [dict(row) for row in result.mappings().all()]
