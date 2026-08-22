from app.solver.constraints.base import HardConstraint


class SessionCompleteness(HardConstraint):
    key = "H08_session_completeness"
    description = "Every generated session must be placed in the timetable."

    def check(self, session, placement, problem, existing_sessions):
        # A concrete placement trivially satisfies completeness for that session;
        # this constraint bites at the whole-timetable level (unplaced sessions).
        return placement is not None

    def violations(self, problem, timetable):
        return len(timetable.unplaced_sessions())
