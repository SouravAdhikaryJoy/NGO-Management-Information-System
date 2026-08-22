from app.solver.constraints.base import HardConstraint


class RoomTypeMatch(HardConstraint):
    key = "H05_room_type_match"
    description = "The room's type must match the session's required room type."

    def check(self, session, placement, problem, existing_sessions):
        room = problem.rooms.get(placement.room_id)
        if room is None:
            return False
        return room.room_type_id == session.required_room_type_id
