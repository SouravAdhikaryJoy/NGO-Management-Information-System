from app.solver.constraints.base import HardConstraint


class LockedSession(HardConstraint):
    key = "H14_locked_session"
    description = "A locked session must remain at exactly its pinned day/slot/room."

    def check(self, session, placement, problem, existing_sessions):
        if not session.is_locked:
            return True
        return (
            placement.day == session.locked_day
            and placement.index == session.locked_index
            and placement.room_id == session.locked_room_id
        )
