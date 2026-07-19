from app.solver.constraints.base import SoftConstraint


class GroupLoadBalance(SoftConstraint):
    key = "S17_group_load_balance"
    description = "Penalise uneven daily load across a group's active days."

    def raw_penalty(self, problem, timetable):
        penalty = 0
        for day_sets in timetable.group_slots.values():
            counts = [len(s) for s in day_sets.values() if s]
            if len(counts) >= 2:
                penalty += max(counts) - min(counts)
        return float(penalty)
