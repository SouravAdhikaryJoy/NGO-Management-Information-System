from app.solver.constraints.base import HardConstraint


class TeacherClash(HardConstraint):
    key = "H02_teacher_clash"
    description = "A teacher cannot teach two sessions in overlapping timeslots."

    def check(self, session, placement, problem, existing_sessions):
        for i in range(placement.index, placement.index + session.duration):
            occupants = existing_sessions.teacher_busy.get((session.teacher_id, placement.day, i))
            if occupants and occupants - {session.id}:
                return False
        return True
