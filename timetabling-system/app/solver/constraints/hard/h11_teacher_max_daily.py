from app.solver.constraints.base import HardConstraint


class TeacherMaxDaily(HardConstraint):
    key = "H11_teacher_max_daily"
    description = "A teacher may not exceed max_sessions_per_day occupied slots."

    def check(self, session, placement, problem, existing_sessions):
        teacher = problem.teachers[session.teacher_id]
        existing = existing_sessions.teacher_slots.get(session.teacher_id, {}).get(placement.day, set())
        new_indexes = set(range(placement.index, placement.index + session.duration))
        return len(existing | new_indexes) <= teacher.max_sessions_per_day
