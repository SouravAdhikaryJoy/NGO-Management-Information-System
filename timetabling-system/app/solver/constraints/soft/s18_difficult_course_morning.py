from app.solver.constraints.base import SoftConstraint


class DifficultCourseMorning(SoftConstraint):
    key = "S18_difficult_course_morning"
    description = "Penalise difficult-course sessions starting after the morning window."

    def raw_penalty(self, problem, timetable):
        morning_end = int(problem.cfg("morning_end_slot", 3))
        penalty = 0
        for session_id, placement in timetable.placements.items():
            if problem.sessions[session_id].is_difficult and placement.index > morning_end:
                penalty += 1
        return float(penalty)
