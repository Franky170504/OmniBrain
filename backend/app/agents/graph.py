from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from app.agents.clarify_agent import ClarifyAgentNode
from app.agents.document_agent import DocumentAgentNode
from app.agents.general_agent import GeneralAgentNode
from app.agents.state import AgentState
from app.agents.supervisor import SupervisorNode, supervisor_router
from app.services.rag_service import RagService

class OmniBrainGraph:
    def __init__(self, rag_service: RagService) -> None:
        self.supervisor = SupervisorNode()
        self.document_agent = DocumentAgentNode(rag_service)
        self.general_agent = GeneralAgentNode()
        self.clarify_agent = ClarifyAgentNode()
        self.graph = self._build()

    def _build(self):
        builder = StateGraph(AgentState)
        builder.add_node("supervisor",self.supervisor)
        builder.add_node("document_agent",self.document_agent)
        builder.add_node("general_agent",self.general_agent)
        builder.add_node("clarify_agent",self.clarify_agent)
        builder.add_edge(START,"supervisor",)
        builder.add_conditional_edges("supervisor",
            supervisor_router,
            {
                "document_agent": "document_agent",
                "general_agent": "general_agent",
                "clarify_agent": "clarify_agent",
            },
        )
        builder.add_edge("document_agent", END)
        builder.add_edge("general_agent", END)
        builder.add_edge("clarify_agent", END)
        return builder.compile()

    def invoke(self, *, question: str, user_id: str, document_id: str | None = None) -> dict:
        state: AgentState = {
            "question": question,
            "user_id": user_id,
            "document_id": document_id,
            "sources": [],
            "error": None,
        }

        result = self.graph.invoke(
            state,
            config={
                "run_name": "omnibrain-agent-graph",
                "tags": [
                    "omnibrain",
                    "langgraph",
                    "groq",
                ],
                "metadata": {
                    "user_id": user_id,
                    "document_id": document_id,
                },
            },
        )

        return {
            "answer": result.get(
                "answer",
                "No answer was produced.",
            ),
            "sources": result.get("sources", []),
            "route": result.get("route"),
            "route_reason": result.get("route_reason"),
        }