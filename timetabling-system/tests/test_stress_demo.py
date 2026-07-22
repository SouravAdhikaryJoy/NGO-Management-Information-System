"""Large stress demo regression test (build order #10): 60 teachers, 240
theory + 120 lab sessions/week, fixed lab/theory timeslot pools, split
Friday-Saturday / Thursday-Friday weekends, at the minimal feasible room
count found by scripts/run_stress_demo.py (7 theory rooms, 10 lab rooms).

Run explicitly with: pytest -m scale -s
"""

import random

import pytest

from app.excel.demo_stress import N_TEACHERS
from app.solver.constraints.registry import build_summary
from app.solver.loader import generate_sessions, load_problem
from app.solver.phase1_construction import run_phase1
from app.solver.phase2_refinement import run_phase2
from scripts.run_stress_demo import load_stress_data, set_config

THEORY_ROOMS = 7
LAB_ROOMS = 10


@pytest.mark.scale
def test_stress_demo_reaches_zero_hard_violations(db):
    generated = load_stress_data(db, THEORY_ROOMS, LAB_ROOMS)
    assert generated == 360  # 60 teachers x (4 theory + 2 lab)

    problem = load_problem(db)
    assert len(problem.teachers) == N_TEACHERS == 60
    rng = random.Random(int(problem.cfg("random_seed", 42)))

    p1 = run_phase1(problem, rng)
    assert p1.feasible, (len(p1.unplaced), [r for r in p1.report if r["violations"]])

    set_config(db, phase2_time_budget_seconds=30, phase2_iteration_budget=50000)
    problem.config["phase2_time_budget_seconds"] = 30.0
    p2 = run_phase2(problem, p1.timetable, rng)

    summary = build_summary(problem, p2.timetable)
    assert summary["hard_constraints_satisfied"] is True
    assert summary["sessions_placed"] == summary["sessions_total"] == 360
    assert summary["hard_violations_total"] == 0
    print(f"\nstress demo: hard=0, soft penalty {p2.initial_penalty:.0f} -> "
          f"{p2.final_penalty:.0f} in 30s at the minimal room count "
          f"({THEORY_ROOMS} theory, {LAB_ROOMS} lab)")
