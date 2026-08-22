"""Manual-edit re-import (design doc section 7).

Admins edit the exported `MasterTimetable` sheet (moving a session's cell, or
changing the teacher code inside a cell — format `CODE.section (Teacher)`,
e.g. `CSE123.3 (T01)`, see section 3.1). Each edited session is re-validated
against all hard constraints in the context of the otherwise-unchanged
timetable; violating rows are rejected individually while valid edits apply,
then the soft-penalty report is recomputed (no re-solve).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, replace
from typing import Dict, List, Optional, Tuple

from openpyxl import load_workbook
from sqlalchemy.orm import Session as DbSession

from app.labels import compute_sections
from app.models import Course, Room, Session, Teacher
from app.solver.constraints.registry import failing_hard_keys, soft_penalty_breakdown
from app.solver.domain import Placement, Problem
from app.solver.loader import load_current_timetable, load_problem

CELL_RE = re.compile(r"^\s*(\S+)\.(\d+)\s*\((\S+)\)\s*$")


@dataclass
class ParsedEntry:
    day: str
    index: int
    room_code: str
    course_code: str
    section: int
    teacher_code: str


def parse_master_sheet(path_or_buffer) -> Tuple[List[ParsedEntry], List[dict]]:
    wb = load_workbook(path_or_buffer, data_only=True)
    if "MasterTimetable" not in wb.sheetnames:
        return [], [{"sheet": "MasterTimetable", "row": None, "field": "<sheet>",
                     "error": "MasterTimetable sheet is missing"}]
    ws = wb["MasterTimetable"]
    entries: List[ParsedEntry] = []
    errors: List[dict] = []
    day: Optional[str] = None
    slot_columns: Dict[int, int] = {}  # column -> slot index
    for row in ws.iter_rows():
        first = row[0].value
        if isinstance(first, str) and first.startswith("Day: "):
            day = first[5:].strip()
            slot_columns = {}
            continue
        if first == "Room":
            slot_columns = {
                cell.column: int(cell.value) for cell in row[1:] if cell.value is not None
            }
            continue
        if first is None or day is None or not slot_columns:
            continue
        room_code = str(first).strip()
        for cell in row[1:]:
            if cell.value is None or cell.column not in slot_columns:
                continue
            text = str(cell.value).strip()
            if not text:
                continue
            match = CELL_RE.match(text)
            if not match:
                errors.append({
                    "sheet": "MasterTimetable", "row": cell.row, "field": f"col {cell.column}",
                    "error": f"cell {text!r} does not match 'CODE.section (Teacher)'",
                })
                continue
            entries.append(ParsedEntry(
                day=day, index=slot_columns[cell.column], room_code=room_code,
                course_code=match.group(1), section=int(match.group(2)),
                teacher_code=match.group(3),
            ))
    return entries, errors


def _collapse_multislot(entries: List[ParsedEntry]) -> List[ParsedEntry]:
    """Merge contiguous repeated cells of one session into its start slot."""
    entries = sorted(entries, key=lambda e: (
        e.day, e.room_code, e.course_code, e.section, e.index
    ))
    collapsed: List[ParsedEntry] = []
    for entry in entries:
        prev = collapsed[-1] if collapsed else None
        if (
            prev is not None
            and (prev.day, prev.room_code, prev.course_code, prev.section)
            == (entry.day, entry.room_code, entry.course_code, entry.section)
        ):
            continue  # continuation slot of the same multi-slot session
        collapsed.append(entry)
    return collapsed


def reimport_master_timetable(db: DbSession, path_or_buffer) -> dict:
    entries, errors = parse_master_sheet(path_or_buffer)
    result = {"applied": [], "rejected": list(errors), "soft_report": None}
    if errors and not entries:
        return result

    entries = _collapse_multislot(entries)

    courses = {c.code: c for c in db.query(Course).all()}
    teachers = {t.code: t for t in db.query(Teacher).all()}
    rooms = {r.code: r for r in db.query(Room).all()}
    sessions = db.query(Session).all()
    # (course_id, section) -> class_group_id, from the same ranking used at export time
    group_by_section: Dict[tuple, int] = {}
    for (course_id, group_id), rank in compute_sections(db).items():
        group_by_section[(course_id, rank)] = group_id

    # bucket sessions by (course, group) — session type is not encoded in the
    # cell, so lectures/labs/tutorials of one course+group share a bucket
    session_buckets: Dict[tuple, List[Session]] = {}
    for s in sorted(sessions, key=lambda s: s.sequence_no):
        session_buckets.setdefault((s.course_id, s.class_group_id), []).append(s)

    entry_buckets: Dict[tuple, List[ParsedEntry]] = {}
    unmatched: List[dict] = []
    for entry in entries:
        course = courses.get(entry.course_code)
        room = rooms.get(entry.room_code)
        teacher = teachers.get(entry.teacher_code)
        problems = []
        group_id = None
        if course is None:
            problems.append(f"unknown course {entry.course_code!r}")
        else:
            group_id = group_by_section.get((course.id, entry.section))
            if group_id is None:
                problems.append(
                    f"course {entry.course_code!r} has no section {entry.section}"
                )
        if room is None:
            problems.append(f"unknown room {entry.room_code!r}")
        if teacher is None:
            problems.append(f"unknown teacher {entry.teacher_code!r}")
        if problems:
            unmatched.append({"entry": vars(entry), "error": "; ".join(problems)})
            continue
        entry_buckets.setdefault((course.id, group_id), []).append(entry)
    result["rejected"].extend(unmatched)

    # pair entries with sessions: keep sessions whose current placement matches
    # some entry unchanged; leftover entries pair with leftover sessions.
    edits: List[Tuple[Session, ParsedEntry]] = []
    for key, bucket_entries in entry_buckets.items():
        bucket_sessions = session_buckets.get(key, [])
        if len(bucket_entries) != len(bucket_sessions):
            result["rejected"].append({
                "entry": vars(bucket_entries[0]),
                "error": (
                    f"expected {len(bucket_sessions)} session(s) of this course/section "
                    f"in the sheet, found {len(bucket_entries)}"
                ),
            })
            continue
        remaining_sessions = list(bucket_sessions)
        pending_entries = []
        for entry in bucket_entries:
            room = rooms[entry.room_code]
            teacher = teachers[entry.teacher_code]
            match = next(
                (
                    s for s in remaining_sessions
                    if s.day_of_week == entry.day and s.slot_index == entry.index
                    and s.room_id == room.id and s.teacher_id == teacher.id
                ),
                None,
            )
            if match is not None:
                remaining_sessions.remove(match)
            else:
                pending_entries.append(entry)
        for entry, session in zip(pending_entries, remaining_sessions):
            edits.append((session, entry))

    if edits:
        problem = load_problem(db)
        timetable = load_current_timetable(db, problem)
        for session, entry in edits:
            room = rooms[entry.room_code]
            teacher = teachers[entry.teacher_code]
            placement = Placement(entry.day, entry.index, room.id)
            sdata = problem.sessions[session.id]
            if teacher.id != sdata.teacher_id:
                sdata = replace(sdata, teacher_id=teacher.id)
                # the edited teacher participates in every subsequent check
                problem.sessions[session.id] = sdata
            old_placement = (
                timetable.remove(session.id) if session.id in timetable.placements else None
            )
            failing = failing_hard_keys(sdata, placement, problem, timetable)
            if failing:
                if old_placement is not None:
                    timetable.place(session.id, old_placement)
                if teacher.id != session.teacher_id:
                    problem.sessions[session.id] = replace(sdata, teacher_id=session.teacher_id)
                result["rejected"].append({
                    "entry": vars(entry),
                    "error": f"hard constraint(s) violated: {failing}",
                })
                continue
            timetable.place(session.id, placement)
            session.day_of_week = entry.day
            session.slot_index = entry.index
            session.room_id = room.id
            session.teacher_id = teacher.id
            result["applied"].append({
                "session_id": session.id,
                "day": entry.day, "slot_index": entry.index,
                "room": entry.room_code, "teacher": entry.teacher_code,
            })
        db.commit()
        result["soft_report"] = soft_penalty_breakdown(problem, timetable)
    else:
        problem = load_problem(db)
        timetable = load_current_timetable(db, problem)
        result["soft_report"] = soft_penalty_breakdown(problem, timetable)
    return result
