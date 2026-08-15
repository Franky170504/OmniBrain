from __future__ import annotations

from langgraph.graph import (
    END,
    START,
    StateGraph,
)

from app.agents.search_agent import (
    SearchAgentNode,
)

from app.agents.sql_agent import (
    SqlAgentNode,
)

from app.agents.state import (
    AgentState,
)

from app.agents.supervisor import (
    SupervisorNode,
    supervisor_router,
)

from app.agents.vision_agent import (
    VisionAgentNode,
)

from app.services.rag_service import (
    RagService,
)

from app.services.sql_query_service import (
    SqlQueryService,
)

from app.services.vision_service import (
    VisionService,
)


class OmniBrainGraph:
    def __init__(
        self,
        rag_service: RagService,
    ) -> None:
        self.supervisor = (
            SupervisorNode()
        )

        self.search_agent = (
            SearchAgentNode(
                rag_service
            )
        )

        self.vision_agent = (
            VisionAgentNode(
                VisionService()
            )
        )

        self.sql_agent = (
            SqlAgentNode(
                SqlQueryService()
            )
        )

        self.graph = self._build()

    def _build(self):
        builder = StateGraph(
            AgentState
        )

        builder.add_node(
            "supervisor",
            self.supervisor,
        )

        builder.add_node(
            "search_agent",
            self.search_agent,
        )

        builder.add_node(
            "vision_agent",
            self.vision_agent,
        )

        builder.add_node(
            "sql_agent",
            self.sql_agent,
        )

        builder.add_edge(
            START,
            "supervisor",
        )

        builder.add_conditional_edges(
            "supervisor",
            supervisor_router,
            {
                "search_agent": (
                    "search_agent"
                ),
                "vision_agent": (
                    "vision_agent"
                ),
                "sql_agent": (
                    "sql_agent"
                ),
                "end": END,
            },
        )

        builder.add_edge(
            "search_agent",
            END,
        )

        builder.add_edge(
            "vision_agent",
            END,
        )

        builder.add_edge(
            "sql_agent",
            END,
        )

        return builder.compile()

    def invoke(
        self,
        *,
        question: str,
        user_id: str,
        document_id: str | None = None,
    ) -> dict:
        state: AgentState = {
            "question": question,
            "user_id": user_id,
            "document_id": document_id,

            "sources": [],
            "retrieval_attempts": 0,

            "visual_context": [],
            "visual_type": None,
            "page_number": None,

            "generated_sql": None,
            "sql_rows": [],

            "error": None,
        }

        result = self.graph.invoke(
            state,
            config={
                "run_name": (
                    "omnibrain-agent-graph"
                ),
                "tags": [
                    "omnibrain",
                    "langgraph",
                    "supervisor",
                    "search-agent",
                    "vision-agent",
                    "sql-agent",
                ],
                "metadata": {
                    "user_id": user_id,
                    "document_id": (
                        document_id
                    ),
                },
            },
        )

        return {
            "answer": result.get(
                "answer",
                "No answer was produced.",
            ),

            "sources": result.get(
                "sources",
                [],
            ),

            "route": result.get(
                "route"
            ),

            "route_reason": result.get(
                "route_reason"
            ),

            "retrieval_attempts": (
                result.get(
                    "retrieval_attempts",
                    0,
                )
            ),

            "visual_context": (
                result.get(
                    "visual_context",
                    [],
                )
            ),

            "visual_type": result.get(
                "visual_type"
            ),

            "page_number": result.get(
                "page_number"
            ),

            "generated_sql": result.get(
                "generated_sql"
            ),

            "sql_rows": result.get(
                "sql_rows",
                [],
            ),

            "error": result.get(
                "error"
            ),
        }