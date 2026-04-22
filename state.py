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
    # Video-pipeline outputs
    script: str
    title: str
    slug: str
    project_dir: str
    audio_path: str
    transcript: list[dict]
    design_brief: str
    html: str
    video_path: str
