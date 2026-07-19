from app.solver.constraints.registry import (
    active_hard_constraints,
    check_all_hard,
    total_soft_penalty,
)
from app.solver.moves.base import Move, MoveOp, movable_sessions


class RuinRecreate(Move):
    """Large Neighbourhood Search: remove `ruin_fraction` random sessions and
    greedily re-insert each at its best-penalty feasible placement."""

    key = "ruin_recreate"

    def propose(self, problem, timetable, rng):
        candidates = movable_sessions(problem, timetable)
        if not candidates:
            return None
        fraction = float(problem.cfg("ruin_fraction", 0.1))
        count = max(1, min(len(candidates), int(len(candidates) * fraction)))
        ruined = rng.sample(candidates, count)

        hard = active_hard_constraints(problem)
        old_placements = {sid: timetable.placements[sid] for sid in ruined}
        for sid in ruined:
            timetable.remove(sid)

        changes = {}
        ok = True
        for sid in ruined:
            session = problem.sessions[sid]
            best, best_score = None, None
            placements = list(problem.all_placements(session))
            rng.shuffle(placements)
            for placement in placements:
                if not check_all_hard(session, placement, problem, timetable, hard):
                    continue
                timetable.place(sid, placement)
                score = total_soft_penalty(problem, timetable)
                timetable.remove(sid)
                if best_score is None or score < best_score:
                    best, best_score = placement, score
            if best is None:
                ok = False
                break
            timetable.place(sid, best)
            changes[sid] = (old_placements[sid], best)

        # restore original state; the engine owns apply/undo
        for sid in list(changes):
            timetable.remove(sid)
        for sid in ruined:
            if sid not in timetable.placements:
                timetable.place(sid, old_placements[sid])
        if not ok:
            return None
        return MoveOp(changes)
