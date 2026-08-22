"""Per-constraint unit tests with synthetic minimal conflict cases (build order #3)."""

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
from app.solver.constraints.hard.h15_slot_type_scope import SlotTypeScope
from app.solver.domain import Placement, SlotData, TeacherData, Timetable
from tests.conftest import default_config, mk_problem, mk_session, place_all


def test_h01_room_occupancy():
    s1 = mk_session(1, teacher=1, group=1)
    s2 = mk_session(2, course=102, teacher=2, group=2)
    problem = mk_problem([s1, s2])
    timetable = place_all(problem, {1: ("MON", 1, 1)})
    constraint = RoomOccupancy()
    assert not constraint.check(s2, Placement("MON", 1, 1), problem, timetable)
    assert constraint.check(s2, Placement("MON", 1, 2), problem, timetable)


def test_h01_room_occupancy_multislot_overlap():
    s1 = mk_session(1, duration=2)
    s2 = mk_session(2, course=102, teacher=2, group=2)
    problem = mk_problem([s1, s2])
    timetable = place_all(problem, {1: ("MON", 1, 1)})  # occupies MON 1-2
    assert not RoomOccupancy().check(s2, Placement("MON", 2, 1), problem, timetable)


def test_h02_teacher_clash():
    s1 = mk_session(1, teacher=1, group=1)
    s2 = mk_session(2, course=102, teacher=1, group=2)
    problem = mk_problem([s1, s2])
    timetable = place_all(problem, {1: ("MON", 1, 1)})
    constraint = TeacherClash()
    assert not constraint.check(s2, Placement("MON", 1, 2), problem, timetable)
    assert constraint.check(s2, Placement("MON", 2, 2), problem, timetable)


def test_h03_group_clash():
    s1 = mk_session(1, teacher=1, group=1)
    s2 = mk_session(2, course=102, teacher=2, group=1)
    problem = mk_problem([s1, s2])
    timetable = place_all(problem, {1: ("MON", 1, 1)})
    constraint = GroupClash()
    assert not constraint.check(s2, Placement("MON", 1, 2), problem, timetable)
    assert constraint.check(s2, Placement("TUE", 1, 2), problem, timetable)


def test_h04_room_capacity():
    s = mk_session(1, group=1)  # G1 has 40 students; L1 capacity is 30
    problem = mk_problem([s])
    timetable = Timetable(problem)
    constraint = RoomCapacity()
    assert not constraint.check(s, Placement("MON", 1, 3), problem, timetable)
    assert constraint.check(s, Placement("MON", 1, 1), problem, timetable)


def test_h05_room_type_match():
    lab_session = mk_session(1, room_type=2, session_type="LAB")
    problem = mk_problem([lab_session])
    timetable = Timetable(problem)
    constraint = RoomTypeMatch()
    assert not constraint.check(lab_session, Placement("MON", 1, 1), problem, timetable)
    assert constraint.check(lab_session, Placement("MON", 1, 3), problem, timetable)


def test_h06_teacher_availability():
    s = mk_session(1, teacher=1)
    teachers = {1: TeacherData(1, "T1", 4, 18, unavailable=frozenset({("MON", 1)}))}
    problem = mk_problem([s], teachers=teachers)
    timetable = Timetable(problem)
    constraint = TeacherAvailabilityConstraint()
    assert not constraint.check(s, Placement("MON", 1, 1), problem, timetable)
    assert constraint.check(s, Placement("TUE", 1, 1), problem, timetable)


def test_h07_teacher_qualification():
    s = mk_session(1, course=101, teacher=2)
    problem = mk_problem([s], qualified={101: {1}})  # only teacher 1 qualifies
    timetable = Timetable(problem)
    assert not TeacherQualification().check(s, Placement("MON", 1, 1), problem, timetable)
    problem.qualified_teachers[101].add(2)
    assert TeacherQualification().check(s, Placement("MON", 1, 1), problem, timetable)


def test_h08_session_completeness():
    s1, s2 = mk_session(1), mk_session(2, course=102, teacher=2, group=2)
    problem = mk_problem([s1, s2])
    timetable = place_all(problem, {1: ("MON", 1, 1)})
    constraint = SessionCompleteness()
    assert constraint.violations(problem, timetable) == 1
    timetable.place(2, Placement("MON", 2, 1))
    assert constraint.violations(problem, timetable) == 0


def test_h09_slot_validity():
    s = mk_session(1)
    slots = {("MON", 1): SlotData("MON", 1), ("MON", 2): SlotData("MON", 2, is_break=True)}
    problem = mk_problem([s], slots=slots)
    timetable = Timetable(problem)
    constraint = SlotValidity()
    assert constraint.check(s, Placement("MON", 1, 1), problem, timetable)
    assert not constraint.check(s, Placement("MON", 2, 1), problem, timetable)  # break slot
    assert not constraint.check(s, Placement("MON", 9, 1), problem, timetable)  # missing slot


