from langgraph.graph import END, START, StateGraph

from nodes import analyst_node, photo_generator_node, searcher_node, writer_node
from state import ResearchState


def build_graph():
    """Compile the deep-research + photo-generator pipeline."""
    g = StateGraph(ResearchState)
    g.add_node("searcher", searcher_node)
    g.add_node("analyst", analyst_node)
    g.add_node("writer", writer_node)
    g.add_node("photo_generator", photo_generator_node)

    g.add_edge(START, "searcher")
    g.add_edge("searcher", "analyst")
    g.add_edge("analyst", "writer")
    g.add_edge("writer", "photo_generator")
    g.add_edge("photo_generator", END)

    return g.compile()
