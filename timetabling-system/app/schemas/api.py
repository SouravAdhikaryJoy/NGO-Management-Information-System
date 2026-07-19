"""Pydantic request/response schemas for /api/v1."""

from typing import List, Optional

from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: list = Field(default_factory=list)


class ErrorResponse(BaseModel):
    error: ErrorDetail


class ImportResponse(BaseModel):
    ok: bool
    counts: dict
    errors: List[dict]


class SolveResponse(BaseModel):
    job_id: str
    status: str


class SolveStatusResponse(BaseModel):
    job_id: str
    status: str
    seed: Optional[int] = None
    phase1_iterations: Optional[int] = None
    phase2_iterations: Optional[int] = None
    runtime_seconds: Optional[float] = None
    hard_violations: Optional[int] = None
    soft_penalty: Optional[float] = None
    error: Optional[str] = None


class SessionOut(BaseModel):
    id: int
    course_code: str
    course_title: str
    session_type: str
    class_group_code: str
    teacher_code: str
    teacher_name: str
    room_code: Optional[str] = None
    day_of_week: Optional[str] = None
    slot_index: Optional[int] = None
    duration_slots: int
    is_locked: bool


class SessionPatch(BaseModel):
    day_of_week: Optional[str] = None
    slot_index: Optional[int] = None
    room_id: Optional[int] = None
    teacher_id: Optional[int] = None
    lock: Optional[bool] = None


class WeightOut(BaseModel):
    constraint_key: str
    tier: int
    weight: float
    is_hard: bool
    enabled: bool


class WeightPatch(BaseModel):
    constraint_key: str
    tier: Optional[int] = None
    weight: Optional[float] = Field(default=None, ge=0)
    is_hard: Optional[bool] = None
    enabled: Optional[bool] = None


class WeightsPatchRequest(BaseModel):
    weights: List[WeightPatch]


class ConfigOut(BaseModel):
    key: str
    value: str
    value_type: str
    description: str


class ConfigPatch(BaseModel):
    key: str
    value: str


class ConfigPatchRequest(BaseModel):
    config: List[ConfigPatch]
