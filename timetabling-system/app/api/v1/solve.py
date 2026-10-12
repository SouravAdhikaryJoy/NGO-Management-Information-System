import uuid

from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.orm import Session as DbSession

from app.api.errors import api_error
from app.database import SessionLocal, get_db
from app.models import SolverRun
from app.schemas.api import SolveResponse, SolveStatusResponse
from app.security import require_admin
from app.solver.constraints.registry import build_summary
from app.solver.engine import execute_solver_run
from app.solver.loader import load_current_timetable, load_problem

router = APIRouter(tags=["solve"])


def _run_job(job_id: str, regenerate_sessions: bool):
    db = SessionLocal()
    try:
        execute_solver_run(db, job_id, regenerate_sessions=regenerate_sessions)
    finally:
        db.close()


@router.post("/solve", response_model=SolveResponse, status_code=202)
def trigger_solve(
    background_tasks: BackgroundTasks,
    regenerate_sessions: bool = True,
    db: DbSession = Depends(get_db),
    _admin=Depends(require_admin),
):
    """Trigger an async Phase1+Phase2 run; poll /solve/{job_id}/status."""
    job_id = str(uuid.uuid4())
    db.add(SolverRun(job_id=job_id, status="PENDING"))
    db.commit()
    background_tasks.add_task(_run_job, job_id, regenerate_sessions)
    return {"job_id": job_id, "status": "PENDING"}


@router.get("/solve/runs")
def list_runs(limit: int = 10, db: DbSession = Depends(get_db)):
    """Most recent solver runs, newest first (used by the web dashboard)."""
    runs = (
        db.query(SolverRun)
        .order_by(SolverRun.created_at.desc(), SolverRun.id.desc())
        .limit(max(1, min(limit, 50)))
        .all()
    )
    return {
        "runs": [
            {
                "job_id": r.job_id,
                "status": r.status,
                "soft_penalty": r.soft_penalty,
                "hard_violations": r.hard_violations,
                "runtime_seconds": r.runtime_seconds,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in runs
        ]
    }


@router.get("/solve/{job_id}/status", response_model=SolveStatusResponse)
def solve_status(job_id: str, db: DbSession = Depends(get_db)):
    run = db.query(SolverRun).filter(SolverRun.job_id == job_id).one_or_none()
    if run is None:
        raise api_error(404, "job_not_found", f"no solver run with job_id {job_id!r}")
    summary = None
    if run.status == "COMPLETED":
        problem = load_problem(db)
        timetable = load_current_timetable(db, problem)
        summary = build_summary(problem, timetable)
    return SolveStatusResponse(
        job_id=run.job_id,
        status=run.status,
        seed=run.seed,
        phase1_iterations=run.phase1_iterations,
        phase2_iterations=run.phase2_iterations,
        runtime_seconds=run.runtime_seconds,
        hard_violations=run.hard_violations,
        soft_penalty=run.soft_penalty,
        error=run.error,
        summary=summary,
    )
