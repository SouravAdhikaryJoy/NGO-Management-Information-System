"""Excel workbook import: read -> validate -> upsert to DB.

One sheet per entity (design doc section 3). Validation is all-or-nothing per
import: any row-level error aborts the write and every error is reported with
sheet, row number (as shown in Excel), field and message — bad rows are never
silently skipped. Re-import upserts by natural key.
"""

from __future__ import annotations

from datetime import time
from typing import Callable, Dict, List, Optional

import pandas as pd
from sqlalchemy.orm import Session as DbSession

from app.models import (
    Building,
    ClassGroup,
    ConstraintWeight,
    Course,
    CourseSessionType,
    Department,
    Room,
    RoomType,
    SystemConfig,
    Teacher,
    TeacherAvailability,
    TeacherCoursePreference,
    TimeSlot,
    University,
)
from app.models.curriculum import SESSION_TYPES
from app.models.infrastructure import DAYS
from app.models.people import AVAILABILITY_STATES, EMPLOYMENT_TYPES

SHEET_ORDER = [
    "Universities", "Departments", "Buildings", "RoomTypes", "Rooms", "TimeSlots",
    "Teachers", "Courses", "CourseSessionTypes", "ClassGroups",
    "TeacherAvailability", "TeacherCoursePreference",
    "ConstraintWeights", "SystemConfig",
]
OPTIONAL_SHEETS = {
    "TeacherAvailability", "TeacherCoursePreference", "ConstraintWeights", "SystemConfig",
}

SHEET_COLUMNS: Dict[str, List[str]] = {
    "Universities": ["code", "name"],
    "Departments": ["code", "name", "university_code"],
    "Buildings": ["code", "name", "university_code"],
    "RoomTypes": ["code", "name"],
    "Rooms": ["code", "name", "building_code", "room_type_code", "capacity"],
    "TimeSlots": ["day_of_week", "slot_index", "start_time", "end_time", "is_break"],
    "Teachers": [
        "code", "name", "department_code", "max_sessions_per_day",
        "max_sessions_per_week", "employment_type", "prefers_back_to_back",
    ],
    "Courses": [
        "code", "title", "department_code", "semester", "credit_hours",
        "is_difficult", "teacher_code",
    ],
    "CourseSessionTypes": [
        "course_code", "session_type", "sessions_per_week", "duration_slots",
        "required_room_type_code",
    ],
    "ClassGroups": ["code", "name", "department_code", "semester", "size"],
    "TeacherAvailability": ["teacher_code", "day_of_week", "slot_index", "availability"],
    "TeacherCoursePreference": ["teacher_code", "course_code", "preference"],
    "ConstraintWeights": ["constraint_key", "tier", "weight", "is_hard", "enabled"],
    "SystemConfig": ["key", "value", "value_type", "description"],
}


class RowError(Exception):
    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(f"{field}: {message}")


def _is_blank(value) -> bool:
    return value is None or (isinstance(value, float) and pd.isna(value)) or (
        isinstance(value, str) and not value.strip()
    )


def _req_str(row, field) -> str:
    value = row.get(field)
    if _is_blank(value):
        raise RowError(field, "required value is missing")
    return str(value).strip()


def _opt_str(row, field) -> Optional[str]:
    value = row.get(field)
    return None if _is_blank(value) else str(value).strip()


def _req_int(row, field, minimum: Optional[int] = None) -> int:
    raw = row.get(field)
    if _is_blank(raw):
        raise RowError(field, "required value is missing")
    try:
        value = int(float(raw))
    except (TypeError, ValueError):
        raise RowError(field, f"expected an integer, got {raw!r}")
    if minimum is not None and value < minimum:
        raise RowError(field, f"must be >= {minimum}, got {value}")
    return value


def _req_float(row, field, minimum: Optional[float] = None) -> float:
    raw = row.get(field)
    if _is_blank(raw):
        raise RowError(field, "required value is missing")
    try:
        value = float(raw)
    except (TypeError, ValueError):
        raise RowError(field, f"expected a number, got {raw!r}")
    if minimum is not None and value < minimum:
        raise RowError(field, f"must be >= {minimum}, got {value}")
    return value


def _req_bool(row, field, default: Optional[bool] = None) -> bool:
    raw = row.get(field)
    if _is_blank(raw):
        if default is not None:
            return default
        raise RowError(field, "required value is missing")
    if isinstance(raw, bool):
        return raw
    text = str(raw).strip().lower()
    if text in ("1", "true", "yes", "y", "1.0"):
        return True
    if text in ("0", "false", "no", "n", "0.0"):
        return False
    raise RowError(field, f"expected a boolean, got {raw!r}")


def _opt_bool(row, field) -> Optional[bool]:
    if _is_blank(row.get(field)):
        return None
    return _req_bool(row, field)


def _req_enum(row, field, allowed) -> str:
    value = _req_str(row, field).upper()
    if value not in allowed:
        raise RowError(field, f"must be one of {sorted(allowed)}, got {value!r}")
    return value


