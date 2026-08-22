from sqlalchemy import Boolean, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.base import TimestampMixin


class ConstraintWeight(Base, TimestampMixin):
    __tablename__ = "constraint_weights"
    id: Mapped[int] = mapped_column(primary_key=True)
    constraint_key: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    tier: Mapped[int] = mapped_column(Integer)
    weight: Mapped[float] = mapped_column(Float)
    is_hard: Mapped[bool] = mapped_column(Boolean, default=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)


class SystemConfig(Base, TimestampMixin):
    __tablename__ = "system_config"
    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    value: Mapped[str] = mapped_column(String(255))
    value_type: Mapped[str] = mapped_column(String(8), default="str")  # int|float|str|bool
    description: Mapped[str] = mapped_column(String(255), default="")
