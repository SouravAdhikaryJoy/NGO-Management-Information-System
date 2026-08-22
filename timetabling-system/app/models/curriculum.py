from typing import Optional

from sqlalchemy import Boolean, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.base import TimestampMixin

SESSION_TYPES = ["LECTURE", "LAB", "TUTORIAL"]


class Course(Base, TimestampMixin):
    __tablename__ = "courses"
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(255))
    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id"))
    semester: Mapped[int] = mapped_column(Integer)
    credit_hours: Mapped[float] = mapped_column(Float)
    is_difficult: Mapped[bool] = mapped_column(Boolean, default=False)
    teacher_id: Mapped[Optional[int]] = mapped_column(ForeignKey("teachers.id"), nullable=True)


class CourseSessionType(Base, TimestampMixin):
    __tablename__ = "course_session_types"
    __table_args__ = (UniqueConstraint("course_id", "session_type", name="uq_course_session_type"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"))
    session_type: Mapped[str] = mapped_column(String(16))
    sessions_per_week: Mapped[int] = mapped_column(Integer)
    duration_slots: Mapped[int] = mapped_column(Integer, default=1)
    required_room_type_id: Mapped[int] = mapped_column(ForeignKey("room_types.id"))


class ClassGroup(Base, TimestampMixin):
    __tablename__ = "class_groups"
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id"))
    semester: Mapped[int] = mapped_column(Integer)
    size: Mapped[int] = mapped_column(Integer)
