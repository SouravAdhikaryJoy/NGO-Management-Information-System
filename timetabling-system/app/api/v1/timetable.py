import io

from fastapi import APIRouter, Depends
from fastapi.responses import Response, StreamingResponse
from sqlalchemy.orm import Session as DbSession

from app.api.errors import api_error
from app.api.v1.serializers import session_rows
from app.database import get_db
from app.excel.export_formats import to_csv, to_ics, to_pdf
from app.excel.export_routine import export_routine
from app.models import SolverRun
from app.solver.constraints.registry import build_summary, hard_violation_report, soft_penalty_breakdown
from app.solver.loader import load_current_timetable, load_problem

router = APIRouter(tags=["timetable"])


def _get_completed_run(db: DbSession, run_id: str) -> SolverRun:
    run = db.query(SolverRun).filter(SolverRun.job_id == run_id).one_or_none()
    if run is None:
        raise api_error(404, "run_not_found", f"no solver run with id {run_id!r}")
    if run.status != "COMPLETED":
        raise api_error(
            409, "run_not_completed",
            f"solver run {run_id!r} has status {run.status}; timetable unavailable",
        )
    return run


@router.get("/timetable/{run_id}")
def get_timetable(run_id: str, db: DbSession = Depends(get_db)):
    """Canonical JSON timetable plus feasibility and soft-penalty reports."""
    run = _get_completed_run(db, run_id)
    problem = load_problem(db)
    timetable = load_current_timetable(db, problem)
    return {
        "run": {
            "job_id": run.job_id,
            "seed": run.seed,
            "soft_penalty": run.soft_penalty,
            "runtime_seconds": run.runtime_seconds,
        },
        "sessions": session_rows(db),
        "feasibility_report": hard_violation_report(problem, timetable),
        "soft_constraint_report": soft_penalty_breakdown(problem, timetable),
        "summary": build_summary(problem, timetable),
    }


@router.get("/timetable/{run_id}/export")
def export_timetable(run_id: str, format: str = "xlsx", db: DbSession = Depends(get_db)):
    _get_completed_run(db, run_id)
    rows = session_rows(db)
    if format == "xlsx":
        problem = load_problem(db)
        timetable = load_current_timetable(db, problem)
        buffer = io.BytesIO()
        export_routine(db, problem, timetable, buffer)
        buffer.seek(0)
        return StreamingResponse(
            buffer,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename=routine_{run_id}.xlsx"},
        )
    if format == "csv":
        return Response(
            to_csv(rows), media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=routine_{run_id}.csv"},
        )
    if format == "ics":
        return Response(
            to_ics(rows), media_type="text/calendar",
            headers={"Content-Disposition": f"attachment; filename=routine_{run_id}.ics"},
        )
    if format == "pdf":
        return Response(
            to_pdf(rows), media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=routine_{run_id}.pdf"},
        )
    raise api_error(400, "bad_format", f"unsupported format {format!r}; use xlsx|csv|ics|pdf")
