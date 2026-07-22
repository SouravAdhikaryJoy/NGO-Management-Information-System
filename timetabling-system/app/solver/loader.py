"""Bridge between the ORM and the pure solver domain.

- generate_sessions: curriculum -> Session rows (the scheduling units)
- load_problem: DB -> Problem (+ optionally current assignments -> Timetable)
- persist_timetable: solved placements -> Session rows
"""

from __future__ import annotations

from typing import Dict, Optional

from sqlalchemy.orm import Session as DbSession

from app.config.seed import load_system_config
from app.models import (
    ClassGroup,
    ConstraintWeight,
    Course,
    CourseSessionType,
    Room,
    Session,
    Teacher,
    TeacherAvailability,
    TeacherCoursePreference,
    TimeSlot,
)
from app.solver.domain import (
    GroupData,
    Placement,
    Problem,
    RoomData,
    SessionData,
    SlotData,
    TeacherData,
    Timetable,
    WeightRow,
)


class SessionGenerationError(Exception):
    pass


def generate_sessions(db: DbSession) -> int:
    """(Re)generate Session rows from curriculum data.

    A class group is enrolled in every course sharing its department+semester.
    Teacher per course: explicit Course.teacher_id, else best available by
    TeacherCoursePreference (highest preference, then lowest assigned weekly
    load). Existing locked sessions are preserved when they still match a
    generated (course, group, type, sequence) tuple.
    """
    courses = db.query(Course).all()
    groups = db.query(ClassGroup).all()
    session_types = db.query(CourseSessionType).all()
    prefs = db.query(TeacherCoursePreference).all()

    prefs_by_course: Dict[int, list] = {}
    for p in prefs:
        prefs_by_course.setdefault(p.course_id, []).append(p)

    teacher_load: Dict[int, int] = {}

    def pick_teacher(course: Course) -> int:
        if course.teacher_id is not None:
            return course.teacher_id
        candidates = prefs_by_course.get(course.id, [])
        if not candidates:
            raise SessionGenerationError(
                f"Course {course.code} has no assigned teacher and no TeacherCoursePreference rows"
            )
        candidates = sorted(
            candidates,
            key=lambda p: (-p.preference, teacher_load.get(p.teacher_id, 0), p.teacher_id),
        )
        return candidates[0].teacher_id

    old_locked = {
        (s.course_id, s.class_group_id, s.session_type, s.sequence_no): s
        for s in db.query(Session).filter(Session.is_locked.is_(True)).all()
    }
    db.query(Session).delete()

    count = 0
    types_by_course: Dict[int, list] = {}
    for st in session_types:
        types_by_course.setdefault(st.course_id, []).append(st)

    for group in groups:
        for course in courses:
            if course.department_id != group.department_id or course.semester != group.semester:
                continue
            teacher_id = pick_teacher(course)
            for st in types_by_course.get(course.id, []):
                for seq in range(1, st.sessions_per_week + 1):
                    locked = old_locked.get((course.id, group.id, st.session_type, seq))
                    row = Session(
                        course_id=course.id,
                        class_group_id=group.id,
                        teacher_id=teacher_id,
                        session_type=st.session_type,
                        duration_slots=st.duration_slots,
                        required_room_type_id=st.required_room_type_id,
                        sequence_no=seq,
                    )
                    if locked is not None:
                        row.is_locked = True
                        row.locked_day = locked.locked_day
                        row.locked_slot_index = locked.locked_slot_index
                        row.locked_room_id = locked.locked_room_id
                        row.day_of_week = locked.day_of_week
                        row.slot_index = locked.slot_index
                        row.room_id = locked.room_id
                        row.teacher_id = locked.teacher_id
                    db.add(row)
                    teacher_load[row.teacher_id] = (
                        teacher_load.get(row.teacher_id, 0) + st.duration_slots
                    )
                    count += 1
    db.commit()
    return count


