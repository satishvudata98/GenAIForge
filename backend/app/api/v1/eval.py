"""RAGAS evaluation endpoints — run evaluation jobs and retrieve results."""
import asyncio
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.models.db import EvalRun

router = APIRouter(prefix="/eval", tags=["eval"])


@router.post("/run", status_code=status.HTTP_202_ACCEPTED)
async def start_eval_run(
    dataset_name: str = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """Upload a CSV and start a RAGAS evaluation job. Returns run_id immediately."""
    if not file.filename or not file.filename.endswith(".csv"):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Only CSV files are accepted."},
        )

    csv_content = await file.read()
    run_id = uuid4()

    eval_run = EvalRun(id=run_id, dataset_name=dataset_name, status="running")
    db.add(eval_run)
    await db.commit()
    await db.refresh(eval_run)

    # Run evaluation in background — does not block the response
    from app.rag.evaluation import run_ragas_evaluation

    async def _background():
        from app.dependencies import SessionLocal

        async with SessionLocal() as bg_db:
            await run_ragas_evaluation(
                run_id=run_id,
                dataset_name=dataset_name,
                csv_content=csv_content,
                db=bg_db,
            )

    asyncio.ensure_future(_background())

    return {"run_id": str(run_id), "status": "running", "dataset_name": dataset_name}


@router.get("/results")
async def list_eval_results(db: AsyncSession = Depends(get_db)):
    """List all evaluation run summaries ordered by creation date."""
    result = await db.execute(select(EvalRun).order_by(EvalRun.created_at.desc()))
    runs = result.scalars().all()
    return [_run_summary(r) for r in runs]


@router.get("/results/{run_id}")
async def get_eval_result(run_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get detailed scorecard for a specific evaluation run."""
    run = await db.get(EvalRun, run_id)
    if run is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": f"Evaluation run '{run_id}' not found."},
        )
    return _run_detail(run)


def _run_summary(run: EvalRun) -> dict:
    return {
        "id": str(run.id),
        "dataset_name": run.dataset_name,
        "row_count": run.row_count,
        "status": run.status,
        "faithfulness": run.faithfulness,
        "answer_relevancy": run.answer_relevancy,
        "context_precision": run.context_precision,
        "context_recall": run.context_recall,
        "created_at": run.created_at.isoformat(),
    }


def _run_detail(run: EvalRun) -> dict:
    return {
        **_run_summary(run),
        "raw_scores": run.raw_scores,
        "error": run.error,
    }
