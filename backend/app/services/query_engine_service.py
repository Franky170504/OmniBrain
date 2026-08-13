from __future__ import annotations

import logging
import uuid
from typing import Any

from sqlalchemy import select

from app.database.database_service import DatabaseService
from app.database.models.authentication.role import Role
from app.database.models.authentication.user import User
from app.database.models.query_engine.chat_session import ChatSession
from app.database.models.query_engine.citation import Citation
from app.database.models.query_engine.context_item import ContextItem
from app.database.models.query_engine.context_item_type import ContextItemType
from app.database.models.query_engine.conversation_turn import ConversationTurn
from app.database.models.query_engine.feedback import Feedback
from app.database.models.query_engine.metrics import Metrics
from app.database.models.query_engine.query import Query
from app.database.models.query_engine.response import Response
from app.database.models.query_engine.retrieved_context import RetrievedContext
from app.database.repositories.query_engine.chat_session_repository import ChatSessionRepository
from app.database.repositories.query_engine.citation_repository import CitationRepository
from app.database.repositories.query_engine.context_item_repository import ContextItemRepository
from app.database.repositories.query_engine.conversation_turn_repository import ConversationTurnRepository
from app.database.repositories.query_engine.feedback_repository import FeedbackRepository
from app.database.repositories.query_engine.metrics_repository import MetricsRepository
from app.database.repositories.query_engine.query_repository import QueryRepository
from app.database.repositories.query_engine.response_repository import ResponseRepository
from app.database.repositories.query_engine.retrieved_context_repository import RetrievedContextRepository


LOGGER = logging.getLogger("omnibrain.query_engine")

