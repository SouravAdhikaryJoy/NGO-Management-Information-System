"""Seed ConstraintWeight, SystemConfig and the default admin account.

Idempotent (insert-if-missing) so it is safe to call on every startup.
"""

import logging
import os

from sqlalchemy.orm import Session as DbSession

from app.config.defaults import (
    HARD_CONSTRAINT_DEFAULTS,
    SOFT_CONSTRAINT_DEFAULTS,
    SYSTEM_CONFIG_DEFAULTS,
)
from app.models import ConstraintWeight, SystemConfig, User
from app.security import hash_password

logger = logging.getLogger("timetabling.seed")


def seed_defaults(db: DbSession) -> None:
    existing_weights = {w.constraint_key for w in db.query(ConstraintWeight).all()}
    for key, tier, weight, is_hard in HARD_CONSTRAINT_DEFAULTS + SOFT_CONSTRAINT_DEFAULTS:
        if key not in existing_weights:
            db.add(ConstraintWeight(
                constraint_key=key, tier=tier, weight=weight, is_hard=is_hard, enabled=True,
            ))
    existing_config = {c.key for c in db.query(SystemConfig).all()}
    for key, (value, value_type, description) in SYSTEM_CONFIG_DEFAULTS.items():
        if key not in existing_config:
            db.add(SystemConfig(key=key, value=value, value_type=value_type, description=description))
    db.commit()
    seed_default_admin(db)


def seed_default_admin(db: DbSession) -> None:
    if db.query(User).count() > 0:
        return
    username = os.environ.get("ADMIN_USERNAME", "admin")
    password = os.environ.get("ADMIN_PASSWORD", "admin123")
    db.add(User(username=username, password_hash=hash_password(password), is_admin=True))
    db.commit()
    if "ADMIN_PASSWORD" not in os.environ:
        logger.warning(
            "No ADMIN_PASSWORD set — created default admin account '%s' with the "
            "well-known password 'admin123'. Change it or set ADMIN_USERNAME/"
            "ADMIN_PASSWORD before exposing this instance beyond local testing.",
            username,
        )


def load_system_config(db: DbSession) -> dict:
    from app.config.defaults import parse_config_value

    out = {}
    for row in db.query(SystemConfig).all():
        out[row.key] = parse_config_value(row.value, row.value_type)
    return out
