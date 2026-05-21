"""CrewAI sequential content pipeline: Researcher → Writer → Editor.

Requires: crewai>=0.90
"""
import logging
from typing import Any

from app.core.tracing import observe

logger = logging.getLogger("genai_forge.crew_pipeline")


@observe(name="crew_pipeline_run")
async def run_crew_pipeline(topic: str, model: str = "gpt-4o-mini") -> dict[str, Any]:
    """Run the Researcher → Writer → Editor pipeline and return the final article."""
    try:
        from crewai import Agent, Crew, Process, Task  # type: ignore[import]
        from crewai.llm import LLM  # type: ignore[import]
    except ImportError:
        logger.error("crewai package not installed. Run: pip install crewai")
        return {"error": "crewai not installed", "content": ""}

    from app.config import get_settings

    settings = get_settings()
    if not settings.openai_api_key:
        return {"error": "OPENAI_API_KEY required for CrewAI", "content": ""}

    llm = LLM(model=model, api_key=settings.openai_api_key)

    researcher = Agent(
        role="Research Specialist",
        goal=f"Gather comprehensive factual information about: {topic}",
        backstory="Expert researcher with deep knowledge across domains. Produces thorough, accurate briefs.",
        llm=llm,
        verbose=False,
    )
    writer = Agent(
        role="Technical Writer",
        goal="Transform research briefs into clear, engaging articles",
        backstory="Experienced technical writer who simplifies complex topics without losing accuracy.",
        llm=llm,
        verbose=False,
    )
    editor = Agent(
        role="Senior Editor",
        goal="Polish and finalize articles to publication quality",
        backstory="Detail-oriented editor focused on clarity, structure, and factual integrity.",
        llm=llm,
        verbose=False,
    )

    research_task = Task(
        description=f"Research the topic '{topic}'. Produce a structured brief with key facts, context, and sources.",
        expected_output="A structured research brief with 5-10 bullet points and source references.",
        agent=researcher,
    )
    write_task = Task(
        description="Using the research brief, write a 400-600 word article on the topic.",
        expected_output="A well-structured article with introduction, body sections, and conclusion.",
        agent=writer,
    )
    edit_task = Task(
        description="Review and polish the article. Fix grammar, improve flow, and ensure factual accuracy.",
        expected_output="A publication-ready article.",
        agent=editor,
    )

    crew = Crew(
        agents=[researcher, writer, editor],
        tasks=[research_task, write_task, edit_task],
        process=Process.sequential,
        verbose=False,
    )

    result = crew.kickoff()
    return {"topic": topic, "content": str(result), "model": model}