def load_problem(db: DbSession) -> Problem:
    def _scope(raw: str | None):
        if not raw or not raw.strip():
            return None
        return frozenset(part.strip().upper() for part in raw.split(",") if part.strip())

    slots = {
        (t.day_of_week, t.slot_index): SlotData(
            t.day_of_week, t.slot_index, t.is_break, _scope(t.session_type_scope)
        )
        for t in db.query(TimeSlot).all()
    }
    rooms = {
        r.id: RoomData(r.id, r.code, r.capacity, r.room_type_id, r.building_id)
        for r in db.query(Room).all()
    }

    availability: Dict[int, Dict[str, set]] = {}
    for a in db.query(TeacherAvailability).all():
        availability.setdefault(a.teacher_id, {"UNAVAILABLE": set(), "PREFERRED": set()})
        if a.availability in ("UNAVAILABLE", "PREFERRED"):
            availability[a.teacher_id][a.availability].add((a.day_of_week, a.slot_index))

    teachers = {}
    for t in db.query(Teacher).all():
        av = availability.get(t.id, {"UNAVAILABLE": set(), "PREFERRED": set()})
        teachers[t.id] = TeacherData(
            id=t.id,
            code=t.code,
            max_sessions_per_day=t.max_sessions_per_day,
            max_sessions_per_week=t.max_sessions_per_week,
            unavailable=frozenset(av["UNAVAILABLE"]),
            preferred=frozenset(av["PREFERRED"]),
            prefers_back_to_back=t.prefers_back_to_back,
        )

    groups = {
        g.id: GroupData(g.id, g.code, g.size) for g in db.query(ClassGroup).all()
    }

    courses = {c.id: c for c in db.query(Course).all()}
    qualified: Dict[int, set] = {c.id: set() for c in courses.values()}
    teacher_course_pref = {}
    for p in db.query(TeacherCoursePreference).all():
        qualified.setdefault(p.course_id, set()).add(p.teacher_id)
        teacher_course_pref[(p.teacher_id, p.course_id)] = p.preference
    for c in courses.values():
        if c.teacher_id is not None:
            qualified[c.id].add(c.teacher_id)

    sessions = {}
    for s in db.query(Session).all():
        course = courses[s.course_id]
        sessions[s.id] = SessionData(
            id=s.id,
            course_id=s.course_id,
            course_code=course.code,
            group_id=s.class_group_id,
            teacher_id=s.teacher_id,
            session_type=s.session_type,
            duration=s.duration_slots,
            required_room_type_id=s.required_room_type_id,
            is_difficult=course.is_difficult,
            is_locked=s.is_locked,
            locked_day=s.locked_day,
            locked_index=s.locked_slot_index,
            locked_room_id=s.locked_room_id,
        )

    weights = {
        w.constraint_key: WeightRow(w.tier, w.weight, w.is_hard, w.enabled)
        for w in db.query(ConstraintWeight).all()
    }
    config = load_system_config(db)

    return Problem(
        slots=slots,
        rooms=rooms,
        teachers=teachers,
        groups=groups,
        sessions=sessions,
        qualified_teachers=qualified,
        teacher_course_pref=teacher_course_pref,
        config=config,
        weights=weights,
    )


def load_current_timetable(db: DbSession, problem: Problem) -> Timetable:
    """Build a Timetable from Session rows that already carry assignments."""
    timetable = Timetable(problem)
    for s in db.query(Session).all():
        if s.day_of_week is not None and s.slot_index is not None and s.room_id is not None:
            timetable.place(s.id, Placement(s.day_of_week, s.slot_index, s.room_id))
    return timetable


def persist_timetable(db: DbSession, timetable: Timetable) -> None:
    for s in db.query(Session).all():
        placement = timetable.placements.get(s.id)
        if placement is None:
            s.day_of_week = s.slot_index = s.room_id = None
        else:
            s.day_of_week = placement.day
            s.slot_index = placement.index
            s.room_id = placement.room_id
    db.commit()
