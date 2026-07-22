from app.solver.constraints.base import HardConstraint


class GroupClash(HardConstraint):
    key = "H03_group_clash"
    description = "A class group cannot attend two sessions in overlapping timeslots."

    def check(self, session, placement, problem, existing_sessions):
        for i in range(placement.index, placement.index + session.duration):
            occupants = existing_sessions.group_busy.get((session.group_id, placement.day, i))
            if occupants and occupants - {session.id}:
                return False
        return True
