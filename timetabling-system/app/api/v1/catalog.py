"""Course/teacher/room/class-group catalog: public reads, admin-gated writes.

Reassigning a course's teacher or tightening a teacher's caps can invalidate
an already-solved routine (a teacher clash, an exceeded daily cap, ...). We
don't silently fix that — cascading the change and then reporting whatever
new hard violations it caused lets the admin see and resolve it (re-solve,
or move the affected sessions) instead of finding out later.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as DbSession

from app.api.errors import api_error
from app.database import get_db
from app.labels import compute_sections
from app.models import (
    ClassGroup,
    Course,
    CourseSessionType,
    Department,
    Room,
    RoomType,
    Session,
    Teacher,
)
from app.schemas.api import CoursePatch, TeacherPatch
from app.security import require_admin
from app.solver.constraints.registry import hard_violation_report
from app.solver.loader import load_current_timetable, load_problem

router = APIRouter(tags=["catalog"])


def _current_violations(db: DbSession):
    problem = load_problem(db)
    timetable = load_current_timetable(db, problem)
    return [row for row in hard_violation_report(problem, timetable) if row["violations"] > 0]


@router.get("/courses")
def list_courses(db: DbSession = Depends(get_db)):
    departments = {d.id: d.code for d in db.query(Department).all()}
    teachers = {t.id: t for t in db.query(Teacher).all()}
    room_types = {rt.id: rt.code for rt in db.query(RoomType).all()}
    sections = compute_sections(db)
    groups_by_code = {g.id: g.code for g in db.query(ClassGroup).all()}

    session_types: dict = {}
    for st in db.query(CourseSessionType).all():
        session_types.setdefault(st.course_id, []).append({
            "session_type": st.session_type,
            "sessions_per_week": st.sessions_per_week,
            "duration_slots": st.duration_slots,
            "required_room_type": room_types.get(st.required_room_type_id),
        })

    course_sections: dict = {}
    for (course_id, group_id), rank in sections.items():
        course_sections.setdefault(course_id, []).append({
            "class_group_code": groups_by_code.get(group_id), "section": rank,
        })

    rows = []
    for c in db.query(Course).order_by(Course.code).all():
        teacher = teachers.get(c.teacher_id)
        rows.append({
            "id": c.id,
            "code": c.code,
            "title": c.title,
            "department_code": departments.get(c.department_id),
            "semester": c.semester,
            "credit_hours": c.credit_hours,
            "is_difficult": c.is_difficult,
            "teacher_id": c.teacher_id,
            "teacher_code": teacher.code if teacher else None,
            "teacher_name": teacher.name if teacher else None,
            "session_types": session_types.get(c.id, []),
            "sections": sorted(course_sections.get(c.id, []), key=lambda s: s["section"]),
        })
    return {"courses": rows}


@router.patch("/course/{course_id}")
def patch_course(
    course_id: int,
    patch: CoursePatch,
    db: DbSession = Depends(get_db),
    _admin=Depends(require_admin),
):
    course = db.get(Course, course_id)
    if course is None:
        raise api_error(404, "course_not_found", f"no course with id {course_id}")
    if patch.teacher_id is not None and db.get(Teacher, patch.teacher_id) is None:
        raise api_error(422, "unknown_teacher", f"no teacher with id {patch.teacher_id}")

    teacher_changed = patch.teacher_id is not None and patch.teacher_id != course.teacher_id
    for field in ("title", "teacher_id", "is_difficult", "semester"):
        value = getattr(patch, field)
        if value is not None:
            setattr(course, field, value)

    if teacher_changed:
        db.query(Session).filter(Session.course_id == course_id).update(
            {"teacher_id": patch.teacher_id}
        )
    db.commit()

    return {
        "course_id": course_id,
        "teacher_id": course.teacher_id,
        "new_hard_violations": _current_violations(db) if teacher_changed else [],
    }


@router.get("/teachers")
def list_teachers(db: DbSession = Depends(get_db)):
    departments = {d.id: d.code for d in db.query(Department).all()}
    load: dict = {}
    for row in db.query(Session.teacher_id).all():
        load[row.teacher_id] = load.get(row.teacher_id, 0) + 1
    rows = []
    for t in db.query(Teacher).order_by(Teacher.code).all():
        rows.append({
            "id": t.id,
            "code": t.code,
            "name": t.name,
            "department_code": departments.get(t.department_id),
            "max_sessions_per_day": t.max_sessions_per_day,
            "max_sessions_per_week": t.max_sessions_per_week,
            "employment_type": t.employment_type,
            "prefers_back_to_back": t.prefers_back_to_back,
            "weekly_sessions_assigned": load.get(t.id, 0),
        })
    return {"teachers": rows}


@router.patch("/teacher/{teacher_id}")
def patch_teacher(
    teacher_id: int,
    patch: TeacherPatch,
    db: DbSession = Depends(get_db),
    _admin=Depends(require_admin),
):
    teacher = db.get(Teacher, teacher_id)
    if teacher is None:
        raise api_error(404, "teacher_not_found", f"no teacher with id {teacher_id}")
    if patch.employment_type is not None:
        from app.models.people import EMPLOYMENT_TYPES

        if patch.employment_type not in EMPLOYMENT_TYPES:
            raise api_error(
                422, "bad_employment_type",
                f"must be one of {EMPLOYMENT_TYPES}",
            )
    caps_tightened = (
        (patch.max_sessions_per_day is not None and patch.max_sessions_per_day < teacher.max_sessions_per_day)
        or (patch.max_sessions_per_week is not None and patch.max_sessions_per_week < teacher.max_sessions_per_week)
    )
    for field in (
        "name", "max_sessions_per_day", "max_sessions_per_week",
        "employment_type", "prefers_back_to_back",
    ):
        value = getattr(patch, field)
        if value is not None:
            setattr(teacher, field, value)
    db.commit()

    return {
        "teacher_id": teacher_id,
        "new_hard_violations": _current_violations(db) if caps_tightened else [],
    }


@router.get("/rooms")
def list_rooms(db: DbSession = Depends(get_db)):
    room_types = {rt.id: rt.code for rt in db.query(RoomType).all()}
    return {
        "rooms": [
            {
                "id": r.id, "code": r.code, "name": r.name,
                "room_type_code": room_types.get(r.room_type_id), "capacity": r.capacity,
            }
            for r in db.query(Room).order_by(Room.code).all()
        ]
    }


@router.get("/class-groups")
def list_class_groups(db: DbSession = Depends(get_db)):
    departments = {d.id: d.code for d in db.query(Department).all()}
    return {
        "class_groups": [
            {
                "id": g.id, "code": g.code, "name": g.name,
                "department_code": departments.get(g.department_id),
                "semester": g.semester, "size": g.size,
            }
            for g in db.query(ClassGroup).order_by(ClassGroup.code).all()
        ]
    }
