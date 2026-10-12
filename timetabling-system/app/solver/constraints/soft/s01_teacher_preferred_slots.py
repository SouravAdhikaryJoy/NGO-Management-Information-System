from app.solver.constraints.base import SoftConstraint


class TeacherPreferredSlots(SoftConstraint):
    key = "S01_teacher_preferred_slots"
    description = "Penalise occupied slots outside a teacher's preferred set."

    def raw_penalty(self, problem, timetable):
        penalty = 0
        for teacher_id, day_sets in timetable.teacher_slots.items():
            teacher = problem.teachers[teacher_id]
            if not teacher.preferred:
                continue
            for day, indexes in day_sets.items():
                penalty += sum(1 for i in indexes if (day, i) not in teacher.preferred)
        return float(penalty)
