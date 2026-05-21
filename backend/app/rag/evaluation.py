"""RAGAS evaluation pipeline — scores RAG quality using gpt-4o as judge.

Metrics computed: faithfulness, answer_relevancy, context_precision, context_recall.
"""
import csv
import io
import logging
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.db import EvalRun

logger = logging.getLogger("genai_forge.evaluation")
settings = get_settings()

EvalRow = dict[str, Any]


def _parse_csv(content: bytes) -> list[EvalRow]:
    """Parse a CSV with columns: question, answer, contexts, ground_truth."""
    rows: list[EvalRow] = []
    reader = csv.DictReader(io.StringIO(content.decode("utf-8")))
    required = {"question", "answer", "contexts", "ground_truth"}
    for i, row in enumerate(reader):
        missing = required - set(row.keys())
        if missing:
            raise ValueError(f"Row {i + 1} missing columns: {missing}")
        rows.append({
            "question": row["question"].strip(),
            "answer": row["answer"].strip(),
            # Contexts column uses pipe | as separator for multiple passages
            "contexts": [c.strip() for c in row["contexts"].split("|") if c.strip()],
            "ground_truth": row["ground_truth"].strip(),
        })
    return rows


async def run_ragas_evaluation(
    *,
    run_id: UUID,
    dataset_name: str,
    csv_content: bytes,
    db: AsyncSession,
) -> None:
    """Run RAGAS evaluation asynchronously and persist results to PostgreSQL."""
    result = await db.get(EvalRun, run_id)
    if result is None:
        logger.error("EvalRun %s not found in DB.", run_id)
        return

    try:
        rows = _parse_csv(csv_content)
        if not rows:
            raise ValueError("CSV file contains no data rows.")

        from datasets import Dataset  # type: ignore[import]
        from ragas import evaluate  # type: ignore[import]
        from ragas.metrics import (  # type: ignore[import]
            answer_relevancy,
            context_precision,
            context_recall,
            faithfulness,
        )

        dataset = Dataset.from_list(rows)
        scores = evaluate(
            dataset=dataset,
            metrics=[faithfulness, answer_relevancy, context_precision, context_recall],
        )
        scores_dict = scores.to_pandas().mean().to_dict()

        result.faithfulness = float(scores_dict.get("faithfulness", 0.0))
        result.answer_relevancy = float(scores_dict.get("answer_relevancy", 0.0))
        result.context_precision = float(scores_dict.get("context_precision", 0.0))
        result.context_recall = float(scores_dict.get("context_recall", 0.0))
        result.raw_scores = {k: float(v) for k, v in scores_dict.items()}
        result.row_count = len(rows)
        result.status = "completed"

    except Exception as exc:
        logger.exception("RAGAS evaluation failed for run %s: %s", run_id, exc)
        result.status = "error"
        result.error = str(exc)

    await db.commit()
