"""Build, minimally-room-size, solve and report the 60-teacher stress demo.

Usage: python scripts/run_stress_demo.py

Two phases:
 1. Room-count search: starting from the analytical lower bound, find the
    smallest (theory_rooms, lab_rooms) that Phase 1 can still solve to zero
    hard violations (search runs with a reduced repair budget so infeasible
    attempts fail fast instead of exhausting the full iteration cap).
 2. Full run: Phase 1 (full budget) + Phase 2, on the minimal room counts
    found, with a full report: hard violations, soft penalty totals and
    per-constraint breakdown, timings.
"""

import io
import math
import random
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import app.models  # noqa: F401  (register metadata)
from app.database import Base, SessionLocal, engine
from app.config.seed import seed_defaults
from app.excel.demo_stress import (
    DAYS, LAB_SLOTS, N_TEACHERS, THEORY_SLOTS, build_stress_frames,
)
from app.excel.import_templates import import_workbook
from app.models import SystemConfig
from app.solver.constraints.registry import build_summary, soft_penalty_breakdown
from app.solver.loader import generate_sessions, load_problem
from app.solver.phase1_construction import run_phase1
from app.solver.phase2_refinement import run_phase2

import pandas as pd


def fresh_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    seed_defaults(db)
    return db


def load_stress_data(db, n_theory_rooms, n_lab_rooms):
    frames = build_stress_frames(n_theory_rooms, n_lab_rooms)
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        for sheet, df in frames.items():
            df.to_excel(writer, sheet_name=sheet, index=False)
    buffer.seek(0)
    result = import_workbook(db, buffer)
    if not result.ok:
        raise RuntimeError(f"import failed: {result.errors[:5]}")
    generated = generate_sessions(db)
    return generated


def set_config(db, **values):
    for key, value in values.items():
        row = db.query(SystemConfig).filter(SystemConfig.key == key).one()
        row.value = str(value)
    db.commit()


def try_feasible(n_theory_rooms, n_lab_rooms, repair_iterations):
    db = fresh_db()
    generated = load_stress_data(db, n_theory_rooms, n_lab_rooms)
    set_config(db, phase1_max_repair_iterations=repair_iterations)
    problem = load_problem(db)
    started = time.monotonic()
    rng = random.Random(int(problem.cfg("random_seed", 42)))
    result = run_phase1(problem, rng)
    elapsed = time.monotonic() - started
    db.close()
    return generated, result, elapsed


def search_room_counts():
    theory_lower_bound = math.ceil(240 / (len(DAYS) * len(THEORY_SLOTS)))
    lab_lower_bound = math.ceil(120 / (len(DAYS) * (len(LAB_SLOTS) // 2)))
    print(f"Analytical lower bounds: theory_rooms >= {theory_lower_bound}, "
          f"lab_rooms >= {lab_lower_bound}\n")

    # search theory rooms with a generous fixed lab room count
    lab_probe = lab_lower_bound + 4
    theory_rooms = theory_lower_bound
    print("--- Searching minimal theory room count ---")
    while True:
        generated, result, elapsed = try_feasible(theory_rooms, lab_probe, 3000)
        status = "FEASIBLE" if result.feasible else f"infeasible ({len(result.unplaced)} unplaced)"
        print(f"  theory_rooms={theory_rooms:3d} lab_rooms={lab_probe:3d}  "
              f"-> {status}  ({elapsed:.1f}s, {generated} sessions)")
        if result.feasible:
            break
        theory_rooms += 1
        if theory_rooms > theory_lower_bound + 15:
            print("  giving up the theory search early (safety cap)")
            break

    # search lab rooms with the theory room count just found
    lab_rooms = lab_lower_bound
    print("\n--- Searching minimal lab room count ---")
    while True:
        generated, result, elapsed = try_feasible(theory_rooms, lab_rooms, 3000)
        status = "FEASIBLE" if result.feasible else f"infeasible ({len(result.unplaced)} unplaced)"
        print(f"  theory_rooms={theory_rooms:3d} lab_rooms={lab_rooms:3d}  "
              f"-> {status}  ({elapsed:.1f}s, {generated} sessions)")
        if result.feasible:
            break
        lab_rooms += 1
        if lab_rooms > lab_lower_bound + 15:
            print("  giving up the lab search early (safety cap)")
            break

    return theory_rooms, lab_rooms


def full_run(theory_rooms, lab_rooms, phase2_seconds=120):
    print(f"\n=== Full run: {theory_rooms} theory rooms, {lab_rooms} lab rooms ===")
    db = fresh_db()
    generated = load_stress_data(db, theory_rooms, lab_rooms)
    set_config(
        db,
        phase2_time_budget_seconds=phase2_seconds,
        phase2_iteration_budget=400000,
    )
    problem = load_problem(db)
    print(f"Teachers: {N_TEACHERS}  Sessions generated: {generated} "
          f"(expect 360 = 240 theory + 120 lab)")
    seed = int(problem.cfg("random_seed", 42))
    rng = random.Random(seed)

    t0 = time.monotonic()
    p1 = run_phase1(problem, rng)
    t1 = time.monotonic()
    print(f"\nPhase 1: feasible={p1.feasible}  time={t1 - t0:.1f}s  "
          f"repair_iterations={p1.iterations}  unplaced={len(p1.unplaced)}")
    if not p1.feasible:
        print("Phase 1 FAILED. Violations found:")
        for row in p1.report:
            if row["violations"]:
                print(f"  {row['key']}: {row['violations']}  ({row['description']})")
        return

    p2 = run_phase2(problem, p1.timetable, rng)
    t2 = time.monotonic()
    print(f"Phase 2: time={t2 - t1:.1f}s  iterations={p2.iterations} "
          f"(finisher {p2.finisher_iterations})  accepted={p2.accepted}")
    print(f"Soft penalty: {p2.initial_penalty:.1f} -> {p2.final_penalty:.1f} "
          f"({(1 - p2.final_penalty / p2.initial_penalty) * 100:.1f}% reduction)")
    print("Move stats:")
    for key, stats in p2.move_stats.items():
        print(f"  {key:16s} attempts={stats['attempts']:5d}  accepted={stats['accepted']:5d}")

    summary = build_summary(problem, p2.timetable)
    print("\n--- Summary ---")
    for key, value in summary.items():
        print(f"  {key}: {value}")

    print("\n--- Soft constraint breakdown (nonzero only) ---")
    breakdown = sorted(
        soft_penalty_breakdown(problem, p2.timetable),
        key=lambda r: -r["weighted_penalty"],
    )
    for row in breakdown:
        if row["raw_penalty"] > 0:
            print(f"  tier{row['tier']}  {row['key']:32s} raw={row['raw_penalty']:7.1f}  "
                  f"weight={row['weight']:5.1f}  weighted={row['weighted_penalty']:8.1f}")

    print(f"\nTotal wall time: {time.monotonic() - t0:.1f}s")
    db.close()
    return summary, breakdown, p2


if __name__ == "__main__":
    theory_rooms, lab_rooms = search_room_counts()
    print(f"\n>>> Minimal feasible room counts found: "
          f"{theory_rooms} theory rooms, {lab_rooms} lab rooms <<<")
    full_run(theory_rooms, lab_rooms)
