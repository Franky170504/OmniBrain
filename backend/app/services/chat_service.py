from __future__ import annotations

from time import perf_counter
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.graph import OmniBrainGraph
from app.core.app_config import app_settings
from app.db.repositories import ChatRepository, KnowledgeRepository, UserRepository


class ChatService:
    def __init__(self, agent_graph: OmniBrainGraph) -> None:
        self.agent_graph = agent_graph

    async def ask(
        self,
        *,
        question: str,
        user_id: str,
        document_id: UUID | None,
        session_id: UUID | None,
        session: AsyncSession,
    ) -> dict:
        question = question.strip()
        if not question:
            raise ValueError("question cannot be blank")

        users = UserRepository(session)
        knowledge = KnowledgeRepository(session)
        chats = ChatRepository(session)
        db_user_id = await users.resolve_user(user_id)

        if document_id is not None:
            allowed = await knowledge.user_can_access_document(
                user_id=db_user_id,
                document_id=document_id,
            )
            if not allowed:
                raise PermissionError("User does not have access to the selected document.")

        if session_id is None:
            session_id = await chats.create_session(
                user_id=db_user_id,
                selected_document_id=document_id,
                title=question[:100],
                metadata={"client_user_key": user_id},
            )
        else:
            valid = await chats.validate_session_owner(
                session_id=session_id,
                user_id=db_user_id,
            )
            if not valid:
                raise PermissionError("Chat session does not belong to this user.")

        user_message_id = await chats.add_message(
            session_id=session_id,
            user_id=db_user_id,
            role="USER",
            content=question,
            document_id=document_id,
        )
        await session.commit()

        started = perf_counter()
        try:
            result = await self.agent_graph.ainvoke(
                question=question,
                user_id=user_id,
                document_id=str(document_id) if document_id else None,
            )
            latency_ms = int((perf_counter() - started) * 1000)

            route = str(result.get("route") or "clarify_agent")
            route_reason = result.get("route_reason")
            answer = str(result.get("answer") or "No answer was generated.")
            sources = list(result.get("sources") or [])
            context_items = list(result.get("context_items") or [])

            agent_run_id = await chats.create_agent_run(
                session_id=session_id,
                user_message_id=user_message_id,
                route=route,
                route_reason=route_reason,
                model_name=app_settings.GROQ_MODEL,
                latency_ms=latency_ms,
                metadata={"source_count": len(sources)},
            )

            if route == "document_agent":
                await chats.create_retrieval_run(
                    agent_run_id=agent_run_id,
                    user_id=db_user_id,
                    document_id=document_id,
                    query_text=question,
                    collection_name=app_settings.QDRANT_COLLECTION,
                    embedding_model=app_settings.EMBEDDING_MODEL,
                    search_limit=app_settings.QDRANT_SEARCH_LIMIT,
                    score_threshold=app_settings.QDRANT_SCORE_THRESHOLD,
                    context_items=context_items,
                    store_text=app_settings.STORE_RETRIEVED_TEXT,
                    latency_ms=result.get("retrieval_latency_ms"),
                )

            assistant_message_id = await chats.add_message(
                session_id=session_id,
                user_id=db_user_id,
                role="ASSISTANT",
                content=answer,
                document_id=document_id,
                metadata={
                    "route": route,
                    "route_reason": route_reason,
                    "sources": sources,
                },
            )
            await chats.attach_assistant_message(
                agent_run_id=agent_run_id,
                assistant_message_id=assistant_message_id,
            )
            await session.commit()

            return {
                "session_id": session_id,
                "message_id": assistant_message_id,
                "answer": answer,
                "sources": sources,
                "route": route,
                "route_reason": route_reason,
                "error": result.get("error"),
            }
        except Exception as exc:
            latency_ms = int((perf_counter() - started) * 1000)
            await session.rollback()
            await chats.record_failed_run(
                session_id=session_id,
                user_message_id=user_message_id,
                model_name=app_settings.GROQ_MODEL,
                latency_ms=latency_ms,
                error=exc,
            )
            await session.commit()
            raise
