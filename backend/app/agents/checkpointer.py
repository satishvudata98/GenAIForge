"""PostgreSQL-backed LangGraph checkpointer for human-in-the-loop agent state persistence."""
from __future__ import annotations

import logging

from app.config import get_settings

logger = logging.getLogger("genai_forge.checkpointer")
settings = get_settings()


def get_postgres_checkpointer():
    """Return a synchronous PostgresSaver for LangGraph graph compilation.

    Uses the sync DSN (psycopg2) derived from the asyncpg DSN.
    The checkpointer is used only during graph.compile(); actual execution
    remains async via ainvoke/astream.
    """
    try:
        from langgraph.checkpoint.postgres import PostgresSaver  # type: ignore[import]

        # Convert asyncpg DSN → psycopg2 DSN
        sync_dsn = settings.postgres_dsn.replace("postgresql+asyncpg://", "postgresql://")
        return PostgresSaver.from_conn_string(sync_dsn)
    except ImportError:
        logger.warning(
            "langgraph-checkpoint-postgres not installed; falling back to in-process MemorySaver."
        )
        from langgraph.checkpoint.memory import MemorySaver  # type: ignore[import]
        return MemorySaver()
