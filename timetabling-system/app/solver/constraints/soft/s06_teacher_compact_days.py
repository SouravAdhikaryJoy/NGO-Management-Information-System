import math

from app.solver.constraints.base import SoftConstraint
from app.solver.constraints.soft.util import active_days, total_slots


class TeacherCompactDays(SoftConstraint):
    key = "S06_teacher_compact_days"
    description = "Penalise teachers spread over more days than their load requires."

    def raw_penalty(self, problem, timetable):
        penalty = 0
        for teacher_id, day_sets in timetable.teacher_slots.items():
            busy = total_slots(day_sets)
            if not busy:
                continue
            cap = problem.teachers[teacher_id].max_sessions_per_day
            min_days = math.ceil(busy / cap)
            penalty += max(0, len(active_days(day_sets)) - min_days)
        return float(penalty)
