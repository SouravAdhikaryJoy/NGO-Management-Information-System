from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as DbSession

from app.api.errors import api_error
from app.config.defaults import parse_config_value
from app.database import get_db
from app.models import ConstraintWeight, SystemConfig
from app.schemas.api import (
    ConfigOut,
    ConfigPatchRequest,
    WeightOut,
    WeightsPatchRequest,
)

router = APIRouter(tags=["config"])


@router.get("/config/weights", response_model=list[WeightOut])
def get_weights(db: DbSession = Depends(get_db)):
    return [
        WeightOut(
            constraint_key=w.constraint_key, tier=w.tier, weight=w.weight,
            is_hard=w.is_hard, enabled=w.enabled,
        )
        for w in db.query(ConstraintWeight).order_by(ConstraintWeight.constraint_key).all()
    ]


@router.patch("/config/weights", response_model=list[WeightOut])
def patch_weights(request: WeightsPatchRequest, db: DbSession = Depends(get_db)):
    for patch in request.weights:
        row = (
            db.query(ConstraintWeight)
            .filter(ConstraintWeight.constraint_key == patch.constraint_key)
            .one_or_none()
        )
        if row is None:
            raise api_error(
                404, "unknown_constraint",
                f"no constraint with key {patch.constraint_key!r}",
            )
        for field in ("tier", "weight", "is_hard", "enabled"):
            value = getattr(patch, field)
            if value is not None:
                setattr(row, field, value)
    db.commit()
    return get_weights(db)


@router.get("/config/system", response_model=list[ConfigOut])
def get_system_config(db: DbSession = Depends(get_db)):
    return [
        ConfigOut(key=c.key, value=c.value, value_type=c.value_type, description=c.description)
        for c in db.query(SystemConfig).order_by(SystemConfig.key).all()
    ]


@router.patch("/config/system", response_model=list[ConfigOut])
def patch_system_config(request: ConfigPatchRequest, db: DbSession = Depends(get_db)):
    for patch in request.config:
        row = db.query(SystemConfig).filter(SystemConfig.key == patch.key).one_or_none()
        if row is None:
            raise api_error(404, "unknown_config_key", f"no config key {patch.key!r}")
        try:
            parse_config_value(patch.value, row.value_type)
        except (TypeError, ValueError):
            raise api_error(
                422, "bad_config_value",
                f"value {patch.value!r} is not a valid {row.value_type} for key {patch.key!r}",
            )
        row.value = patch.value
    db.commit()
    return get_system_config(db)
