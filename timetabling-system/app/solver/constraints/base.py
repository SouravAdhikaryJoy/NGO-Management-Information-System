"""Common constraint interfaces (design doc section 2).

Hard constraints answer "may this session sit at this placement given the rest
of the timetable?"; soft constraints score a whole timetable. The solver only
ever iterates registered constraint instances — no constraint logic lives in
the solver loop itself.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.solver.domain import Placement, Problem, SessionData, Timetable


class HardConstraint(ABC):
    key: str = ""
    description: str = ""

    @abstractmethod
    def check(
        self,
        session: SessionData,
        placement: Placement,
        problem: Problem,
        existing_sessions: Timetable,
    ) -> bool:
        """True if placing `session` at `placement` satisfies this constraint,
        given the other placements in `existing_sessions` (the session itself
        must NOT currently be placed in it)."""

    def violations(self, problem: Problem, timetable: Timetable) -> int:
        """Count violations over a full timetable. Default: re-check each
        placed session against the rest."""
        count = 0
        for session_id in list(timetable.placements):
            placement = timetable.remove(session_id)
            if not self.check(problem.sessions[session_id], placement, problem, timetable):
                count += 1
            timetable.place(session_id, placement)
        return count


class SoftConstraint(ABC):
    key: str = ""
    description: str = ""

    @abstractmethod
    def raw_penalty(self, problem: Problem, timetable: Timetable) -> float:
        """Unweighted penalty units for the whole timetable."""

    def penalty(self, problem: Problem, timetable: Timetable) -> float:
        """Weighted penalty contribution (weight read from ConstraintWeight)."""
        row = problem.weights.get(self.key)
        if row is None or not row.enabled:
            return 0.0
        return row.weight * self.raw_penalty(problem, timetable)
