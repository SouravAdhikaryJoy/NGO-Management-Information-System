from app.solver.constraints.base import HardConstraint


class RoomCapacity(HardConstraint):
    key = "H04_room_capacity"
    description = "Room capacity must be >= class group size."

    def check(self, session, placement, problem, existing_sessions):
        room = problem.rooms.get(placement.room_id)
        if room is None:
            return False
        return room.capacity >= problem.groups[session.group_id].size
