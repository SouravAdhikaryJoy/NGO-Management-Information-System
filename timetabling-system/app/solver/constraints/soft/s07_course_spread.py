from itertools import combinations

from app.solver.constraints.base import SoftConstraint


class CourseSpread(SoftConstraint):
    key = "S07_course_spread"
    description = "Penalise same course+group sessions on adjacent days."

    def raw_penalty(self, problem, timetable):
        by_course_group = {}
        for session_id, placement in timetable.placements.items():
            s = problem.sessions[session_id]
            by_course_group.setdefault((s.course_id, s.group_id), []).append(placement.day)
        day_pos = {d: i for i, d in enumerate(problem.days)}
        penalty = 0
        for days in by_course_group.values():
            for a, b in combinations(days, 2):
                if abs(day_pos.get(a, 0) - day_pos.get(b, 0)) == 1:
                    penalty += 1
        return float(penalty)
