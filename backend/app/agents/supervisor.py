from __future__ import annotations

from typing import Literal

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field

from app.agents.state import AgentState
from app.core.app_config import app_settings


class SupervisorDecision(BaseModel):
    route: Literal["document_agent", "general_agent", "clarify_agent"]
    reason: str = Field(min_length=1)


class SupervisorNode:
    def __init__(self) -> None:
        llm = ChatGroq(
            api_key=app_settings.GROQ_API_KEY,
            model=app_settings.GROQ_SUPERVISIOR_MODEL,
            temperature=0,
        )
        self.router = llm.with_structured_output(SupervisorDecision)

    async def __call__(self, state: AgentState) -> dict:
        question = state.get("question", "").strip()
        document_id = state.get("document_id")

        system_prompt = """
You are the OmniBrain supervisor. Route the request; do not answer it.

Routes:
- document_agent: the user asks for facts, summaries, calculations, comparisons,
  evidence, or analysis that must come from the selected uploaded document.
- general_agent: the question is general knowledge and can be answered without
  an uploaded document.
- clarify_agent: critical information is missing or the request is ambiguous.
  Use this when a document-specific request has no document_id, or when the
  requested metric/comparison/entities are too unclear to answer responsibly.

Return exactly one valid structured route and a concise reason.
""".strip()

        response = await self.router.ainvoke(
            [
                SystemMessage(content=system_prompt),
                HumanMessage(
                    content=(
                        f"Question: {question}\n"
                        f"Selected document_id: {document_id or 'NONE'}"
                    )
                ),
            ]
        )
        return {"route": response.route, "route_reason": response.reason}
