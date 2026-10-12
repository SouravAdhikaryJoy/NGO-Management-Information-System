from app.solver.constraints.base import HardConstraint


class TeacherAvailabilityConstraint(HardConstraint):
    key = "H06_teacher_availability"
    description = "A session may not sit in a slot its teacher marked UNAVAILABLE."

    def check(self, session, placement, problem, existing_sessions):
        teacher = problem.teachers[session.teacher_id]
        for i in range(placement.index, placement.index + session.duration):
            if (placement.day, i) in teacher.unavailable:
                return False
        return True
