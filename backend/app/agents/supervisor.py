from __future__ import annotations

from typing import Literal

from langchain_groq import ChatGroq
from pydantic import BaseModel, Field

from app.agents.routing import deterministic_route
from app.agents.state import AgentRoute, AgentState
from app.core.app_config import settings


class SupervisorDecision(BaseModel):
    route: Literal[
        "search_agent",
        "vision_agent",
        "sql_agent",
    ] = Field(
        description=(
            "The specialized OmniBrain agent "
            "that should process the request."
        )
    )

    reason: str = Field(
        description=(
            "A brief explanation of the "
            "routing decision."
        )
    )


class SupervisorNode:
    def __init__(self) -> None:
        if not settings.groq_api_key:
            raise RuntimeError(
                "GROQ_API_KEY is required "
                "for the supervisor."
            )

        model_name = (
            settings.groq_supervisior_model
            or settings.groq_model
        )

        model = ChatGroq(
            model=model_name,
            api_key=settings.groq_api_key,
            temperature=0,
            max_retries=0,
        )

        self.router = (
            model.with_structured_output(
                SupervisorDecision
            )
        )

    def __call__(
        self,
        state: AgentState,
    ) -> dict:
        question = (
            state
            .get("question", "")
            .strip()
        )

        document_id = state.get(
            "document_id"
        )

        if not question:
            return {
                "route": "end",
                "route_reason": (
                    "No question was provided."
                ),
                "answer": (
                    "Please enter a question."
                ),
                "sources": [],
                "error": None,
            }

        route = deterministic_route(
            question,
            document_id,
        )

        if route == "end":
            return {
                "route": "end",
                "route_reason": (
                    "The question is empty."
                ),
                "answer": (
                    "Please enter a question."
                ),
                "sources": [],
                "error": None,
            }

        if route:
            reasons = {
                "search_agent": (
                    "The request requires textual "
                    "information from a document."
                ),
                "vision_agent": (
                    "The request requires interpreting "
                    "a table, chart, graph, figure, "
                    "diagram, or image."
                ),
                "sql_agent": (
                    "The request requires structured "
                    "or historical data analysis."
                ),
            }

            return {
                "route": route,
                "route_reason": reasons[route],
            }

        normalized = question.lower()

        document_terms = (
            "document",
            "pdf",
            "report",
            "page",
            "chapter",
            "table",
            "chart",
            "graph",
            "figure",
            "image",
            "diagram",
        )

        if (
            not document_id
            and any(
                term in normalized
                for term in document_terms
            )
        ):
            return {
                "route": "end",
                "route_reason": (
                    "The request refers to a document "
                    "but no document is selected."
                ),
                "answer": (
                    "Please upload or select a document "
                    "before asking this question."
                ),
                "sources": [],
                "error": None,
            }

        prompt = f"""
You are the routing supervisor for OmniBrain.

You do NOT answer the user's question.

You only select one of these three agents:

SEARCH_AGENT

Use search_agent for textual information contained
inside uploaded documents.

Examples:
- summarize this report
- explain section 3
- where is AI mentioned?
- what does the PDF say about risk?
- find a fact inside the document
- explain a paragraph
- search document text

SEARCH_AGENT uses Qdrant semantic retrieval.

VISION_AGENT

Use vision_agent when understanding visual document
content is required.

Examples:
- explain this table
- explain the chart on page 10
- describe the graph
- interpret figure 4
- explain this diagram
- describe an image
- identify a trend in a chart

Visual content includes:
- tables
- charts
- graphs
- images
- diagrams
- figures
- plots

SQL_AGENT

Use sql_agent when the user needs structured or
historical data from PostgreSQL.

Examples:
- total revenue by year
- average sales by month
- top 10 customers
- count records
- historical values
- aggregate millions of rows
- compare years
- query structured datasets
- historical stock information

Rules:

1. Text inside documents -> search_agent.
2. Tables/images/charts/graphs -> vision_agent.
3. Structured/historical data -> sql_agent.
4. Do not answer the question.
5. Select exactly one route.

Selected document:
{document_id or "NONE"}

Question:
{question}
""".strip()

        decision = self.router.invoke(
            prompt
        )

        return {
            "route": decision.route,
            "route_reason": decision.reason,
        }


def supervisor_router(
    state: AgentState,
) -> AgentRoute:
    return state.get(
        "route",
        "end",
    )