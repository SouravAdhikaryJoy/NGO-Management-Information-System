from typing import Dict, List, Optional

from sqlalchemy.orm import Session as DbSession

from app.labels import compute_sections, course_group_label
from app.models import ClassGroup, Course, Room, Session, Teacher, TimeSlot


def session_rows(db: DbSession, filter_by: Optional[dict] = None) -> List[dict]:
    """Flat serialized session rows used by JSON responses and csv/ics/pdf.

    Cell labels follow design doc section 3.1 (`CODE.section`, e.g.
    `CSE123.3`): the room-view/teacher-view/group-view label variants are
    precomputed here so the frontend never re-derives the convention.
    """
    courses: Dict[int, Course] = {c.id: c for c in db.query(Course).all()}
    groups = {g.id: g for g in db.query(ClassGroup).all()}
    teachers = {t.id: t for t in db.query(Teacher).all()}
    rooms = {r.id: r for r in db.query(Room).all()}
    slots = {
        (t.day_of_week, t.slot_index): t for t in db.query(TimeSlot).all()
    }
    sections = compute_sections(db)
    query = db.query(Session)
    if filter_by:
        query = query.filter_by(**filter_by)
    rows = []
    for s in query.all():
        slot = slots.get((s.day_of_week, s.slot_index)) if s.day_of_week else None
        course = courses[s.course_id]
        teacher = teachers[s.teacher_id]
        room = rooms.get(s.room_id) if s.room_id else None
        section = sections.get((s.course_id, s.class_group_id), 1)
        code = course_group_label(course.code, section)
        rows.append({
            "session_id": s.id,
            "id": s.id,
            "course_id": s.course_id,
            "course_code": course.code,
            "course_title": course.title,
            "session_type": s.session_type,
            "class_group_id": s.class_group_id,
            "class_group_code": groups[s.class_group_id].code,
            "teacher_id": s.teacher_id,
            "teacher_code": teacher.code,
            "teacher_name": teacher.name,
            "day_of_week": s.day_of_week,
            "slot_index": s.slot_index,
            "duration_slots": s.duration_slots,
            "room_id": s.room_id,
            "room_code": room.code if room else None,
            "start_time": slot.start_time.strftime("%H:%M") if slot else None,
            "end_time": slot.end_time.strftime("%H:%M") if slot else None,
            "is_locked": s.is_locked,
            "section": section,
            "code_section": code,
            "label_room_view": f"{code} ({teacher.code})",
            "label_teacher_view": f"{code} ({room.code})" if room else code,
            "label_group_view": f"{code} ({teacher.code}) ({room.code})" if room else f"{code} ({teacher.code})",
        })
    return rows
