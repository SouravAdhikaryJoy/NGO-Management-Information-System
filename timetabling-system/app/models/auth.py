from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.base import TimestampMixin


class User(Base, TimestampMixin):
    """An account allowed to make changes (import, solve, edit). Timetable
    viewing stays public and needs no account."""

    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    is_admin: Mapped[bool] = mapped_column(Boolean, default=True)
