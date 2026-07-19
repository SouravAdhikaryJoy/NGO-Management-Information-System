from app.solver.domain import Placement
from app.solver.moves.base import Move, MoveOp, movable_sessions


class SingleSwap(Move):
    """Relocate one session to a random placement, or swap two sessions'
    placements (50/50)."""

    key = "single_swap"

    def propose(self, problem, timetable, rng):
        candidates = movable_sessions(problem, timetable)
        if not candidates:
            return None
        sid_a = rng.choice(candidates)
        old_a = timetable.placements[sid_a]
        if len(candidates) > 1 and rng.random() < 0.5:
            sid_b = rng.choice(candidates)
            if sid_b != sid_a:
                old_b = timetable.placements[sid_b]
                return MoveOp({sid_a: (old_a, old_b), sid_b: (old_b, old_a)})
        day = rng.choice(problem.days)
        index = rng.choice(problem.day_slot_indexes[day])
        room_id = rng.choice(list(problem.rooms))
        new = Placement(day, index, room_id)
        if new == old_a:
            return None
        return MoveOp({sid_a: (old_a, new)})
