"""Research Agent — LangGraph graph with plan → search → extract → synthesize → report nodes.

Tools:
  - Tavily Search API (web search)
  - Wikipedia API (structured knowledge)
"""
import json
import logging
from typing import Any

from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph import END, START, StateGraph

from app.agents.state import ResearchState
from app.config import get_settings
from app.core.llm_clients import stream_completion
from app.core.tracing import observe, update_span_usage

logger = logging.getLogger("genai_forge.research_agent")
settings = get_settings()


async def _call_llm(prompt: str, model: str = "gpt-4o-mini") -> str:
    """Single-shot LLM call, collects streamed tokens into a string."""
    tokens: list[str] = []
    gen = await stream_completion(model=model, messages=[{"role": "user", "content": prompt}])
    async for token in gen:
        tokens.append(token)
    result = "".join(tokens)
    update_span_usage(model, prompt, result)
    return result


async def _tavily_search(query: str, max_results: int = 5) -> list[dict[str, Any]]:
    if not settings.tavily_api_key:
        logger.warning("TAVILY_API_KEY not set; returning empty search results.")
        return []
    try:
        from tavily import AsyncTavilyClient  # type: ignore[import]

        client = AsyncTavilyClient(api_key=settings.tavily_api_key)
        response = await client.search(query=query, max_results=max_results)
        return response.get("results", [])
    except Exception as exc:
        logger.error("Tavily search failed: %s", exc)
        return []


async def _wikipedia_search(query: str) -> dict[str, Any]:
    try:
        import wikipedia  # type: ignore[import]

        page = wikipedia.page(query, auto_suggest=True)
        return {"title": page.title, "summary": page.summary, "url": page.url}
    except Exception:
        return {}


# ── Graph nodes ──────────────────────────────────────────────────────────────

@observe(name="research_plan_node")
async def plan_node(state: ResearchState) -> ResearchState:
    plan = await _call_llm(
        f"Create a concise research plan (3-5 bullet steps) for answering this query:\n\n{state['query']}"
    )
    return {**state, "plan": plan, "current_node": "plan", "messages": [AIMessage(content=f"Plan:\n{plan}")]}


@observe(name="research_search_node")
async def search_node(state: ResearchState) -> ResearchState:
    tavily_results = await _tavily_search(state["query"])
    wiki_result = await _wikipedia_search(state["query"])
    all_results = tavily_results
    if wiki_result:
        all_results = [{"title": wiki_result["title"], "content": wiki_result["summary"], "url": wiki_result["url"]}, *tavily_results]
    summary = f"Found {len(all_results)} sources."
    return {**state, "search_results": all_results, "current_node": "search", "messages": [AIMessage(content=summary)]}


@observe(name="research_extract_node")
async def extract_node(state: ResearchState) -> ResearchState:
    sources_text = "\n\n".join(
        f"[{i+1}] {r.get('title', 'Unknown')}: {r.get('content', '')[:400]}"
        for i, r in enumerate(state["search_results"])
    )
    facts_raw = await _call_llm(
        f"Extract 5-10 key facts relevant to '{state['query']}' from these sources:\n\n{sources_text}\n\nReturn as a JSON array of strings."
    )
    try:
        start = facts_raw.find("[")
        end = facts_raw.rfind("]") + 1
        facts: list[str] = json.loads(facts_raw[start:end]) if start >= 0 else [facts_raw]
    except json.JSONDecodeError:
        facts = [facts_raw]
    return {**state, "extracted_facts": facts, "current_node": "extract", "messages": [AIMessage(content=f"Extracted {len(facts)} facts.")]}


@observe(name="research_synthesize_node")
async def synthesize_node(state: ResearchState) -> ResearchState:
    facts_text = "\n".join(f"- {f}" for f in state["extracted_facts"])
    report = await _call_llm(
        f"Write a comprehensive research report answering '{state['query']}' based on these facts:\n\n{facts_text}\n\n"
        "Include an introduction, key findings, and a conclusion. Cite sources as [N]."
    )
    return {**state, "report": report, "current_node": "synthesize", "messages": [AIMessage(content="Report drafted.")]}


@observe(name="research_report_node")
async def report_node(state: ResearchState) -> ResearchState:
    return {**state, "current_node": "report", "messages": [AIMessage(content="Research complete.")]}


# ── Graph definition ──────────────────────────────────────────────────────────

def build_research_graph() -> StateGraph:
    g = StateGraph(ResearchState)
    g.add_node("plan", plan_node)
    g.add_node("search", search_node)
    g.add_node("extract", extract_node)
    g.add_node("synthesize", synthesize_node)
    g.add_node("report", report_node)

    g.add_edge(START, "plan")
    g.add_edge("plan", "search")
    g.add_edge("search", "extract")
    g.add_edge("extract", "synthesize")
    g.add_edge("synthesize", "report")
    g.add_edge("report", END)
    return g


research_graph = build_research_graph().compile()
