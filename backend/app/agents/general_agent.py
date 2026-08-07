from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq

from app.agents.state import AgentState
from app.core.app_config import app_settings


class GeneralAgent:
    def __init__(self) -> None:
        self.llm = ChatGroq(
            api_key=app_settings.GROQ_API_KEY,
            model=app_settings.GROQ_GENERAL_MODEL,
            temperature=0.2,
        )

    async def __call__(self, state: AgentState) -> dict:
        response = await self.llm.ainvoke(
            [
                SystemMessage(
                    content=(
                        "You are OmniBrain's general analysis agent. Give a clear, accurate answer. "
                        "For financial questions, distinguish facts, formulas, assumptions, and possible interpretations. "
                        "Do not pretend you used an uploaded document when the request is general knowledge."
                    )
                ),
                HumanMessage(content=state["question"]),
            ]
        )
        return {
            "answer": str(response.content),
            "sources": [],
            "context_items": [],
            "retrieval_latency_ms": None,
            "error": None,
        }