class QueryEngineService:
    def __init__(self, database_service: DatabaseService | None = None) -> None:
        self.database_service = database_service or DatabaseService()

    def persist_chat_request(self, *, question: str, user_id: str, document_id: str | None, result: dict[str, Any]) -> None:
        with self.database_service.transaction() as session:
            chat_session_repo = ChatSessionRepository(session)
            conversation_turn_repo = ConversationTurnRepository(session)
            query_repo = QueryRepository(session)
            response_repo = ResponseRepository(session)
            retrieved_context_repo = RetrievedContextRepository(session)
            citation_repo = CitationRepository(session)
            feedback_repo = FeedbackRepository(session)
            metrics_repo = MetricsRepository(session)

            resolved_user_id = uuid.UUID(user_id) if self._is_uuid(user_id) else uuid.uuid5(uuid.NAMESPACE_URL, user_id)
            user_row = session.execute(
                select(User.user_id).where(User.user_id == resolved_user_id)
            ).scalar_one_or_none()

            if user_row is None:
                role_id = self._resolve_role_id(session)

                email = f"{str(resolved_user_id)}@local.omnibrain"
                session.add(
                    User(
                        user_id=resolved_user_id,
                        role_id=role_id,
                        email=email,
                        full_name=user_id or "OmniBrain Local User",
                        is_active=True,
                    )
                )
                session.flush()

            chat_session = ChatSession(
                session_id=uuid.uuid4(),
                user_id=resolved_user_id,
                session_title="Chat Session",
                description="Persisted from chat request",
                status="ACTIVE",
                metadata_json={},
            )
            chat_session_repo.create(chat_session)

            conversation_turn = ConversationTurn(
                turn_id=uuid.uuid4(),
                session_id=chat_session.session_id,
                turn_number=1,
                sender_type="USER",
                message=question,
                metadata_json={},
            )
            conversation_turn_repo.create(conversation_turn)

            query = Query(
                query_id=uuid.uuid4(),
                turn_id=conversation_turn.turn_id,
                intent_id=1,
                status_id=1,
                strategy_id=1,
                priority_id=1,
                original_query=question,
                metadata_json={},
            )
            query_repo.create(query)

            response = Response(
                response_id=uuid.uuid4(),
                query_id=query.query_id,
                response_text=result.get("answer", ""),
                metadata_json={"document_id": document_id, "sources": result.get("sources", [])},
            )
            response_repo.create(response)

            sources = result.get("sources", []) or []
            if sources:
                retrieved_context = RetrievedContext(
                    retrieval_id=uuid.uuid4(),
                    query_id=query.query_id,
                    retriever_name="qdrant",
                    retriever_version="1.0",
                    search_namespace="documents",
                    retrieval_source="LIVE",
                    candidate_count=len(sources),
                    returned_count=len(sources),
                    metadata_json={"document_id": document_id},
                )
                retrieved_context_repo.create(retrieved_context)

                context_item_repo = ContextItemRepository(session)
                for index, source in enumerate(sources, start=1):
                    chunk_id = source.get("chunk_id")
                    image_id = source.get("image_id")
                    table_entity_id = source.get("table_id")
                    datasource_id = source.get("datasource_id")

                    if not any((chunk_id, image_id, table_entity_id, datasource_id)):
                        LOGGER.warning(
                            "Skipping source without retrievable evidence: %s",
                            source,
                        )
                        continue

                    item_type_code = "CHUNK"
                    if table_entity_id is not None:
                        item_type_code = "TABLE"
                    elif image_id is not None:
                        item_type_code = "IMAGE"
                    elif datasource_id is not None:
                        item_type_code = "STRUCTURED"

                    context_item_type_id = session.execute(
                        select(ContextItemType.item_type_id).where(ContextItemType.item_type_code == item_type_code)
                    ).scalar_one_or_none()

                    if context_item_type_id is None:
                        context_item_type_id = self._resolve_context_item_type_id(
                            session=session,
                            item_type_code=item_type_code,
                        )

                    context_item = ContextItem(
                        context_item_id=uuid.uuid4(),
                        retrieval_id=retrieved_context.retrieval_id,
                        item_type_id=context_item_type_id,
                        chunk_id=chunk_id,
                        image_id=image_id,
                        table_entity_id=table_entity_id,
                        datasource_id=datasource_id,
                        retrieval_rank=index,
                        relevance_score=source.get("score") or 0.0,
                        page_number=source.get("page_start"),
                        citation_label=source.get("filename"),
                        highlight_json=source.get("highlight_json"),
                        metadata_json=source,
                    )
                    context_item_repo.create(context_item)

                    citation = Citation(
                        citation_id=uuid.uuid4(),
                        response_id=response.response_id,
                        context_item_id=context_item.context_item_id,
                        citation_order=index,
                        citation_type="DIRECT",
                        is_primary=index == 1,
                        citation_text=source.get("filename") or f"Source {index}",
                        metadata_json={},
                    )
                    citation_repo.create(citation)

            feedback_payload = result.get("feedback") or {}
            if feedback_payload:
                feedback = Feedback(
                    feedback_id=uuid.uuid4(),
                    response_id=response.response_id,
                    user_id=uuid.UUID(user_id) if self._is_uuid(user_id) else None,
                    feedback_source=str(feedback_payload.get("source") or "UNKNOWN"),
                    feedback_type=str(feedback_payload.get("type") or "UNKNOWN"),
                    rating=feedback_payload.get("rating"),
                    is_helpful=feedback_payload.get("is_helpful"),
                    evaluation_label=feedback_payload.get("evaluation_label"),
                    comment=feedback_payload.get("comment"),
                    metadata_json={
                        **(feedback_payload.get("metadata") or {}),
                        "document_id": document_id,
                    },
                )
                feedback_repo.create(feedback)

            metrics_payload = result.get("metrics") or {}
            if metrics_payload:
                metrics = Metrics(
                    metric_id=uuid.uuid4(),
                    query_id=query.query_id,
                    response_id=response.response_id,
                    metric_scope=str(metrics_payload.get("scope") or "request"),
                    provider_name=metrics_payload.get("provider_name"),
                    model_name=metrics_payload.get("model_name"),
                    execution_duration_ms=int(metrics_payload.get("execution_duration_ms") or 0),
                    input_tokens=metrics_payload.get("input_tokens"),
                    output_tokens=metrics_payload.get("output_tokens"),
                    cost_usd=float(metrics_payload.get("cost_usd")) if metrics_payload.get("cost_usd") is not None else None,
                    cache_hit=metrics_payload.get("cache_hit"),
                    cache_lookup_ms=metrics_payload.get("cache_lookup_ms"),
                    retrieved_documents=metrics_payload.get("retrieved_documents"),
                    reranked_documents=metrics_payload.get("reranked_documents"),
                    metadata_json={
                        **(metrics_payload.get("metadata") or {}),
                        "document_id": document_id,
                    },
                )
                metrics_repo.create(metrics)

            session.flush()

    def _resolve_role_id(self, session) -> uuid.UUID:
        role_id = session.execute(
            select(Role.role_id).where(Role.role_name == "Viewer")
        ).scalar_one_or_none()
        if role_id is not None:
            return role_id

        role_id = session.execute(
            select(Role.role_id).where(Role.role_name == "Admin")
        ).scalar_one_or_none()
        if role_id is not None:
            return role_id

        raise RuntimeError(
            "Required auth roles are missing from the database. "
            "Ensure the SQL schema bootstrap has been applied."
        )

    def _resolve_context_item_type_id(
        self,
        session,
        item_type_code: str,
    ) -> int:
        context_item_type_id = session.execute(
            select(ContextItemType.item_type_id).where(
                ContextItemType.item_type_code == item_type_code
            )
        ).scalar_one_or_none()

        if context_item_type_id is not None:
            return context_item_type_id

        raise RuntimeError(
            f"Required lookup row missing for query_engine.context_item_types: "
            f"{item_type_code}. Ensure the SQL schema bootstrap has been applied."
        )

    @staticmethod
    def _is_uuid(value: str) -> bool:
        try:
            uuid.UUID(value)
            return True
        except ValueError:
            return False
