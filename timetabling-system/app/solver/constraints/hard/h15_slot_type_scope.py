from app.solver.constraints.base import HardConstraint


class SlotTypeScope(HardConstraint):
    key = "H15_slot_type_scope"
    description = (
        "A session may only occupy slots whose fixed timeslot pool allows its "
        "session type (e.g. labs only in lab-designated slots)."
    )

    def check(self, session, placement, problem, existing_sessions):
        for i in range(placement.index, placement.index + session.duration):
            slot = problem.slots.get((placement.day, i))
            if slot is None:
                return False
            if slot.allowed_types is not None and session.session_type not in slot.allowed_types:
                return False
        return True
