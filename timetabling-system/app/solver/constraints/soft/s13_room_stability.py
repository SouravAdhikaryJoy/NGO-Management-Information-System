from app.solver.constraints.base import SoftConstraint


class RoomStability(SoftConstraint):
    key = "S13_room_stability"
    description = "Penalise the number of distinct rooms a group uses."

    def raw_penalty(self, problem, timetable):
        rooms_by_group = {}
        for session_id, placement in timetable.placements.items():
            s = problem.sessions[session_id]
            rooms_by_group.setdefault(s.group_id, set()).add(placement.room_id)
        return float(sum(max(0, len(r) - 1) for r in rooms_by_group.values()))
