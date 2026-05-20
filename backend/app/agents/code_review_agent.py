"""Code Review Agent — LangGraph graph with human-in-the-loop approval.

Graph: analyze → security → suggest → [INTERRUPT for human feedback] → finalize
"""
import logging

from langchain_core.messages import AIMessage
from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt

from app.agents.checkpointer import get_postgres_checkpointer
from app.agents.state import CodeReviewState
from app.core.llm_clients import stream_completion

logger = logging.getLogger("genai_forge.code_review_agent")


async def _call_llm(prompt: str, model: str = "gpt-4o-mini") -> str:
    tokens: list[str] = []
    gen = await stream_completion(model=model, messages=[{"role": "user", "content": prompt}])
    async for token in gen:
        tokens.append(token)
    return "".join(tokens)


# ── Graph nodes ──────────────────────────────────────────────────────────────

async def analyze_node(state: CodeReviewState) -> CodeReviewState:
    analysis = await _call_llm(
        f"Analyze this {state['language']} code for quality, clarity, and correctness.\n\n```\n{state['code']}\n```"
    )
    return {**state, "analysis": analysis, "current_node": "analyze", "messages": [AIMessage(content=analysis)]}


async def security_node(state: CodeReviewState) -> CodeReviewState:
    raw = await _call_llm(
        f"List all security vulnerabilities in this {state['language']} code as a JSON array of strings.\n\n```\n{state['code']}\n```"
    )
    import json
    try:
        start, end = raw.find("["), raw.rfind("]") + 1
        issues: list[str] = json.loads(raw[start:end]) if start >= 0 else [raw]
    except json.JSONDecodeError:
        issues = [raw]
    return {
        **state,
        "security_issues": issues,
        "current_node": "security",
        "messages": [AIMessage(content=f"Found {len(issues)} security issue(s).")],
    }


async def suggest_node(state: CodeReviewState) -> CodeReviewState:
    context = f"Analysis:\n{state['analysis']}\n\nSecurity issues:\n" + "\n".join(state["security_issues"])
    raw = await _call_llm(
        f"Given this review context, suggest concrete improvements as a JSON array of strings.\n\n{context}"
    )
    import json
    try:
        start, end = raw.find("["), raw.rfind("]") + 1
        suggestions: list[str] = json.loads(raw[start:end]) if start >= 0 else [raw]
    except json.JSONDecodeError:
        suggestions = [raw]
    return {
        **state,
        "suggestions": suggestions,
        "current_node": "suggest",
        "messages": [AIMessage(content=f"Generated {len(suggestions)} suggestion(s). Awaiting human review.")],
    }


async def human_review_node(state: CodeReviewState) -> CodeReviewState:
    """Interrupt the graph to collect human feedback; resumes when feedback is provided."""
    review_summary = (
        f"Analysis:\n{state['analysis']}\n\n"
        f"Security issues:\n" + "\n".join(f"- {i}" for i in state["security_issues"]) + "\n\n"
        f"Suggestions:\n" + "\n".join(f"- {s}" for s in state["suggestions"])
    )
    # interrupt() pauses execution until /agents/resume/{job_id} is called
    feedback: str = interrupt({"prompt": "Review the analysis and approve or provide feedback.", "summary": review_summary})
    return {
        **state,
        "human_feedback": feedback,
        "approved": feedback.strip().lower() in ("approve", "approved", "lgtm", "yes"),
        "current_node": "human_review",
        "messages": [AIMessage(content=f"Human feedback received: {feedback}")],
    }


async def finalize_node(state: CodeReviewState) -> CodeReviewState:
    feedback_section = f"\n\nHuman feedback: {state['human_feedback']}" if state["human_feedback"] else ""
    final_report = await _call_llm(
        f"Produce a final code review report incorporating all findings and human feedback.\n\n"
        f"Analysis: {state['analysis']}\n"
        f"Security: {state['security_issues']}\n"
        f"Suggestions: {state['suggestions']}"
        f"{feedback_section}"
    )
    return {
        **state,
        "final_report": final_report,
        "current_node": "finalize",
        "messages": [AIMessage(content="Code review complete.")],
    }


# ── Graph definition ──────────────────────────────────────────────────────────

def build_code_review_graph():
    g = StateGraph(CodeReviewState)
    g.add_node("analyze", analyze_node)
    g.add_node("security", security_node)
    g.add_node("suggest", suggest_node)
    g.add_node("human_review", human_review_node)
    g.add_node("finalize", finalize_node)

    g.add_edge(START, "analyze")
    g.add_edge("analyze", "security")
    g.add_edge("security", "suggest")
    g.add_edge("suggest", "human_review")
    g.add_edge("human_review", "finalize")
    g.add_edge("finalize", END)
    return g


def get_code_review_graph():
    checkpointer = get_postgres_checkpointer()
    return build_code_review_graph().compile(checkpointer=checkpointer, interrupt_before=["human_review"])
