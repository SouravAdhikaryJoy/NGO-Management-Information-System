from typing import Optional

from sqlalchemy import Boolean, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.base import TimestampMixin

EMPLOYMENT_TYPES = ["FULL_TIME", "PART_TIME", "ADJUNCT"]
AVAILABILITY_STATES = ["UNAVAILABLE", "AVAILABLE", "PREFERRED"]


class Teacher(Base, TimestampMixin):
    __tablename__ = "teachers"
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id"))
    max_sessions_per_day: Mapped[int] = mapped_column(Integer, default=4)
    max_sessions_per_week: Mapped[int] = mapped_column(Integer, default=18)
    employment_type: Mapped[str] = mapped_column(String(16), default="FULL_TIME")
    prefers_back_to_back: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)


class TeacherAvailability(Base, TimestampMixin):
    __tablename__ = "teacher_availability"
    __table_args__ = (
        UniqueConstraint("teacher_id", "day_of_week", "slot_index", name="uq_teacher_avail"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    teacher_id: Mapped[int] = mapped_column(ForeignKey("teachers.id"))
    day_of_week: Mapped[str] = mapped_column(String(3))
    slot_index: Mapped[int] = mapped_column(Integer)
    availability: Mapped[str] = mapped_column(String(16), default="AVAILABLE")


class TeacherCoursePreference(Base, TimestampMixin):
    __tablename__ = "teacher_course_preferences"
    __table_args__ = (
        UniqueConstraint("teacher_id", "course_id", name="uq_teacher_course_pref"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    teacher_id: Mapped[int] = mapped_column(ForeignKey("teachers.id"))
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"))
    preference: Mapped[int] = mapped_column(Integer)  # 1..5, 5 = most preferred
