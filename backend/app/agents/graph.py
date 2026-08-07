from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from app.agents.clarify_agent import ClarifyAgent
from app.agents.document_agent import DocumentAgent
from app.agents.general_agent import GeneralAgent
from app.agents.state import AgentRoute, AgentState
from app.agents.supervisor import SupervisorNode
from app.services.rag_service import RagService


class OmniBrainGraph:
    def __init__(self, rag_service: RagService) -> None:
        supervisor = SupervisorNode()
        document_agent = DocumentAgent(rag_service)
        general_agent = GeneralAgent()
        clarify_agent = ClarifyAgent()

        builder = StateGraph(AgentState)
        builder.add_node("supervisor", supervisor)
        builder.add_node("document_agent", document_agent)
        builder.add_node("general_agent", general_agent)
        builder.add_node("clarify_agent", clarify_agent)

        builder.add_edge(START, "supervisor")
        builder.add_conditional_edges(
            "supervisor",
            self.supervisor_router,
            {
                "document_agent": "document_agent",
                "general_agent": "general_agent",
                "clarify_agent": "clarify_agent",
            },
        )
        builder.add_edge("document_agent", END)
        builder.add_edge("general_agent", END)
        builder.add_edge("clarify_agent", END)

        self.graph = builder.compile()

    @staticmethod
    def supervisor_router(state: AgentState) -> AgentRoute:
        return state.get("route", "clarify_agent")

    async def ainvoke(
        self,
        *,
        question: str,
        user_id: str,
        document_id: str | None,
    ) -> AgentState:
        initial_state: AgentState = {
            "question": question,
            "user_id": user_id,
            "document_id": document_id,
            "sources": [],
            "context_items": [],
            "error": None,
        }
        result = await self.graph.ainvoke(
            initial_state,
            config={
                "run_name": "omnibrain-agent-graph",
                "tags": ["omnibrain", "langgraph"],
            },
        )
        return result
