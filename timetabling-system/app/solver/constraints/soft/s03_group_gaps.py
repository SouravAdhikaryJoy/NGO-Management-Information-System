from app.solver.constraints.base import SoftConstraint
from app.solver.constraints.soft.util import day_gaps


class GroupGaps(SoftConstraint):
    key = "S03_group_gaps"
    description = "Penalise idle slots inside a class group's day."

    def raw_penalty(self, problem, timetable):
        return float(
            sum(
                day_gaps(indexes)
                for day_sets in timetable.group_slots.values()
                for indexes in day_sets.values()
            )
        )
