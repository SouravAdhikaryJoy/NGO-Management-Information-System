"""Shared display-label helpers (design doc section 3.1: course.section)."""

from typing import Dict, Tuple

from sqlalchemy.orm import Session as DbSession

from app.models import ClassGroup, Course, Session


def compute_sections(db: DbSession) -> Dict[Tuple[int, int], int]:
    """(course_id, class_group_id) -> 1-based section number, ranked
    alphabetically by class-group code among the groups taking that course."""
    groups_by_code = {g.id: g.code for g in db.query(ClassGroup).all()}
    course_groups: Dict[int, set] = {}
    for s in db.query(Session.course_id, Session.class_group_id).distinct().all():
        course_groups.setdefault(s.course_id, set()).add(s.class_group_id)

    sections: Dict[Tuple[int, int], int] = {}
    for course_id, group_ids in course_groups.items():
        ordered = sorted(group_ids, key=lambda gid: groups_by_code.get(gid, ""))
        for rank, group_id in enumerate(ordered, start=1):
            sections[(course_id, group_id)] = rank
    return sections


def course_group_label(course_code: str, section: int) -> str:
    return f"{course_code}.{section}"
