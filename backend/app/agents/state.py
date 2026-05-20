"""Shared state schemas for LangGraph agent graphs."""
from typing import Annotated, Any
from typing_extensions import TypedDict

from langgraph.graph.message import add_messages


class ResearchState(TypedDict):
    """State for the multi-step Research Agent graph."""

    query: str
    plan: str
    search_results: list[dict[str, Any]]
    extracted_facts: list[str]
    report: str
    messages: Annotated[list, add_messages]
    current_node: str
    error: str | None


class CodeReviewState(TypedDict):
    """State for the Code Review Agent graph (supports human-in-the-loop pause)."""

    code: str
    language: str
    analysis: str
    security_issues: list[str]
    suggestions: list[str]
    human_feedback: str | None
    final_report: str
    messages: Annotated[list, add_messages]
    current_node: str
    approved: bool
    job_id: str
