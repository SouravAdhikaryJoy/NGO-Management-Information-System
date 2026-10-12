from app.solver.constraints.base import SoftConstraint


class EarlySlotAvoidance(SoftConstraint):
    key = "S10_early_slot_avoidance"
    description = "Penalise sessions occupying the first slot of a day."

    def raw_penalty(self, problem, timetable):
        penalty = 0
        for session_id, placement in timetable.placements.items():
            indexes = problem.day_slot_indexes.get(placement.day)
            if not indexes:
                continue
            s = problem.sessions[session_id]
            if placement.index <= indexes[0] < placement.index + s.duration:
                penalty += 1
        return float(penalty)
