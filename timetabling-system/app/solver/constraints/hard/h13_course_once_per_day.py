from app.solver.constraints.base import HardConstraint


class CourseOncePerDay(HardConstraint):
    key = "H13_course_once_per_day"
    description = "The same course may meet at most once per day for a class group."

    def check(self, session, placement, problem, existing_sessions):
        # the session itself is lifted out of the timetable during its check,
        # so any counted session under this key is a different one
        key = (session.course_id, session.group_id, placement.day)
        return existing_sessions.course_group_day.get(key, 0) == 0
