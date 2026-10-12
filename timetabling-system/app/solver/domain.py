"""Pure in-memory solver domain, decoupled from the ORM.

Constraints and moves operate only on these structures, which makes every
constraint unit-testable with tiny synthetic problems (no database needed).

A Placement assigns a session to (day, start slot_index, room). A session of
duration d occupies slot indexes [index, index + d - 1] on that day.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

SlotKey = Tuple[str, int]  # (day_of_week, slot_index)


@dataclass(frozen=True)
class SlotData:
    day: str
    index: int
    is_break: bool = False
    # None = any session type may start here; otherwise the allowed subset
    # (e.g. {"LAB"} or {"LECTURE", "TUTORIAL"}) — fixed lab/theory timeslots.
    allowed_types: Optional[frozenset] = None


@dataclass(frozen=True)
class RoomData:
    id: int
    code: str
    capacity: int
    room_type_id: int
    building_id: int


@dataclass(frozen=True)
class TeacherData:
    id: int
    code: str
    max_sessions_per_day: int
    max_sessions_per_week: int
    unavailable: frozenset = frozenset()  # of SlotKey
    preferred: frozenset = frozenset()  # of SlotKey
    prefers_back_to_back: Optional[bool] = None


@dataclass(frozen=True)
class GroupData:
    id: int
    code: str
    size: int


@dataclass(frozen=True)
class SessionData:
    id: int
    course_id: int
    course_code: str
    group_id: int
    teacher_id: int
    session_type: str
    duration: int
    required_room_type_id: int
    is_difficult: bool = False
    is_locked: bool = False
    locked_day: Optional[str] = None
    locked_index: Optional[int] = None
    locked_room_id: Optional[int] = None


@dataclass(frozen=True)
class Placement:
    day: str
    index: int
    room_id: int


@dataclass
class WeightRow:
    tier: int
    weight: float
    is_hard: bool
    enabled: bool


@dataclass
class Problem:
    slots: Dict[SlotKey, SlotData]
    rooms: Dict[int, RoomData]
    teachers: Dict[int, TeacherData]
    groups: Dict[int, GroupData]
    sessions: Dict[int, SessionData]
    qualified_teachers: Dict[int, Set[int]]  # course_id -> teacher ids
    teacher_course_pref: Dict[Tuple[int, int], int]  # (teacher_id, course_id) -> 1..5
    config: Dict[str, object] = field(default_factory=dict)
    weights: Dict[str, WeightRow] = field(default_factory=dict)

    # derived, built in __post_init__
    days: List[str] = field(default_factory=list)
    day_slot_indexes: Dict[str, List[int]] = field(default_factory=dict)  # sorted, non-break

    def __post_init__(self):
        by_day: Dict[str, List[int]] = {}
        for (day, index), slot in self.slots.items():
            if not slot.is_break:
                by_day.setdefault(day, []).append(index)
        day_order = ["SAT", "SUN", "MON", "TUE", "WED", "THU", "FRI"]
        self.days = sorted(by_day, key=lambda d: day_order.index(d) if d in day_order else 99)
        self.day_slot_indexes = {d: sorted(v) for d, v in by_day.items()}

    def cfg(self, key: str, default=None):
        return self.config.get(key, default)

    def occupied_indexes(self, session: SessionData, placement: Placement) -> List[int]:
        return list(range(placement.index, placement.index + session.duration))

    def all_placements(self, session: SessionData):
        """Iterate every syntactically possible placement for a session."""
        for day, indexes in self.day_slot_indexes.items():
            for index in indexes:
                for room_id in self.rooms:
                    yield Placement(day, index, room_id)


class Timetable:
    """Assignment state with incremental indexes for O(1) clash lookups."""

    def __init__(self, problem: Problem):
        self.problem = problem
        self.placements: Dict[int, Placement] = {}
        # (resource_id, day, index) -> set of occupying session ids. A set,
        # not a single id: move evaluation can transiently place a candidate
        # session onto a slot another session already legitimately holds
        # (that's exactly what hard-constraint checking needs to detect), so
        # a second occupant must never silently clobber the first one's
        # bookkeeping — it has to be tracked and cleanly un-recorded on its
        # own removal, independent of whatever else is sharing the slot.
        self.room_busy: Dict[Tuple[int, str, int], Set[int]] = {}
        self.teacher_busy: Dict[Tuple[int, str, int], Set[int]] = {}
        self.group_busy: Dict[Tuple[int, str, int], Set[int]] = {}
        # entity_id -> day -> set of occupied indexes, derived from *_busy
        # emptiness so a rejected/undone overlapping placement can never
        # erase an unrelated session's still-legitimate slot.
        self.teacher_slots: Dict[int, Dict[str, Set[int]]] = {}
        self.group_slots: Dict[int, Dict[str, Set[int]]] = {}
        # (course_id, group_id, day) -> number of sessions (for H13, O(1))
        self.course_group_day: Dict[Tuple[int, int, str], int] = {}

    def clone(self) -> "Timetable":
        other = Timetable(self.problem)
        for sid, pl in self.placements.items():
            other.place(sid, pl)
        return other

    def occupied(self, session_id: int) -> List[Tuple[str, int]]:
        pl = self.placements[session_id]
        s = self.problem.sessions[session_id]
        return [(pl.day, i) for i in range(pl.index, pl.index + s.duration)]

    def place(self, session_id: int, placement: Placement) -> None:
        assert session_id not in self.placements, f"session {session_id} already placed"
        s = self.problem.sessions[session_id]
        self.placements[session_id] = placement
        for i in range(placement.index, placement.index + s.duration):
            self.room_busy.setdefault((placement.room_id, placement.day, i), set()).add(session_id)
            self.teacher_busy.setdefault((s.teacher_id, placement.day, i), set()).add(session_id)
            self.group_busy.setdefault((s.group_id, placement.day, i), set()).add(session_id)
            self.teacher_slots.setdefault(s.teacher_id, {}).setdefault(placement.day, set()).add(i)
            self.group_slots.setdefault(s.group_id, {}).setdefault(placement.day, set()).add(i)
        key = (s.course_id, s.group_id, placement.day)
        self.course_group_day[key] = self.course_group_day.get(key, 0) + 1

    def remove(self, session_id: int) -> Placement:
        placement = self.placements.pop(session_id)
        s = self.problem.sessions[session_id]
        for i in range(placement.index, placement.index + s.duration):
            room_key = (placement.room_id, placement.day, i)
            teacher_key = (s.teacher_id, placement.day, i)
            group_key = (s.group_id, placement.day, i)
            self.room_busy.get(room_key, set()).discard(session_id)
            if not self.room_busy.get(room_key):
                self.room_busy.pop(room_key, None)
            self.teacher_busy.get(teacher_key, set()).discard(session_id)
            if not self.teacher_busy.get(teacher_key):
                self.teacher_busy.pop(teacher_key, None)
                self.teacher_slots.get(s.teacher_id, {}).get(placement.day, set()).discard(i)
            self.group_busy.get(group_key, set()).discard(session_id)
            if not self.group_busy.get(group_key):
                self.group_busy.pop(group_key, None)
                self.group_slots.get(s.group_id, {}).get(placement.day, set()).discard(i)
        key = (s.course_id, s.group_id, placement.day)
        remaining = self.course_group_day.get(key, 0) - 1
        if remaining > 0:
            self.course_group_day[key] = remaining
        else:
            self.course_group_day.pop(key, None)
        return placement

    def unplaced_sessions(self) -> List[int]:
        return [sid for sid in self.problem.sessions if sid not in self.placements]

    def conflicting_sessions(self, session_id: int, placement: Placement) -> Set[int]:
        """Sessions already placed that share room/teacher/group slots with this placement."""
        s = self.problem.sessions[session_id]
        conflicts: Set[int] = set()
        for i in range(placement.index, placement.index + s.duration):
            for busy, rid in (
                (self.room_busy, placement.room_id),
                (self.teacher_busy, s.teacher_id),
                (self.group_busy, s.group_id),
            ):
                conflicts.update(busy.get((rid, placement.day, i), set()) - {session_id})
        return conflicts
