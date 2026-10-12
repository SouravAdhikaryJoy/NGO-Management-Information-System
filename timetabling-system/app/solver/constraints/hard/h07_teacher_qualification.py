from app.solver.constraints.base import HardConstraint


class TeacherQualification(HardConstraint):
    key = "H07_teacher_qualification"
    description = "The session's teacher must be qualified for its course."

    def check(self, session, placement, problem, existing_sessions):
        return session.teacher_id in problem.qualified_teachers.get(session.course_id, set())
