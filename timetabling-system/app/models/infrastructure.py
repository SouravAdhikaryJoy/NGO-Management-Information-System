from datetime import time
from typing import Optional

from sqlalchemy import Boolean, ForeignKey, Integer, String, Time, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.base import TimestampMixin

DAYS = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]


class University(Base, TimestampMixin):
    __tablename__ = "universities"
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))


class Department(Base, TimestampMixin):
    __tablename__ = "departments"
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    university_id: Mapped[int] = mapped_column(ForeignKey("universities.id"))


class Building(Base, TimestampMixin):
    __tablename__ = "buildings"
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    university_id: Mapped[int] = mapped_column(ForeignKey("universities.id"))


class RoomType(Base, TimestampMixin):
    __tablename__ = "room_types"
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))


class Room(Base, TimestampMixin):
    __tablename__ = "rooms"
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    building_id: Mapped[int] = mapped_column(ForeignKey("buildings.id"))
    room_type_id: Mapped[int] = mapped_column(ForeignKey("room_types.id"))
    capacity: Mapped[int] = mapped_column(Integer)


class TimeSlot(Base, TimestampMixin):
    __tablename__ = "time_slots"
    __table_args__ = (UniqueConstraint("day_of_week", "slot_index", name="uq_timeslot_day_index"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    day_of_week: Mapped[str] = mapped_column(String(3))
    slot_index: Mapped[int] = mapped_column(Integer)
    start_time: Mapped[time] = mapped_column(Time)
    end_time: Mapped[time] = mapped_column(Time)
    is_break: Mapped[bool] = mapped_column(Boolean, default=False)
    # comma list of session types allowed to start here (e.g. "LAB" or
    # "LECTURE,TUTORIAL"); NULL/blank means any session type may use it.
    # Implements fixed timeslot pools per class type (H15).
    session_type_scope: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
