"""Per-constraint unit tests for all 19 soft constraints (build order #5)."""

from app.solver.constraints.soft.s01_teacher_preferred_slots import TeacherPreferredSlots
from app.solver.constraints.soft.s02_teacher_course_preference import (
    TeacherCoursePreferencePenalty,
)
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
from app.solver.domain import GroupData, TeacherData
from tests.conftest import default_config, mk_problem, mk_session, place_all


def two_sessions(**kwargs):
    return [
        mk_session(1, course=101, **kwargs),
        mk_session(2, course=102, **kwargs),
    ]


def test_s01_teacher_preferred_slots():
    teachers = {1: TeacherData(1, "T1", 4, 18, preferred=frozenset({("MON", 1)}))}
    s = mk_session(1, teacher=1)
    problem = mk_problem([s], teachers=teachers)
    assert TeacherPreferredSlots().raw_penalty(
        problem, place_all(problem, {1: ("MON", 2, 1)})) == 1
    assert TeacherPreferredSlots().raw_penalty(
        problem, place_all(problem, {1: ("MON", 1, 1)})) == 0


def test_s02_teacher_course_preference():
    s = mk_session(1, course=101, teacher=1)
    problem = mk_problem([s], prefs={(1, 101): 3})
    assert TeacherCoursePreferencePenalty().raw_penalty(
        problem, place_all(problem, {1: ("MON", 1, 1)})) == 2
    problem.teacher_course_pref[(1, 101)] = 5
    assert TeacherCoursePreferencePenalty().raw_penalty(
        problem, place_all(problem, {1: ("MON", 1, 1)})) == 0


def test_s03_group_gaps():
    sessions = two_sessions(group=1, teacher=1)
    problem = mk_problem(sessions)
    gapped = place_all(problem, {1: ("MON", 1, 1), 2: ("MON", 3, 1)})
    assert GroupGaps().raw_penalty(problem, gapped) == 1
    tight = place_all(problem, {1: ("MON", 1, 1), 2: ("MON", 2, 1)})
    assert GroupGaps().raw_penalty(problem, tight) == 0


def test_s04_teacher_gaps():
    sessions = two_sessions(teacher=1, group=1)
    problem = mk_problem(sessions)
    gapped = place_all(problem, {1: ("MON", 1, 1), 2: ("MON", 4, 1)})
    assert TeacherGaps().raw_penalty(problem, gapped) == 2


def test_s05_group_compact_days():
    sessions = two_sessions(group=1, teacher=1)
    problem = mk_problem(sessions)
    spread = place_all(problem, {1: ("MON", 1, 1), 2: ("TUE", 1, 1)})
    assert GroupCompactDays().raw_penalty(problem, spread) == 1
    compact = place_all(problem, {1: ("MON", 1, 1), 2: ("MON", 2, 1)})
    assert GroupCompactDays().raw_penalty(problem, compact) == 0


def test_s06_teacher_compact_days():
    sessions = two_sessions(teacher=1, group=1)
    problem = mk_problem(sessions)
    spread = place_all(problem, {1: ("MON", 1, 1), 2: ("WED", 1, 1)})
    assert TeacherCompactDays().raw_penalty(problem, spread) == 1


def test_s07_course_spread():
    s1 = mk_session(1, course=101, group=1)
    s2 = mk_session(2, course=101, group=1)
    problem = mk_problem([s1, s2])
    adjacent = place_all(problem, {1: ("MON", 1, 1), 2: ("TUE", 1, 1)})
    assert CourseSpread().raw_penalty(problem, adjacent) == 1
    spread = place_all(problem, {1: ("MON", 1, 1), 2: ("WED", 1, 1)})
    assert CourseSpread().raw_penalty(problem, spread) == 0


def test_s08_group_max_consecutive():
    sessions = [mk_session(i, course=100 + i, group=1, teacher=1) for i in (1, 2, 3)]
    problem = mk_problem(sessions, config=default_config(max_consecutive_group=2))
    run3 = place_all(problem, {1: ("MON", 1, 1), 2: ("MON", 2, 1), 3: ("MON", 3, 1)})
    assert GroupMaxConsecutive().raw_penalty(problem, run3) == 1


def test_s09_teacher_max_consecutive():
    sessions = [mk_session(i, course=100 + i, group=1, teacher=1) for i in (1, 2, 3)]
    problem = mk_problem(sessions, config=default_config(max_consecutive_teacher=2))
    run3 = place_all(problem, {1: ("MON", 1, 1), 2: ("MON", 2, 1), 3: ("MON", 3, 1)})
    assert TeacherMaxConsecutive().raw_penalty(problem, run3) == 1


def test_s10_early_slot_avoidance():
    s = mk_session(1)
    problem = mk_problem([s])
    assert EarlySlotAvoidance().raw_penalty(problem, place_all(problem, {1: ("MON", 1, 1)})) == 1
    assert EarlySlotAvoidance().raw_penalty(problem, place_all(problem, {1: ("MON", 2, 1)})) == 0


