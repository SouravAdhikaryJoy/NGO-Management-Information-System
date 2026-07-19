"""Scale test (build order #10): 500+ courses, Phase 1 construction profiled.

Run explicitly with:  pytest -m scale -s
"""

import io
import random
import time

import pytest

from app.excel.import_templates import import_workbook
from app.excel.sample_data import build_sample_frames
from app.solver.loader import generate_sessions, load_problem
from app.solver.phase1_construction import run_phase1

import pandas as pd


@pytest.mark.scale
def test_phase1_at_scale(db):
    frames = build_sample_frames(scale=50)  # 50 departments x 10 courses = 500 courses
    assert len(frames["Courses"]) == 500
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        for sheet, df in frames.items():
            df.to_excel(writer, sheet_name=sheet, index=False)
    buffer.seek(0)

    started = time.monotonic()
    result = import_workbook(db, buffer)
    assert result.ok, result.errors[:5]
    print(f"\nimport: {time.monotonic() - started:.1f}s")

    started = time.monotonic()
    generated = generate_sessions(db)
    print(f"session generation: {generated} sessions in {time.monotonic() - started:.1f}s")
    assert generated >= 2000

    problem = load_problem(db)
    started = time.monotonic()
    p1 = run_phase1(problem, random.Random(42))
    elapsed = time.monotonic() - started
    print(f"phase1: feasible={p1.feasible} in {elapsed:.1f}s "
          f"({p1.iterations} repair iterations, {len(p1.unplaced)} unplaced)")
    assert p1.feasible, (len(p1.unplaced), [r for r in p1.report if r["violations"]])
