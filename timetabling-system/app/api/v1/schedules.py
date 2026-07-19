from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as DbSession

from app.api.errors import api_error
from app.api.v1.serializers import session_rows
from app.database import get_db
from app.models import ClassGroup, Teacher

router = APIRouter(tags=["schedules"])


@router.get("/teacher/{teacher_id}/schedule")
def teacher_schedule(teacher_id: int, db: DbSession = Depends(get_db)):
    teacher = db.get(Teacher, teacher_id)
    if teacher is None:
        raise api_error(404, "teacher_not_found", f"no teacher with id {teacher_id}")
    return {
        "teacher": {"id": teacher.id, "code": teacher.code, "name": teacher.name},
        "sessions": session_rows(db, {"teacher_id": teacher_id}),
    }


@router.get("/group/{class_group_id}/schedule")
def group_schedule(class_group_id: int, db: DbSession = Depends(get_db)):
    group = db.get(ClassGroup, class_group_id)
    if group is None:
        raise api_error(404, "group_not_found", f"no class group with id {class_group_id}")
    return {
        "class_group": {"id": group.id, "code": group.code, "name": group.name},
        "sessions": session_rows(db, {"class_group_id": class_group_id}),
    }
