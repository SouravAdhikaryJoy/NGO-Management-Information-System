from app.solver.constraints.base import SoftConstraint


class RoomUtilizationFit(SoftConstraint):
    key = "S15_room_utilization_fit"
    description = "Penalise sessions in rooms far larger than the group."

    def raw_penalty(self, problem, timetable):
        threshold = float(problem.cfg("room_fit_slack_threshold", 2.0))
        penalty = 0
        for session_id, placement in timetable.placements.items():
            s = problem.sessions[session_id]
            size = problem.groups[s.group_id].size
            capacity = problem.rooms[placement.room_id].capacity
            if size > 0 and capacity / size > threshold:
                penalty += 1
        return float(penalty)
