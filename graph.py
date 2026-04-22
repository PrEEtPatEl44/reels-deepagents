from langgraph.graph import END, START, StateGraph

from nodes import (
    analyst_node,
    builder_node,
    designer_node,
    narrator_node,
    renderer_node,
    scripter_node,
    searcher_node,
    writer_node,
)
from state import ResearchState


def build_graph():
    """Compile the deep-research + HyperFrames video pipeline."""
    g = StateGraph(ResearchState)
    g.add_node("searcher", searcher_node)
    g.add_node("analyst", analyst_node)
    g.add_node("writer", writer_node)
    g.add_node("scripter", scripter_node)
    g.add_node("narrator", narrator_node)
    g.add_node("designer", designer_node)
    g.add_node("builder", builder_node)
    g.add_node("renderer", renderer_node)

    g.add_edge(START, "searcher")
    g.add_edge("searcher", "analyst")
    g.add_edge("analyst", "writer")
    g.add_edge("writer", "scripter")
    g.add_edge("scripter", "narrator")
    g.add_edge("narrator", "designer")
    g.add_edge("designer", "builder")
    g.add_edge("builder", "renderer")
    g.add_edge("renderer", END)

    return g.compile()