def _req_time(row, field) -> time:
    raw = row.get(field)
    if _is_blank(raw):
        raise RowError(field, "required value is missing")
    if isinstance(raw, time):
        return raw
    text = str(raw).strip()
    for fmt in ("%H:%M", "%H:%M:%S"):
        try:
            from datetime import datetime

            return datetime.strptime(text, fmt).time()
        except ValueError:
            continue
    raise RowError(field, f"expected HH:MM time, got {raw!r}")


def _lookup(cache: dict, key, field: str, entity: str) -> int:
    obj_id = cache.get(key)
    if obj_id is None:
        raise RowError(field, f"unknown {entity} {key!r}")
    return obj_id


class ImportResult:
    def __init__(self):
        self.errors: List[dict] = []
        self.counts: Dict[str, int] = {}

    @property
    def ok(self) -> bool:
        return not self.errors

    def add_error(self, sheet: str, row: Optional[int], field: str, message: str):
        self.errors.append({"sheet": sheet, "row": row, "field": field, "error": message})

    def as_dict(self):
        return {"ok": self.ok, "counts": self.counts, "errors": self.errors}


def import_workbook(db: DbSession, path_or_buffer) -> ImportResult:
    result = ImportResult()
    try:
        book: Dict[str, pd.DataFrame] = pd.read_excel(path_or_buffer, sheet_name=None)
    except Exception as exc:
        result.add_error("<workbook>", None, "<file>", f"could not read workbook: {exc}")
        return result

    for sheet in SHEET_ORDER:
        if sheet not in book and sheet not in OPTIONAL_SHEETS:
            result.add_error(sheet, None, "<sheet>", "required sheet is missing")
    for sheet, df in book.items():
        if sheet not in SHEET_COLUMNS:
            continue
        missing = [c for c in SHEET_COLUMNS[sheet] if c not in df.columns]
        for column in missing:
            result.add_error(sheet, None, column, "required column is missing")
    if not result.ok:
        return result

    # caches: natural key -> id, populated as sheets import in FK order
    ids: Dict[str, Dict] = {}

    def upsert(model, key_fields: dict, values: dict):
        obj = db.query(model).filter_by(**key_fields).one_or_none()
        if obj is None:
            obj = model(**key_fields, **values)
            db.add(obj)
        else:
            for field, value in values.items():
                setattr(obj, field, value)
        db.flush()
        return obj

    def run_sheet(sheet: str, handler: Callable):
        df = book.get(sheet)
        count = 0
        if df is not None:
            for position, row in enumerate(df.to_dict(orient="records")):
                excel_row = position + 2  # 1-based + header row
                try:
                    handler(row)
                    count += 1
                except RowError as err:
                    result.add_error(sheet, excel_row, err.field, err.message)
        result.counts[sheet] = count

    def universities(row):
        obj = upsert(University, {"code": _req_str(row, "code")}, {"name": _req_str(row, "name")})
        ids.setdefault("university", {})[obj.code] = obj.id

    def departments(row):
        uni = _lookup(ids.get("university", {}), _req_str(row, "university_code"),
                      "university_code", "university")
        obj = upsert(Department, {"code": _req_str(row, "code")},
                     {"name": _req_str(row, "name"), "university_id": uni})
        ids.setdefault("department", {})[obj.code] = obj.id

    def buildings(row):
        uni = _lookup(ids.get("university", {}), _req_str(row, "university_code"),
                      "university_code", "university")
        obj = upsert(Building, {"code": _req_str(row, "code")},
                     {"name": _req_str(row, "name"), "university_id": uni})
        ids.setdefault("building", {})[obj.code] = obj.id

    def room_types(row):
        obj = upsert(RoomType, {"code": _req_str(row, "code")}, {"name": _req_str(row, "name")})
        ids.setdefault("room_type", {})[obj.code] = obj.id

    def rooms(row):
        obj = upsert(Room, {"code": _req_str(row, "code")}, {
            "name": _req_str(row, "name"),
            "building_id": _lookup(ids.get("building", {}), _req_str(row, "building_code"),
                                   "building_code", "building"),
            "room_type_id": _lookup(ids.get("room_type", {}), _req_str(row, "room_type_code"),
                                    "room_type_code", "room type"),
            "capacity": _req_int(row, "capacity", minimum=1),
        })
        ids.setdefault("room", {})[obj.code] = obj.id

    def time_slots(row):
        upsert(TimeSlot, {
            "day_of_week": _req_enum(row, "day_of_week", DAYS),
            "slot_index": _req_int(row, "slot_index", minimum=1),
        }, {
            "start_time": _req_time(row, "start_time"),
            "end_time": _req_time(row, "end_time"),
            "is_break": _req_bool(row, "is_break", default=False),
        })

    def teachers(row):
        obj = upsert(Teacher, {"code": _req_str(row, "code")}, {
            "name": _req_str(row, "name"),
            "department_id": _lookup(ids.get("department", {}), _req_str(row, "department_code"),
                                     "department_code", "department"),
            "max_sessions_per_day": _req_int(row, "max_sessions_per_day", minimum=1),
            "max_sessions_per_week": _req_int(row, "max_sessions_per_week", minimum=1),
            "employment_type": _req_enum(row, "employment_type", EMPLOYMENT_TYPES),
            "prefers_back_to_back": _opt_bool(row, "prefers_back_to_back"),
        })
        ids.setdefault("teacher", {})[obj.code] = obj.id

    def courses(row):
        teacher_code = _opt_str(row, "teacher_code")
        teacher_id = None
        if teacher_code:
            teacher_id = _lookup(ids.get("teacher", {}), teacher_code, "teacher_code", "teacher")
        obj = upsert(Course, {"code": _req_str(row, "code")}, {
            "title": _req_str(row, "title"),
            "department_id": _lookup(ids.get("department", {}), _req_str(row, "department_code"),
                                     "department_code", "department"),
            "semester": _req_int(row, "semester", minimum=1),
            "credit_hours": _req_float(row, "credit_hours", minimum=0),
            "is_difficult": _req_bool(row, "is_difficult", default=False),
            "teacher_id": teacher_id,
        })
        ids.setdefault("course", {})[obj.code] = obj.id

    def course_session_types(row):
        upsert(CourseSessionType, {
            "course_id": _lookup(ids.get("course", {}), _req_str(row, "course_code"),
                                 "course_code", "course"),
            "session_type": _req_enum(row, "session_type", SESSION_TYPES),
        }, {
            "sessions_per_week": _req_int(row, "sessions_per_week", minimum=1),
            "duration_slots": _req_int(row, "duration_slots", minimum=1),
            "required_room_type_id": _lookup(
                ids.get("room_type", {}), _req_str(row, "required_room_type_code"),
                "required_room_type_code", "room type"),
        })

    def class_groups(row):
        upsert(ClassGroup, {"code": _req_str(row, "code")}, {
            "name": _req_str(row, "name"),
            "department_id": _lookup(ids.get("department", {}), _req_str(row, "department_code"),
                                     "department_code", "department"),
            "semester": _req_int(row, "semester", minimum=1),
            "size": _req_int(row, "size", minimum=1),
        })

    def teacher_availability(row):
        upsert(TeacherAvailability, {
            "teacher_id": _lookup(ids.get("teacher", {}), _req_str(row, "teacher_code"),
                                  "teacher_code", "teacher"),
            "day_of_week": _req_enum(row, "day_of_week", DAYS),
            "slot_index": _req_int(row, "slot_index", minimum=1),
        }, {"availability": _req_enum(row, "availability", AVAILABILITY_STATES)})

    def teacher_course_preference(row):
        preference = _req_int(row, "preference")
        if not 1 <= preference <= 5:
            raise RowError("preference", f"must be between 1 and 5, got {preference}")
        upsert(TeacherCoursePreference, {
            "teacher_id": _lookup(ids.get("teacher", {}), _req_str(row, "teacher_code"),
                                  "teacher_code", "teacher"),
            "course_id": _lookup(ids.get("course", {}), _req_str(row, "course_code"),
                                 "course_code", "course"),
        }, {"preference": preference})

    def constraint_weights(row):
        upsert(ConstraintWeight, {"constraint_key": _req_str(row, "constraint_key")}, {
            "tier": _req_int(row, "tier", minimum=0),
            "weight": _req_float(row, "weight", minimum=0),
            "is_hard": _req_bool(row, "is_hard"),
            "enabled": _req_bool(row, "enabled", default=True),
        })

    def system_config(row):
        value_type = _req_str(row, "value_type").lower()
        if value_type not in ("int", "float", "str", "bool"):
            raise RowError("value_type", f"must be int|float|str|bool, got {value_type!r}")
        upsert(SystemConfig, {"key": _req_str(row, "key")}, {
            "value": _req_str(row, "value"),
            "value_type": value_type,
            "description": _opt_str(row, "description") or "",
        })

    handlers = {
        "Universities": universities,
        "Departments": departments,
        "Buildings": buildings,
        "RoomTypes": room_types,
        "Rooms": rooms,
        "TimeSlots": time_slots,
        "Teachers": teachers,
        "Courses": courses,
        "CourseSessionTypes": course_session_types,
        "ClassGroups": class_groups,
        "TeacherAvailability": teacher_availability,
        "TeacherCoursePreference": teacher_course_preference,
        "ConstraintWeights": constraint_weights,
        "SystemConfig": system_config,
    }

    for sheet in SHEET_ORDER:
        run_sheet(sheet, handlers[sheet])

    if result.ok:
        db.commit()
    else:
        db.rollback()
    return result


def write_blank_template(path) -> None:
    """Write an empty workbook with every sheet and header row."""
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        for sheet in SHEET_ORDER:
            pd.DataFrame(columns=SHEET_COLUMNS[sheet]).to_excel(
                writer, sheet_name=sheet, index=False
            )
