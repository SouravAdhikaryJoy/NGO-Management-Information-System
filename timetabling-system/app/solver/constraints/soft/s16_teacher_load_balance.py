from app.solver.constraints.base import SoftConstraint


class TeacherLoadBalance(SoftConstraint):
    key = "S16_teacher_load_balance"
    description = "Penalise uneven daily load across a teacher's active days."

    def raw_penalty(self, problem, timetable):
        penalty = 0
        for day_sets in timetable.teacher_slots.values():
            counts = [len(s) for s in day_sets.values() if s]
            if len(counts) >= 2:
                penalty += max(counts) - min(counts)
        return float(penalty)
