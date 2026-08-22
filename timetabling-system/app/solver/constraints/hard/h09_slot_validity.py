from app.solver.constraints.base import HardConstraint


class SlotValidity(HardConstraint):
    key = "H09_slot_validity"
    description = "A session's start slot must be an existing, non-break timeslot."

    def check(self, session, placement, problem, existing_sessions):
        slot = problem.slots.get((placement.day, placement.index))
        return slot is not None and not slot.is_break
