from typing import TypedDict
from typing_extensions import Annotated

from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages


class ResearchState(TypedDict, total=False):
    topic: str
    search_messages: Annotated[list[AnyMessage], add_messages]
    research_findings: str
    analysis: str
    report: str
    slide_plan: list[dict]
    caption: str
    carousel_zip_path: str
