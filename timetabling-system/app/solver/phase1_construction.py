"""Phase 1 — feasibility: most-constrained-first construction + tabu repair.

Output must reach 0 hard-constraint violations before Phase 2 may run.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Dict, List

from app.solver.constraints.registry import (
    active_hard_constraints,
    check_all_hard,
    hard_violation_report,
)
from app.solver.domain import Placement, Problem, Timetable


@dataclass
class Phase1Result:
    timetable: Timetable
    feasible: bool
    iterations: int
    unplaced: List[int] = field(default_factory=list)
    report: List[dict] = field(default_factory=list)


def _feasible_placement_count(session, problem, timetable, hard, cap: int = 50) -> int:
    count = 0
    for placement in problem.all_placements(session):
        if check_all_hard(session, placement, problem, timetable, hard):
            count += 1
            if count >= cap:
                break
    return count


def order_sessions(problem: Problem, timetable: Timetable, hard) -> List[int]:
    """Brélaz-style most-constrained-first static ordering."""
    scored = []
    for sid, session in problem.sessions.items():
        feasible = _feasible_placement_count(session, problem, timetable, hard)
        scored.append((
            0 if session.is_locked else 1,      # locked first
            -session.duration,                   # long sessions first
            feasible,                            # fewest options first
            -problem.groups[session.group_id].size,
            sid,
        ))
    scored.sort()
    return [item[-1] for item in scored]


def greedy_construct(problem: Problem, timetable: Timetable, hard, rng) -> List[int]:
    unplaced = []
    for sid in order_sessions(problem, timetable, hard):
        session = problem.sessions[sid]
        placed = False
        if session.is_locked:
            placement = Placement(session.locked_day, session.locked_index, session.locked_room_id)
            if check_all_hard(session, placement, problem, timetable, hard):
                timetable.place(sid, placement)
                placed = True
        else:
            placements = list(problem.all_placements(session))
            rng.shuffle(placements)
            for placement in placements:
                if check_all_hard(session, placement, problem, timetable, hard):
                    timetable.place(sid, placement)
                    placed = True
                    break
        if not placed:
            unplaced.append(sid)
    return unplaced


def tabu_repair(problem: Problem, timetable: Timetable, unplaced: List[int], hard, rng) -> int:
    """Min-conflicts ejection with a tabu list, hard-violations-only objective."""
    max_iterations = int(problem.cfg("phase1_max_repair_iterations", 20000))
    tenure = int(problem.cfg("phase1_tabu_tenure", 25))
    tabu: Dict[tuple, int] = {}
    pending = list(unplaced)
    iteration = 0
    while pending and iteration < max_iterations:
        iteration += 1
        sid = pending.pop(rng.randrange(len(pending)))
        session = problem.sessions[sid]
        best_placement, best_conflicts = None, None
        placements = list(problem.all_placements(session))
        rng.shuffle(placements)
        for placement in placements:
            conflicts = timetable.conflicting_sessions(sid, placement)
            if any(problem.sessions[c].is_locked for c in conflicts):
                continue
            # non-conflict hard checks must hold even after ejection
            probe = [timetable.remove(c) for c in conflicts]
            ok = check_all_hard(session, placement, problem, timetable, hard)
            for c, pl in zip(conflicts, probe):
                timetable.place(c, pl)
            if not ok:
                continue
            key = (sid, placement.day, placement.index)
            if tabu.get(key, 0) > iteration and conflicts:
                continue
            score = len(conflicts)
            if best_conflicts is None or score < best_conflicts:
                best_placement, best_conflicts = placement, score
                if score == 0:
                    break
        if best_placement is None:
            pending.append(sid)
            continue
        ejected = timetable.conflicting_sessions(sid, best_placement)
        for c in ejected:
            timetable.remove(c)
            pending.append(c)
        timetable.place(sid, best_placement)
        tabu[(sid, best_placement.day, best_placement.index)] = iteration + tenure
    return iteration


def run_phase1(problem: Problem, rng: random.Random) -> Phase1Result:
    hard = active_hard_constraints(problem)
    timetable = Timetable(problem)
    unplaced = greedy_construct(problem, timetable, hard, rng)
    iterations = 0
    if unplaced:
        iterations = tabu_repair(problem, timetable, unplaced, hard, rng)
    remaining = timetable.unplaced_sessions()
    report = hard_violation_report(problem, timetable)
    feasible = not remaining and all(r["violations"] == 0 for r in report)
    return Phase1Result(
        timetable=timetable,
        feasible=feasible,
        iterations=iterations,
        unplaced=remaining,
        report=report,
    )
