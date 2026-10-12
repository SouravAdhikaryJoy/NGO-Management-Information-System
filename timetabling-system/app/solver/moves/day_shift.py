from app.solver.domain import Placement
from app.solver.moves.base import Move, MoveOp, movable_sessions


class DayShift(Move):
    """Move one session to another day, keeping (when possible) its slot index
    and room, otherwise a random slot on the target day."""

    key = "day_shift"

    def propose(self, problem, timetable, rng):
        candidates = movable_sessions(problem, timetable)
        if not candidates or len(problem.days) < 2:
            return None
        sid = rng.choice(candidates)
        old = timetable.placements[sid]
        other_days = [d for d in problem.days if d != old.day]
        day = rng.choice(other_days)
        indexes = problem.day_slot_indexes[day]
        index = old.index if old.index in indexes else rng.choice(indexes)
        return MoveOp({sid: (old, Placement(day, index, old.room_id))})
