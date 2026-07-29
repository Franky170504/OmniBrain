from __future__ import annotations

from typing import Literal
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field
from app.agents.state import AgentRoute, AgentState
from config.settings import settings


class SupervisorDecision(BaseModel):
    route: Literal[
        "document_agent",
        "general_agent",
        "clarify_agent",
    ] = Field(description="The agent that should process the request.")

    reason: str = Field(description="A brief explanation of the routing decision.")

class SupervisorNode:
    def __init__(self) -> None:
        if not settings.groq_api_key:
            raise RuntimeError("GROQ_API_KEY is required for the supervisor.")

        model_name = (settings.groq_supervisior_model or settings.groq_model)
        model = ChatGroq(
            model=model_name,
            api_key=settings.groq_api_key,
            temperature=0,
            max_retries=0,
        )
        self.router = model.with_structured_output(SupervisorDecision)

    def __call__(self, state: AgentState) -> dict:
        question = state.get("question", "").strip()
        document_id = state.get("document_id")
        if not question:
            return {
                "route": "clarify_agent",
                "route_reason": "No question was provided.",
            }
        prompt = f"""
                    You are the supervisor for OmniBrain.

                    Choose exactly one route:

                    document_agent:
                    Use this route when the user asks about an uploaded PDF, book,
                    report, document, chapter, author, table, summary, or document fact.

                    general_agent:
                    Use this route for general questions that do not depend on an
                    uploaded document.

                    clarify_agent:
                    Use this route when the question refers to a document but no
                    document_id is available, or when the request is unclear.

                    Document ID:
                    {document_id or "NONE"}

                    Question:
                    {question}

                    Do not answer the question. Only select the route.
                    """.strip()

        decision = self.router.invoke(prompt)
        return {
            "route": decision.route,
            "route_reason": decision.reason,
        }


def supervisor_router(state: AgentState) -> AgentRoute:
    return state.get("route", "clarify_agent")