def test_s11_late_slot_avoidance():
    s = mk_session(1)
    problem = mk_problem([s])
    assert LateSlotAvoidance().raw_penalty(problem, place_all(problem, {1: ("MON", 4, 1)})) == 1
    assert LateSlotAvoidance().raw_penalty(problem, place_all(problem, {1: ("MON", 2, 1)})) == 0


def test_s12_lunch_break():
    sessions = two_sessions(group=1, teacher=1)
    problem = mk_problem(
        sessions, config=default_config(lunch_start_slot=2, lunch_end_slot=3)
    )
    blocked = place_all(problem, {1: ("MON", 2, 1), 2: ("MON", 3, 1)})
    assert LunchBreak().raw_penalty(problem, blocked) == 1
    free = place_all(problem, {1: ("MON", 1, 1), 2: ("MON", 3, 1)})
    assert LunchBreak().raw_penalty(problem, free) == 0


def test_s13_room_stability():
    sessions = two_sessions(group=1, teacher=1)
    problem = mk_problem(sessions)
    two_rooms = place_all(problem, {1: ("MON", 1, 1), 2: ("MON", 2, 2)})
    assert RoomStability().raw_penalty(problem, two_rooms) == 1
    one_room = place_all(problem, {1: ("MON", 1, 1), 2: ("MON", 2, 1)})
    assert RoomStability().raw_penalty(problem, one_room) == 0


def test_s14_building_travel():
    sessions = two_sessions(group=1, teacher=1)
    problem = mk_problem(sessions)
    # R1 is in building 1, R2 in building 2, back-to-back slots
    travel = place_all(problem, {1: ("MON", 1, 1), 2: ("MON", 2, 2)})
    assert BuildingTravel().raw_penalty(problem, travel) == 1
    same = place_all(problem, {1: ("MON", 1, 1), 2: ("MON", 2, 1)})
    assert BuildingTravel().raw_penalty(problem, same) == 0


def test_s15_room_utilization_fit():
    groups = {1: GroupData(1, "G1", 20)}  # 20 students: 50-seat room -> 2.5, 30-seat lab -> 1.5
    s = mk_session(1, group=1)
    problem = mk_problem([s], groups=groups)
    assert RoomUtilizationFit().raw_penalty(problem, place_all(problem, {1: ("MON", 1, 1)})) == 1
    assert RoomUtilizationFit().raw_penalty(problem, place_all(problem, {1: ("MON", 1, 3)})) == 0


def test_s16_teacher_load_balance():
    sessions = [mk_session(i, course=100 + i, teacher=1, group=1) for i in (1, 2, 3)]
    problem = mk_problem(sessions)
    lopsided = place_all(
        problem, {1: ("MON", 1, 1), 2: ("MON", 2, 1), 3: ("TUE", 1, 1)}
    )
    assert TeacherLoadBalance().raw_penalty(problem, lopsided) == 1


def test_s17_group_load_balance():
    sessions = [mk_session(i, course=100 + i, teacher=1, group=1) for i in (1, 2, 3)]
    problem = mk_problem(sessions)
    lopsided = place_all(
        problem, {1: ("MON", 1, 1), 2: ("MON", 2, 1), 3: ("TUE", 1, 1)}
    )
    assert GroupLoadBalance().raw_penalty(problem, lopsided) == 1


def test_s18_difficult_course_morning():
    s = mk_session(1, is_difficult=True)
    problem = mk_problem([s], config=default_config(morning_end_slot=2))
    assert DifficultCourseMorning().raw_penalty(
        problem, place_all(problem, {1: ("MON", 3, 1)})) == 1
    assert DifficultCourseMorning().raw_penalty(
        problem, place_all(problem, {1: ("MON", 2, 1)})) == 0


def test_s19_teacher_back_to_back():
    avoider = {1: TeacherData(1, "T1", 4, 18, prefers_back_to_back=False)}
    sessions = two_sessions(teacher=1, group=1)
    problem = mk_problem(sessions, teachers=avoider)
    adjacent = place_all(problem, {1: ("MON", 1, 1), 2: ("MON", 2, 1)})
    assert TeacherBackToBack().raw_penalty(problem, adjacent) == 1

    preferrer = {1: TeacherData(1, "T1", 4, 18, prefers_back_to_back=True)}
    problem = mk_problem(sessions, teachers=preferrer)
    isolated = place_all(problem, {1: ("MON", 1, 1), 2: ("MON", 3, 1)})
    assert TeacherBackToBack().raw_penalty(problem, isolated) == 2
    adjacent = place_all(problem, {1: ("MON", 1, 1), 2: ("MON", 2, 1)})
    assert TeacherBackToBack().raw_penalty(problem, adjacent) == 0


def test_weighted_penalty_reads_constraint_weight_table():
    from app.solver.constraints.registry import total_soft_penalty

    s = mk_session(1)
    problem = mk_problem([s])
    timetable = place_all(problem, {1: ("MON", 1, 1)})
    baseline = total_soft_penalty(problem, timetable)
    problem.weights["S10_early_slot_avoidance"].weight += 13.0
    assert total_soft_penalty(problem, timetable) == baseline + 13.0
    problem.weights["S10_early_slot_avoidance"].enabled = False
    assert total_soft_penalty(problem, timetable) < baseline
