import math

from app.solver.constraints.base import SoftConstraint
from app.solver.constraints.soft.util import active_days, total_slots


class GroupCompactDays(SoftConstraint):
    key = "S05_group_compact_days"
    description = "Penalise groups spread over more days than their load requires."

    def raw_penalty(self, problem, timetable):
        cap = int(problem.cfg("group_max_sessions_per_day", 6))
        penalty = 0
        for day_sets in timetable.group_slots.values():
            busy = total_slots(day_sets)
            if not busy:
                continue
            min_days = math.ceil(busy / cap)
            penalty += max(0, len(active_days(day_sets)) - min_days)
        return float(penalty)
