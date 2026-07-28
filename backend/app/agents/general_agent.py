from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq

from app.agents.state import AgentState
from config.settings import settings

class GeneralAgentNode:
    def __init__(self) -> None:
        self.model = ChatGroq(
            model=settings.groq_general_model,
            api_key=settings.groq_api_key,
            temperature=0.2,
            max_retries=0,
        )

    def __call__(self, state: AgentState) -> dict:
        question = state.get("question", "").strip()
        response = self.model.invoke(
            [
                SystemMessage(
                    content=(
                        "You are OmniBrain's general assistant. "
                        "Answer clearly and directly."
                    )
                ),
                HumanMessage(content=question),
            ]
        )

        answer = (
            response.content
            if isinstance(response.content, str)
            else str(response.content)
        )

        return {
            "answer": answer,
            "sources": [],
            "error": None,
        }