"""Constraint registry — the single place a new constraint gets wired in.

Adding a constraint = new class file + one entry here. The solver only ever
iterates these lists.
"""

from app.solver.constraints.hard.h01_room_occupancy import RoomOccupancy
from app.solver.constraints.hard.h02_teacher_clash import TeacherClash
from app.solver.constraints.hard.h03_group_clash import GroupClash
from app.solver.constraints.hard.h04_room_capacity import RoomCapacity
from app.solver.constraints.hard.h05_room_type_match import RoomTypeMatch
from app.solver.constraints.hard.h06_teacher_availability import TeacherAvailabilityConstraint
from app.solver.constraints.hard.h07_teacher_qualification import TeacherQualification
from app.solver.constraints.hard.h08_session_completeness import SessionCompleteness
from app.solver.constraints.hard.h09_slot_validity import SlotValidity
from app.solver.constraints.hard.h10_multislot_contiguity import MultiSlotContiguity
from app.solver.constraints.hard.h11_teacher_max_daily import TeacherMaxDaily
from app.solver.constraints.hard.h12_group_max_daily import GroupMaxDaily
from app.solver.constraints.hard.h13_course_once_per_day import CourseOncePerDay
from app.solver.constraints.hard.h14_locked_session import LockedSession
from app.solver.constraints.soft.s01_teacher_preferred_slots import TeacherPreferredSlots
from app.solver.constraints.soft.s02_teacher_course_preference import TeacherCoursePreferencePenalty
from app.solver.constraints.soft.s03_group_gaps import GroupGaps
from app.solver.constraints.soft.s04_teacher_gaps import TeacherGaps
from app.solver.constraints.soft.s05_group_compact_days import GroupCompactDays
from app.solver.constraints.soft.s06_teacher_compact_days import TeacherCompactDays
from app.solver.constraints.soft.s07_course_spread import CourseSpread
from app.solver.constraints.soft.s08_group_max_consecutive import GroupMaxConsecutive
from app.solver.constraints.soft.s09_teacher_max_consecutive import TeacherMaxConsecutive
from app.solver.constraints.soft.s10_early_slot_avoidance import EarlySlotAvoidance
from app.solver.constraints.soft.s11_late_slot_avoidance import LateSlotAvoidance
from app.solver.constraints.soft.s12_lunch_break import LunchBreak
from app.solver.constraints.soft.s13_room_stability import RoomStability
from app.solver.constraints.soft.s14_building_travel import BuildingTravel
from app.solver.constraints.soft.s15_room_utilization_fit import RoomUtilizationFit
from app.solver.constraints.soft.s16_teacher_load_balance import TeacherLoadBalance
from app.solver.constraints.soft.s17_group_load_balance import GroupLoadBalance
from app.solver.constraints.soft.s18_difficult_course_morning import DifficultCourseMorning
from app.solver.constraints.soft.s19_teacher_back_to_back import TeacherBackToBack

HARD_CONSTRAINTS = [
    RoomOccupancy(),
    TeacherClash(),
    GroupClash(),
    RoomCapacity(),
    RoomTypeMatch(),
    TeacherAvailabilityConstraint(),
    TeacherQualification(),
    SessionCompleteness(),
    SlotValidity(),
    MultiSlotContiguity(),
    TeacherMaxDaily(),
    GroupMaxDaily(),
    CourseOncePerDay(),
    LockedSession(),
]

SOFT_CONSTRAINTS = [
    TeacherPreferredSlots(),
    TeacherCoursePreferencePenalty(),
    GroupGaps(),
    TeacherGaps(),
    GroupCompactDays(),
    TeacherCompactDays(),
    CourseSpread(),
    GroupMaxConsecutive(),
    TeacherMaxConsecutive(),
    EarlySlotAvoidance(),
    LateSlotAvoidance(),
    LunchBreak(),
    RoomStability(),
    BuildingTravel(),
    RoomUtilizationFit(),
    TeacherLoadBalance(),
    GroupLoadBalance(),
    DifficultCourseMorning(),
    TeacherBackToBack(),
]


def active_hard_constraints(problem):
    """Hard checks honouring ConstraintWeight.is_hard/enabled overrides.

    A constraint with no weight row stays active (safe default)."""
    active = []
    for c in HARD_CONSTRAINTS:
        row = problem.weights.get(c.key)
        if row is None or (row.enabled and row.is_hard):
            active.append(c)
    return active


def active_soft_constraints(problem):
    active = []
    for c in SOFT_CONSTRAINTS:
        row = problem.weights.get(c.key)
        if row is None or row.enabled:
            active.append(c)
    return active


def check_all_hard(session, placement, problem, timetable, constraints=None):
    """True iff every active hard constraint accepts the placement."""
    for c in constraints or active_hard_constraints(problem):
        if not c.check(session, placement, problem, timetable):
            return False
    return True


def failing_hard_keys(session, placement, problem, timetable):
    return [
        c.key
        for c in active_hard_constraints(problem)
        if not c.check(session, placement, problem, timetable)
    ]


def total_soft_penalty(problem, timetable):
    return sum(c.penalty(problem, timetable) for c in active_soft_constraints(problem))


def soft_penalty_breakdown(problem, timetable):
    rows = []
    for c in SOFT_CONSTRAINTS:
        row = problem.weights.get(c.key)
        raw = c.raw_penalty(problem, timetable)
        weight = row.weight if row else 0.0
        tier = row.tier if row else 0
        enabled = row.enabled if row else True
        rows.append({
            "key": c.key,
            "description": c.description,
            "tier": tier,
            "weight": weight,
            "enabled": enabled,
            "raw_penalty": raw,
            "weighted_penalty": weight * raw if enabled else 0.0,
        })
    return rows


def hard_violation_report(problem, timetable):
    return [
        {"key": c.key, "description": c.description, "violations": c.violations(problem, timetable)}
        for c in HARD_CONSTRAINTS
    ]
