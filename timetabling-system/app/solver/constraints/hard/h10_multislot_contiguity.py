from app.solver.constraints.base import HardConstraint


class MultiSlotContiguity(HardConstraint):
    key = "H10_multislot_contiguity"
    description = (
        "A multi-slot session must occupy contiguous, existing, non-break slots "
        "within a single day."
    )

    def check(self, session, placement, problem, existing_sessions):
        for i in range(placement.index, placement.index + session.duration):
            slot = problem.slots.get((placement.day, i))
            if slot is None or slot.is_break:
                return False
        return True
