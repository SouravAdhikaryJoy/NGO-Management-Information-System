from app.solver.constraints.base import HardConstraint


class GroupMaxDaily(HardConstraint):
    key = "H12_group_max_daily"
    description = "A class group may not exceed group_max_sessions_per_day occupied slots."

    def check(self, session, placement, problem, existing_sessions):
        cap = int(problem.cfg("group_max_sessions_per_day", 6))
        existing = existing_sessions.group_slots.get(session.group_id, {}).get(placement.day, set())
        new_indexes = set(range(placement.index, placement.index + session.duration))
        return len(existing | new_indexes) <= cap
