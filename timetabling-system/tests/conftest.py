import os
import tempfile

_tmpdir = tempfile.mkdtemp(prefix="timetabling-test-")
os.environ["DATABASE_URL"] = f"sqlite:///{_tmpdir}/test.db"

import pytest  # noqa: E402

from app.config.defaults import (  # noqa: E402
    HARD_CONSTRAINT_DEFAULTS,
    SOFT_CONSTRAINT_DEFAULTS,
    SYSTEM_CONFIG_DEFAULTS,
    parse_config_value,
)
import app.models  # noqa: E402, F401  (register all tables on Base.metadata)
from app.database import Base, SessionLocal, engine  # noqa: E402
from app.solver.domain import (  # noqa: E402
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

# ---------------------------------------------------------------------------
# synthetic problem builders (no database needed)
# ---------------------------------------------------------------------------

DAYS = ["MON", "TUE", "WED"]
SLOTS = [1, 2, 3, 4]


def default_weights():
    return {
        key: WeightRow(tier=tier, weight=weight, is_hard=is_hard, enabled=True)
        for key, tier, weight, is_hard in HARD_CONSTRAINT_DEFAULTS + SOFT_CONSTRAINT_DEFAULTS
    }


def default_config(**overrides):
    config = {
        key: parse_config_value(value, value_type)
        for key, (value, value_type, _desc) in SYSTEM_CONFIG_DEFAULTS.items()
    }
    config.update(overrides)
    return config


def mk_session(
    sid,
    course=101,
    course_code=None,
    group=1,
    teacher=1,
    duration=1,
    room_type=1,
    session_type="LECTURE",
    is_difficult=False,
    locked=None,  # (day, index, room_id)
):
    return SessionData(
        id=sid,
        course_id=course,
        course_code=course_code or f"C{course}",
        group_id=group,
        teacher_id=teacher,
        session_type=session_type,
        duration=duration,
        required_room_type_id=room_type,
        is_difficult=is_difficult,
        is_locked=locked is not None,
        locked_day=locked[0] if locked else None,
        locked_index=locked[1] if locked else None,
        locked_room_id=locked[2] if locked else None,
    )


def mk_problem(
    sessions,
    teachers=None,
    groups=None,
    rooms=None,
    slots=None,
    qualified=None,
    prefs=None,
    config=None,
    weights=None,
):
    slots = slots if slots is not None else {
        (day, index): SlotData(day, index) for day in DAYS for index in SLOTS
    }
    rooms = rooms if rooms is not None else {
        1: RoomData(1, "R1", 50, 1, 1),
        2: RoomData(2, "R2", 50, 1, 2),
        3: RoomData(3, "L1", 30, 2, 1),
    }
    teachers = teachers if teachers is not None else {
        1: TeacherData(1, "T1", 4, 18),
        2: TeacherData(2, "T2", 4, 18),
    }
    groups = groups if groups is not None else {
        1: GroupData(1, "G1", 40),
        2: GroupData(2, "G2", 35),
    }
    session_map = {s.id: s for s in sessions}
    if qualified is None:
        qualified = {}
        for s in sessions:
            qualified.setdefault(s.course_id, set()).update(teachers.keys())
    return Problem(
        slots=slots,
        rooms=rooms,
        teachers=teachers,
        groups=groups,
        sessions=session_map,
        qualified_teachers=qualified,
        teacher_course_pref=prefs or {},
        config=config or default_config(),
        weights=weights or default_weights(),
    )


def place_all(problem, placements):
    """placements: {session_id: (day, index, room_id)} -> Timetable"""
    timetable = Timetable(problem)
    for sid, (day, index, room_id) in placements.items():
        timetable.place(sid, Placement(day, index, room_id))
    return timetable


@pytest.fixture()
def db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        from app.config.seed import seed_defaults

        seed_defaults(session)
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(db):
    from fastapi.testclient import TestClient

    from app.main import app

    with TestClient(app) as test_client:
        yield test_client
