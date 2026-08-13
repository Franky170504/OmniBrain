from __future__ import annotations

import logging
from typing import Any
from langsmith import traceable

from app.agents.graph import OmniBrainGraph

LOGGER = logging.getLogger("omnibrain.chat_service")

class ChatService:
    def __init__(self, agent_graph: OmniBrainGraph, query_engine_service: Any | None = None) -> None:
        self.agent_graph = agent_graph
        self.query_engine_service = query_engine_service

    @traceable(name="omnibrain-chat-request", run_type="chain")
    def ask(self, *, question: str, user_id: str, document_id: str | None = None,) -> dict[str, Any]:
        LOGGER.info(
            "ChatService.ask ingress: question_len=%d user_id_len=%d document_id=%s",
            len(question or ""),
            len(user_id or ""),
            document_id,
        )
        result = self.agent_graph.invoke(
            question=question,
            user_id=user_id,
            document_id=document_id,
        )

        LOGGER.info(
            "ChatService.ask result stats: answer_len=%d sources=%d route=%s",
            len(str(result.get("answer") or "")),
            len(result.get("sources") or []),
            result.get("route"),
        )

        if self.query_engine_service is not None:
            try:
                self.query_engine_service.persist_chat_request(
                    question=question,
                    user_id=user_id,
                    document_id=document_id,
                    result=result,
                )
            except Exception as exc:
                LOGGER.warning(
                    "Query engine persistence was skipped after chat execution: %s",
                    exc,
                )

        return result