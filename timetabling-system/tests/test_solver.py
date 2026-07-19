"""Phase 1 + Phase 2 solver tests on the sample dataset (build order #4/#6)."""

import io
import random

import pytest

from app.excel.import_templates import import_workbook
from app.excel.sample_data import write_sample_workbook
from app.models import Session, SystemConfig
from app.solver.constraints.registry import hard_violation_report, total_soft_penalty
from app.solver.loader import generate_sessions, load_problem
from app.solver.phase1_construction import run_phase1
from app.solver.phase2_refinement import run_phase2


def load_sample(db, scale: int = 1):
    buffer = io.BytesIO()
    write_sample_workbook(buffer, scale=scale)
    buffer.seek(0)
    result = import_workbook(db, buffer)
    assert result.ok, result.errors
    return result


def set_config(db, **values):
    for key, value in values.items():
        row = db.query(SystemConfig).filter(SystemConfig.key == key).one()
        row.value = str(value)
    db.commit()


@pytest.fixture()
def sample_problem(db):
    load_sample(db)
    generated = generate_sessions(db)
    assert generated > 40
    set_config(db, phase2_time_budget_seconds=3, phase2_iteration_budget=1500)
    return db, load_problem(db)


def test_phase1_reaches_zero_hard_violations(sample_problem):
    db, problem = sample_problem
    rng = random.Random(int(problem.cfg("random_seed", 42)))
    result = run_phase1(problem, rng)
    assert result.feasible, (result.unplaced, result.report)
    assert not result.unplaced
    assert all(row["violations"] == 0 for row in result.report)
    assert len(result.timetable.placements) == len(problem.sessions)


def test_phase2_improves_and_keeps_hard_invariant(sample_problem):
    db, problem = sample_problem
    rng = random.Random(int(problem.cfg("random_seed", 42)))
    p1 = run_phase1(problem, rng)
    assert p1.feasible
    initial = total_soft_penalty(problem, p1.timetable)
    p2 = run_phase2(problem, p1.timetable, rng)
    assert p2.final_penalty <= initial
    # hard invariant: refined timetable still has zero hard violations
    report = hard_violation_report(problem, p2.timetable)
    assert all(row["violations"] == 0 for row in report), report
    assert len(p2.timetable.placements) == len(problem.sessions)
    # every move type was exercised by the hyper-heuristic selector
    assert set(p2.move_stats) == {"single_swap", "kempe_chain", "ruin_recreate", "day_shift"}
    assert sum(stats["attempts"] for stats in p2.move_stats.values()) == p2.iterations


def test_solver_respects_locked_sessions(db):
    load_sample(db)
    generate_sessions(db)
    set_config(db, phase2_time_budget_seconds=2, phase2_iteration_budget=500)
    # lock one session to a fixed pin
    session = db.query(Session).first()
    session.is_locked = True
    session.locked_day = "WED"
    session.locked_slot_index = 3
    from app.models import Room, RoomType

    room_type = db.get(RoomType, session.required_room_type_id)
    room = db.query(Room).filter(Room.room_type_id == room_type.id).first()
    session.locked_room_id = room.id
    db.commit()

    problem = load_problem(db)
    rng = random.Random(1)
    p1 = run_phase1(problem, rng)
    assert p1.feasible
    p2 = run_phase2(problem, p1.timetable, rng)
    placement = p2.timetable.placements[session.id]
    assert (placement.day, placement.index, placement.room_id) == ("WED", 3, room.id)


def test_engine_run_records_reproducibility_metadata(db):
    import uuid

    from app.models import SolverRun
    from app.solver.engine import execute_solver_run

    load_sample(db)
    set_config(db, phase2_time_budget_seconds=2, phase2_iteration_budget=500)
    job_id = str(uuid.uuid4())
    db.add(SolverRun(job_id=job_id, status="PENDING"))
    db.commit()
    run = execute_solver_run(db, job_id)
    assert run.status == "COMPLETED", run.error
    assert run.seed is not None
    assert run.weights_snapshot and "S03_group_gaps" in run.weights_snapshot
    assert run.config_snapshot and "random_seed" in run.config_snapshot
    assert run.runtime_seconds > 0
    assert run.hard_violations == 0
