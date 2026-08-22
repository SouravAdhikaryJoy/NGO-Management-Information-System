from app.solver.constraints.base import SoftConstraint
from app.solver.constraints.soft.util import excess_over_max_run


class TeacherMaxConsecutive(SoftConstraint):
    key = "S09_teacher_max_consecutive"
    description = "Penalise teacher slots beyond max_consecutive_teacher in a run."

    def raw_penalty(self, problem, timetable):
        max_run = int(problem.cfg("max_consecutive_teacher", 3))
        return float(
            sum(
                excess_over_max_run(indexes, max_run)
                for day_sets in timetable.teacher_slots.values()
                for indexes in day_sets.values()
            )
        )
