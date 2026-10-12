from app.solver.constraints.base import SoftConstraint

DEFAULT_MISSING_PREFERENCE = 3


class TeacherCoursePreferencePenalty(SoftConstraint):
    key = "S02_teacher_course_preference"
    description = "Penalise sessions taught by teachers with low course preference."

    def raw_penalty(self, problem, timetable):
        penalty = 0
        for session_id in timetable.placements:
            s = problem.sessions[session_id]
            pref = problem.teacher_course_pref.get(
                (s.teacher_id, s.course_id), DEFAULT_MISSING_PREFERENCE
            )
            penalty += max(0, 5 - pref)
        return float(penalty)
