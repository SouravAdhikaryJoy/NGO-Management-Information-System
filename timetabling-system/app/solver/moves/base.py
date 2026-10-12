"""Move interface for Phase 2 refinement.

A move proposes a reassignment of one or more sessions. The engine applies it,
validates the hard invariant, evaluates the soft objective, and either keeps or
undoes it. Moves therefore return a MoveOp describing old and new placements.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Optional

from app.solver.domain import Placement, Problem, Timetable


@dataclass
class MoveOp:
    # session_id -> (old placement or None, new placement or None)
    changes: Dict[int, tuple]

    def apply(self, timetable: Timetable) -> None:
        for session_id, (old, _new) in self.changes.items():
            if old is not None:
                timetable.remove(session_id)
        for session_id, (_old, new) in self.changes.items():
            if new is not None:
                timetable.place(session_id, new)

    def undo(self, timetable: Timetable) -> None:
        for session_id, (_old, new) in self.changes.items():
            if new is not None:
                timetable.remove(session_id)
        for session_id, (old, _new) in self.changes.items():
            if old is not None:
                timetable.place(session_id, old)

    def moved_session_ids(self):
        return [sid for sid, (_o, new) in self.changes.items() if new is not None]


class Move(ABC):
    key: str = ""

    @abstractmethod
    def propose(self, problem: Problem, timetable: Timetable, rng) -> Optional[MoveOp]:
        """Return a candidate MoveOp, or None if no move could be built."""


def movable_sessions(problem: Problem, timetable: Timetable):
    return [
        sid for sid in timetable.placements
        if not problem.sessions[sid].is_locked
    ]
