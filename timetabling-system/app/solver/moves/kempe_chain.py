from app.solver.domain import Placement
from app.solver.moves.base import Move, MoveOp


class KempeChain(Move):
    """Kempe-chain interchange between two timeslot columns.

    Pick two (day, index) columns; build the conflict graph between their
    sessions (edges = shared teacher or group); swap one connected chain
    between the columns. Rooms are kept, so room-occupancy feasibility is
    re-checked by the engine like any other move."""

    key = "kempe_chain"

    def propose(self, problem, timetable, rng):
        columns = [
            (day, index)
            for day in problem.days
            for index in problem.day_slot_indexes[day]
        ]
        if len(columns) < 2:
            return None
        (day_a, idx_a), (day_b, idx_b) = rng.sample(columns, 2)

        def column_sessions(day, index):
            found = set()
            for sid, pl in timetable.placements.items():
                s = problem.sessions[sid]
                if pl.day == day and pl.index <= index < pl.index + s.duration:
                    if not s.is_locked and s.duration == 1:
                        found.add(sid)
            return found

        col_a = column_sessions(day_a, idx_a)
        col_b = column_sessions(day_b, idx_b)
        pool = col_a | col_b
        if not pool:
            return None

        # conflict graph: sessions in opposite columns sharing teacher or group
        def conflicts(x, y):
            sx, sy = problem.sessions[x], problem.sessions[y]
            return sx.teacher_id == sy.teacher_id or sx.group_id == sy.group_id

        start = rng.choice(sorted(pool))
        chain, frontier = {start}, [start]
        while frontier:
            current = frontier.pop()
            current_col = col_a if current in col_a else col_b
            opposite = col_b if current_col is col_a else col_a
            for other in opposite:
                if other not in chain and conflicts(current, other):
                    chain.add(other)
                    frontier.append(other)

        changes = {}
        for sid in chain:
            old = timetable.placements[sid]
            if sid in col_a:
                new = Placement(day_b, idx_b, old.room_id)
            else:
                new = Placement(day_a, idx_a, old.room_id)
            changes[sid] = (old, new)
        return MoveOp(changes)
