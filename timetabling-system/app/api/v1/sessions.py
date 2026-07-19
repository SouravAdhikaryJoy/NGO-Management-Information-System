from dataclasses import replace

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as DbSession

from app.api.errors import api_error
from app.api.v1.serializers import session_rows
from app.database import get_db
from app.models import Room, Session, Teacher
from app.solver.constraints.registry import failing_hard_keys, total_soft_penalty
from app.solver.domain import Placement
from app.solver.loader import load_current_timetable, load_problem
from app.schemas.api import SessionPatch

router = APIRouter(tags=["sessions"])


@router.patch("/session/{session_id}")
def patch_session(session_id: int, patch: SessionPatch, db: DbSession = Depends(get_db)):
    """Manual override of one session's day/slot/room/teacher, validated
    against every hard constraint before being applied."""
    session = db.get(Session, session_id)
    if session is None:
        raise api_error(404, "session_not_found", f"no session with id {session_id}")

    day = patch.day_of_week or session.day_of_week
    index = patch.slot_index if patch.slot_index is not None else session.slot_index
    room_id = patch.room_id if patch.room_id is not None else session.room_id
    teacher_id = patch.teacher_id if patch.teacher_id is not None else session.teacher_id
    if day is None or index is None or room_id is None:
        raise api_error(
            422, "incomplete_assignment",
            "day_of_week, slot_index and room_id must all be set (directly or already assigned)",
        )
    if patch.room_id is not None and db.get(Room, patch.room_id) is None:
        raise api_error(422, "unknown_room", f"no room with id {patch.room_id}")
    if patch.teacher_id is not None and db.get(Teacher, patch.teacher_id) is None:
        raise api_error(422, "unknown_teacher", f"no teacher with id {patch.teacher_id}")

    problem = load_problem(db)
    timetable = load_current_timetable(db, problem)
    sdata = problem.sessions[session_id]
    if teacher_id != sdata.teacher_id:
        sdata = replace(sdata, teacher_id=teacher_id)
        problem.sessions[session_id] = sdata
    if session_id in timetable.placements:
        timetable.remove(session_id)
    placement = Placement(day, index, room_id)
    # a manual override may not fight its own lock; unlock implicitly if asked
    if session.is_locked and patch.lock is not False:
        sdata = replace(
            sdata, locked_day=day, locked_index=index, locked_room_id=room_id
        )
        problem.sessions[session_id] = sdata
    failing = failing_hard_keys(sdata, placement, problem, timetable)
    if failing:
        raise api_error(
            409, "hard_constraint_violation",
            "the requested assignment violates hard constraints",
            details=failing,
        )
    timetable.place(session_id, placement)

    session.day_of_week = day
    session.slot_index = index
    session.room_id = room_id
    session.teacher_id = teacher_id
    if patch.lock is not None:
        session.is_locked = patch.lock
    if session.is_locked:
        session.locked_day = day
        session.locked_slot_index = index
        session.locked_room_id = room_id
    else:
        session.locked_day = session.locked_slot_index = session.locked_room_id = None
    db.commit()

    return {
        "session": next(r for r in session_rows(db) if r["id"] == session_id),
        "soft_penalty": total_soft_penalty(problem, timetable),
    }
