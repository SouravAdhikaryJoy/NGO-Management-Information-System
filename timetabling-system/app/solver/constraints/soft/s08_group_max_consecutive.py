from app.solver.constraints.base import SoftConstraint
from app.solver.constraints.soft.util import excess_over_max_run


class GroupMaxConsecutive(SoftConstraint):
    key = "S08_group_max_consecutive"
    description = "Penalise group slots beyond max_consecutive_group in a run."

    def raw_penalty(self, problem, timetable):
        max_run = int(problem.cfg("max_consecutive_group", 3))
        return float(
            sum(
                excess_over_max_run(indexes, max_run)
                for day_sets in timetable.group_slots.values()
                for indexes in day_sets.values()
            )
        )
