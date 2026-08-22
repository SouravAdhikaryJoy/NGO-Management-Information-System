from app.solver.constraints.base import SoftConstraint


class LunchBreak(SoftConstraint):
    key = "S12_lunch_break"
    description = "Penalise group-days whose whole lunch window is occupied."

    def raw_penalty(self, problem, timetable):
        start = int(problem.cfg("lunch_start_slot", 4))
        end = int(problem.cfg("lunch_end_slot", 5))
        window = set(range(start, end + 1))
        penalty = 0
        for day_sets in timetable.group_slots.values():
            for indexes in day_sets.values():
                if window and window <= indexes:
                    penalty += 1
        return float(penalty)
