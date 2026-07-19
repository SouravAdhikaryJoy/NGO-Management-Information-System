"""Solver run orchestration: Phase 1 gate -> Phase 2 -> persist + log run."""

from __future__ import annotations

import logging
import random
import time
import traceback

from sqlalchemy.orm import Session as DbSession

from app.models import SolverRun
from app.solver.loader import generate_sessions, load_problem, persist_timetable
from app.solver.phase1_construction import run_phase1
from app.solver.phase2_refinement import run_phase2

logger = logging.getLogger("timetabling.solver")


def execute_solver_run(db: DbSession, job_id: str, regenerate_sessions: bool = True) -> SolverRun:
    run = db.query(SolverRun).filter(SolverRun.job_id == job_id).one()
    run.status = "RUNNING"
    db.commit()
    started = time.monotonic()
    try:
        if regenerate_sessions:
            generate_sessions(db)
        problem = load_problem(db)
        seed = int(problem.cfg("random_seed", 42))
        rng = random.Random(seed)

        run.seed = seed
        run.weights_snapshot = {
            key: {"tier": w.tier, "weight": w.weight, "is_hard": w.is_hard, "enabled": w.enabled}
            for key, w in problem.weights.items()
        }
        run.config_snapshot = {k: str(v) for k, v in problem.config.items()}
        db.commit()

        logger.info(
            "solver run %s starting: %d sessions, seed=%d",
            job_id, len(problem.sessions), seed,
        )

        p1 = run_phase1(problem, rng)
        run.phase1_iterations = p1.iterations
        run.hard_violations = sum(r["violations"] for r in p1.report)
        if not p1.feasible:
            run.status = "PHASE1_FAILED"
            run.error = (
                f"Phase 1 could not reach feasibility: {len(p1.unplaced)} unplaced sessions; "
                f"violations: {[r for r in p1.report if r['violations']]}"
            )
            run.runtime_seconds = time.monotonic() - started
            db.commit()
            return run

        p2 = run_phase2(problem, p1.timetable, rng)
        run.phase2_iterations = p2.iterations
        run.soft_penalty = p2.final_penalty

        persist_timetable(db, p2.timetable)
        run.status = "COMPLETED"
        run.runtime_seconds = time.monotonic() - started
        db.commit()
        logger.info(
            "solver run %s completed in %.2fs: penalty %.1f -> %.1f "
            "(phase1 %d iters, phase2 %d iters, %d accepted) move_stats=%s",
            job_id, run.runtime_seconds, p2.initial_penalty, p2.final_penalty,
            p1.iterations, p2.iterations, p2.accepted, p2.move_stats,
        )
        return run
    except Exception as exc:  # surfaced via job status, never a raw 500
        db.rollback()
        run = db.query(SolverRun).filter(SolverRun.job_id == job_id).one()
        run.status = "FAILED"
        run.error = f"{exc}\n{traceback.format_exc()}"
        run.runtime_seconds = time.monotonic() - started
        db.commit()
        logger.exception("solver run %s failed", job_id)
        return run
