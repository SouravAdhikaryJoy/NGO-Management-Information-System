"""Phase 2 — quality: hyper-heuristic move selection + pluggable acceptance.

Invariant: no accepted move may reintroduce a hard-constraint violation. Every
candidate is validated against all active hard constraints before evaluation.
"""

from __future__ import annotations

import random
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Dict, List

from app.solver.acceptance import build_acceptance
from app.solver.constraints.registry import (
    active_hard_constraints,
    total_soft_penalty,
)
from app.solver.domain import Problem, Timetable
from app.solver.moves.day_shift import DayShift
from app.solver.moves.kempe_chain import KempeChain
from app.solver.moves.ruin_recreate import RuinRecreate
from app.solver.moves.swap import SingleSwap

MOVES = [SingleSwap(), KempeChain(), RuinRecreate(), DayShift()]


@dataclass
class Phase2Result:
    timetable: Timetable
    initial_penalty: float
    final_penalty: float
    iterations: int
    accepted: int
    move_stats: Dict[str, dict] = field(default_factory=dict)


class HyperHeuristicSelector:
    """Weighted-random move selection by recent success rate."""

    def __init__(self, moves, window: int):
        self.moves = moves
        self.history = {m.key: deque(maxlen=max(1, window)) for m in moves}

    def select(self, rng):
        weights = []
        for m in self.moves:
            h = self.history[m.key]
            rate = (sum(h) / len(h)) if h else 0.5
            weights.append(0.05 + rate)  # floor keeps every move type alive
        return rng.choices(self.moves, weights=weights, k=1)[0]

    def record(self, move, success: bool):
        self.history[move.key].append(1 if success else 0)


def _op_is_hard_feasible(op, problem, timetable, hard) -> bool:
    """Validate every moved session against all hard constraints, with the
    move applied and the session itself lifted out during its own check."""
    for sid in op.moved_session_ids():
        placement = timetable.remove(sid)
        ok = all(
            c.check(problem.sessions[sid], placement, problem, timetable) for c in hard
        )
        timetable.place(sid, placement)
        if not ok:
            return False
    return True


def run_phase2(problem: Problem, timetable: Timetable, rng: random.Random) -> Phase2Result:
    hard = active_hard_constraints(problem)
    time_budget = float(problem.cfg("phase2_time_budget_seconds", 60))
    iteration_budget = int(problem.cfg("phase2_iteration_budget", 200000))
    window = int(problem.cfg("hyper_heuristic_window", 100))

    current_cost = total_soft_penalty(problem, timetable)
    initial_cost = current_cost
    acceptance = build_acceptance(problem.config, current_cost)
    selector = HyperHeuristicSelector(MOVES, window)

    best_timetable = timetable.clone()
    best_cost = current_cost

    start = time.monotonic()
    iterations = accepted = 0
    attempts: Dict[str, int] = {m.key: 0 for m in MOVES}
    accepts: Dict[str, int] = {m.key: 0 for m in MOVES}

    while iterations < iteration_budget and (time.monotonic() - start) < time_budget:
        iterations += 1
        move = selector.select(rng)
        attempts[move.key] += 1
        op = move.propose(problem, timetable, rng)
        if op is None:
            selector.record(move, False)
            continue
        try:
            op.apply(timetable)
        except AssertionError:
            selector.record(move, False)
            continue
        if not _op_is_hard_feasible(op, problem, timetable, hard):
            op.undo(timetable)
            selector.record(move, False)
            continue
        candidate_cost = total_soft_penalty(problem, timetable)
        if acceptance.accept(candidate_cost, current_cost, rng):
            current_cost = candidate_cost
            acceptance.on_accept(current_cost)
            accepted += 1
            accepts[move.key] += 1
            selector.record(move, True)
            if candidate_cost < best_cost:
                best_cost = candidate_cost
                best_timetable = timetable.clone()
        else:
            op.undo(timetable)
            selector.record(move, False)

    move_stats = {
        key: {"attempts": attempts[key], "accepted": accepts[key]} for key in attempts
    }
    return Phase2Result(
        timetable=best_timetable,
        initial_penalty=initial_cost,
        final_penalty=best_cost,
        iterations=iterations,
        accepted=accepted,
        move_stats=move_stats,
    )
