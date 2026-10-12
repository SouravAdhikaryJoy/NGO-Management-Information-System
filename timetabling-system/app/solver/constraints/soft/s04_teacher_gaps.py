from app.solver.constraints.base import SoftConstraint
from app.solver.constraints.soft.util import day_gaps


class TeacherGaps(SoftConstraint):
    key = "S04_teacher_gaps"
    description = "Penalise idle slots inside a teacher's day."

    def raw_penalty(self, problem, timetable):
        return float(
            sum(
                day_gaps(indexes)
                for day_sets in timetable.teacher_slots.values()
                for indexes in day_sets.values()
            )
        )
