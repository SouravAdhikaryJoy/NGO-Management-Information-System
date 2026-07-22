from app.solver.constraints.base import HardConstraint


class RoomOccupancy(HardConstraint):
    key = "H01_room_occupancy"
    description = "No two sessions may occupy the same room in the same timeslot."

    def check(self, session, placement, problem, existing_sessions):
        for i in range(placement.index, placement.index + session.duration):
            occupants = existing_sessions.room_busy.get((placement.room_id, placement.day, i))
            if occupants and occupants - {session.id}:
                return False
        return True
