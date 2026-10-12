from app.solver.constraints.base import SoftConstraint
from app.solver.constraints.soft.util import consecutive_runs


class TeacherBackToBack(SoftConstraint):
    key = "S19_teacher_back_to_back"
    description = (
        "Respect declared back-to-back preference: avoiders pay per adjacency, "
        "preferrers pay per isolated slot-run on multi-session days."
    )

    def raw_penalty(self, problem, timetable):
        penalty = 0
        for teacher_id, day_sets in timetable.teacher_slots.items():
            pref = problem.teachers[teacher_id].prefers_back_to_back
            if pref is None:
                continue
            for indexes in day_sets.values():
                if not indexes:
                    continue
                runs = consecutive_runs(indexes)
                if pref is False:
                    penalty += sum(r - 1 for r in runs)
                elif len(indexes) >= 2:
                    penalty += sum(1 for r in runs if r == 1)
        return float(penalty)