def test_h10_multislot_contiguity():
    s = mk_session(1, duration=2)
    problem = mk_problem([s])
    timetable = Timetable(problem)
    constraint = MultiSlotContiguity()
    assert constraint.check(s, Placement("MON", 1, 1), problem, timetable)
    # starting at the last slot of the day would spill past the day's end
    assert not constraint.check(s, Placement("MON", 4, 1), problem, timetable)


def test_h10_multislot_contiguity_break_in_span():
    s = mk_session(1, duration=2)
    slots = {
        ("MON", 1): SlotData("MON", 1),
        ("MON", 2): SlotData("MON", 2, is_break=True),
        ("MON", 3): SlotData("MON", 3),
    }
    problem = mk_problem([s], slots=slots)
    assert not MultiSlotContiguity().check(s, Placement("MON", 1, 1), problem, Timetable(problem))


def test_h11_teacher_max_daily():
    teachers = {1: TeacherData(1, "T1", 2, 18)}
    sessions = [mk_session(i, course=100 + i, teacher=1, group=1) for i in (1, 2, 3)]
    problem = mk_problem(sessions, teachers=teachers)
    timetable = place_all(problem, {1: ("MON", 1, 1), 2: ("MON", 2, 1)})
    constraint = TeacherMaxDaily()
    assert not constraint.check(sessions[2], Placement("MON", 3, 1), problem, timetable)
    assert constraint.check(sessions[2], Placement("TUE", 1, 1), problem, timetable)


def test_h12_group_max_daily():
    sessions = [mk_session(i, course=100 + i, teacher=1, group=1) for i in (1, 2, 3)]
    problem = mk_problem(sessions, config=default_config(group_max_sessions_per_day=2))
    timetable = place_all(problem, {1: ("MON", 1, 1), 2: ("MON", 2, 1)})
    constraint = GroupMaxDaily()
    assert not constraint.check(sessions[2], Placement("MON", 3, 1), problem, timetable)
    assert constraint.check(sessions[2], Placement("TUE", 1, 1), problem, timetable)


def test_h13_course_once_per_day():
    s1 = mk_session(1, course=101, group=1)
    s2 = mk_session(2, course=101, group=1)
    problem = mk_problem([s1, s2])
    timetable = place_all(problem, {1: ("MON", 1, 1)})
    constraint = CourseOncePerDay()
    assert not constraint.check(s2, Placement("MON", 3, 2), problem, timetable)
    assert constraint.check(s2, Placement("TUE", 1, 1), problem, timetable)


def test_h14_locked_session():
    s = mk_session(1, locked=("MON", 2, 1))
    problem = mk_problem([s])
    timetable = Timetable(problem)
    constraint = LockedSession()
    assert constraint.check(s, Placement("MON", 2, 1), problem, timetable)
    assert not constraint.check(s, Placement("MON", 3, 1), problem, timetable)
    assert not constraint.check(s, Placement("MON", 2, 2), problem, timetable)


def test_h15_slot_type_scope():
    lab_session = mk_session(1, room_type=2, session_type="LAB", duration=1)
    slots = {
        ("MON", 1): SlotData("MON", 1, allowed_types=frozenset({"LECTURE"})),
        ("MON", 2): SlotData("MON", 2, allowed_types=frozenset({"LAB"})),
        ("MON", 3): SlotData("MON", 3),  # unrestricted
    }
    problem = mk_problem([lab_session], slots=slots)
    timetable = Timetable(problem)
    constraint = SlotTypeScope()
    assert not constraint.check(lab_session, Placement("MON", 1, 3), problem, timetable)
    assert constraint.check(lab_session, Placement("MON", 2, 3), problem, timetable)
    assert constraint.check(lab_session, Placement("MON", 3, 3), problem, timetable)


def test_h15_slot_type_scope_multislot_every_slot_must_allow():
    lab_session = mk_session(1, room_type=2, session_type="LAB", duration=2)
    slots = {
        ("MON", 1): SlotData("MON", 1, allowed_types=frozenset({"LAB"})),
        ("MON", 2): SlotData("MON", 2, allowed_types=frozenset({"LECTURE"})),
    }
    problem = mk_problem([lab_session], slots=slots)
    assert not SlotTypeScope().check(
        lab_session, Placement("MON", 1, 3), problem, Timetable(problem)
    )


def test_full_timetable_violation_counts_are_zero_on_clean_assignment():
    from app.solver.constraints.registry import hard_violation_report

    s1 = mk_session(1, course=101, teacher=1, group=1)
    s2 = mk_session(2, course=102, teacher=2, group=2)
    problem = mk_problem([s1, s2])
    timetable = place_all(problem, {1: ("MON", 1, 1), 2: ("MON", 1, 2)})
    report = hard_violation_report(problem, timetable)
    assert all(row["violations"] == 0 for row in report)
    assert len(report) == 15
