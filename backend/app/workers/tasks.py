"""Celery task definitions for async CrewAI and agent execution."""
import asyncio
import logging

from app.workers.celery_app import celery_app

logger = logging.getLogger("genai_forge.tasks")


def _run_async(coro):
    """Run an async coroutine from a sync Celery task."""
    return asyncio.get_event_loop().run_until_complete(coro)


@celery_app.task(bind=True, name="tasks.run_crew_pipeline")
def run_crew_pipeline_task(self, topic: str, model: str = "gpt-4o-mini") -> dict:
    """Execute the CrewAI content pipeline as a background task."""
    from app.workers.crew_pipeline import run_crew_pipeline

    self.update_state(state="PROGRESS", meta={"step": "starting", "topic": topic})
    try:
        result = _run_async(run_crew_pipeline(topic=topic, model=model))
        return result
    except Exception as exc:
        logger.error("crew_pipeline_task failed for topic '%s': %s", topic, exc)
        raise


@celery_app.task(bind=True, name="tasks.run_research_agent")
def run_research_agent_task(self, query: str, model: str = "gpt-4o-mini") -> dict:
    """Execute the research agent graph as a background task."""
    from app.agents.research_agent import research_graph
    from app.agents.state import ResearchState

    self.update_state(state="PROGRESS", meta={"step": "starting", "query": query})
    initial_state: ResearchState = {
        "query": query,
        "plan": "",
        "search_results": [],
        "extracted_facts": [],
        "report": "",
        "messages": [],
        "current_node": "start",
        "error": None,
    }
    result = _run_async(research_graph.ainvoke(initial_state))
    return {"report": result.get("report", ""), "facts": result.get("extracted_facts", [])}
