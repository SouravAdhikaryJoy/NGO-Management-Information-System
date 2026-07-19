from typing import Dict, List, Optional

from sqlalchemy.orm import Session as DbSession

from app.models import ClassGroup, Course, Room, Session, Teacher, TimeSlot


def session_rows(db: DbSession, filter_by: Optional[dict] = None) -> List[dict]:
    """Flat serialized session rows used by JSON responses and csv/ics/pdf."""
    courses: Dict[int, Course] = {c.id: c for c in db.query(Course).all()}
    groups = {g.id: g for g in db.query(ClassGroup).all()}
    teachers = {t.id: t for t in db.query(Teacher).all()}
    rooms = {r.id: r for r in db.query(Room).all()}
    slots = {
        (t.day_of_week, t.slot_index): t for t in db.query(TimeSlot).all()
    }
    query = db.query(Session)
    if filter_by:
        query = query.filter_by(**filter_by)
    rows = []
    for s in query.all():
        slot = slots.get((s.day_of_week, s.slot_index)) if s.day_of_week else None
        course = courses[s.course_id]
        teacher = teachers[s.teacher_id]
        rows.append({
            "session_id": s.id,
            "id": s.id,
            "course_code": course.code,
            "course_title": course.title,
            "session_type": s.session_type,
            "class_group_code": groups[s.class_group_id].code,
            "teacher_code": teacher.code,
            "teacher_name": teacher.name,
            "day_of_week": s.day_of_week,
            "slot_index": s.slot_index,
            "duration_slots": s.duration_slots,
            "room_code": rooms[s.room_id].code if s.room_id else None,
            "start_time": slot.start_time.strftime("%H:%M") if slot else None,
            "end_time": slot.end_time.strftime("%H:%M") if slot else None,
            "is_locked": s.is_locked,
        })
    return rows
