from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional
from backend.rag.deep_research.nodes import (
    node_decompose,
    node_retrieve,
    node_synthesize,
    node_reflect,
    node_requery,
    node_finalize,
)


class ResearchState(TypedDict):
    question: str
    provider: str
    model: Optional[str]
    collections: list[str]
    sub_questions: list[str]
    retrieved_chunks: list[dict]
    draft_answer: str
    confidence: float
    gaps: str
    needs_requery: bool
    requeried: bool
    final_answer: str
    citations: list[dict]
    steps: list[dict]


def _route_after_reflect(state: ResearchState) -> str:
    if state.get("needs_requery"):
        return "requery"
    return "finalize"


def build_graph() -> StateGraph:
    g = StateGraph(ResearchState)

    g.add_node("decompose", node_decompose)
    g.add_node("retrieve", node_retrieve)
    g.add_node("synthesize", node_synthesize)
    g.add_node("reflect", node_reflect)
    g.add_node("requery", node_requery)
    g.add_node("finalize", node_finalize)

    g.set_entry_point("decompose")
    g.add_edge("decompose", "retrieve")
    g.add_edge("retrieve", "synthesize")
    g.add_edge("synthesize", "reflect")
    g.add_conditional_edges("reflect", _route_after_reflect, {"requery": "requery", "finalize": "finalize"})
    g.add_edge("requery", "synthesize")
    g.add_edge("finalize", END)

    return g.compile()


_graph = None


def get_graph():
    global _graph
    if _graph is None:
        _graph = build_graph()
    return _graph
