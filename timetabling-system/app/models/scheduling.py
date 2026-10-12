from typing import Optional

from sqlalchemy import JSON, Boolean, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.base import TimestampMixin

RUN_STATUSES = ["PENDING", "RUNNING", "PHASE1_FAILED", "COMPLETED", "FAILED"]


class Session(Base, TimestampMixin):
    """One weekly meeting of a course for a class group (the scheduling unit)."""

    __tablename__ = "sessions"
    id: Mapped[int] = mapped_column(primary_key=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"))
    class_group_id: Mapped[int] = mapped_column(ForeignKey("class_groups.id"))
    teacher_id: Mapped[int] = mapped_column(ForeignKey("teachers.id"))
    session_type: Mapped[str] = mapped_column(String(16))
    duration_slots: Mapped[int] = mapped_column(Integer, default=1)
    required_room_type_id: Mapped[int] = mapped_column(ForeignKey("room_types.id"))
    sequence_no: Mapped[int] = mapped_column(Integer, default=1)

    # assignment (null until solved)
    day_of_week: Mapped[Optional[str]] = mapped_column(String(3), nullable=True)
    slot_index: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    room_id: Mapped[Optional[int]] = mapped_column(ForeignKey("rooms.id"), nullable=True)

    is_locked: Mapped[bool] = mapped_column(Boolean, default=False)
    locked_day: Mapped[Optional[str]] = mapped_column(String(3), nullable=True)
    locked_slot_index: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    locked_room_id: Mapped[Optional[int]] = mapped_column(ForeignKey("rooms.id"), nullable=True)


class SolverRun(Base, TimestampMixin):
    __tablename__ = "solver_runs"
    id: Mapped[int] = mapped_column(primary_key=True)
    job_id: Mapped[str] = mapped_column(String(36), unique=True, index=True)
    status: Mapped[str] = mapped_column(String(16), default="PENDING")
    seed: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    phase1_iterations: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    phase2_iterations: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    runtime_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    hard_violations: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    soft_penalty: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    weights_snapshot: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    config_snapshot: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
