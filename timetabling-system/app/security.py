"""Minimal, dependency-free session auth.

All *read* endpoints (timetable, schedules, catalog lists) stay public per
the design brief. Every *write* endpoint (import, solve, manual edits, config
changes, course/teacher reassignment) requires a logged-in account via a
signed, HttpOnly session cookie. No external auth library: passwords are
hashed with stdlib PBKDF2, and the cookie is an HMAC-signed, expiring token
(a JWT would be equivalent complexity here with no expressiveness gain).
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import os
import time

from fastapi import Depends, Request
from sqlalchemy.orm import Session as DbSession

from app.api.errors import api_error
from app.database import get_db
from app.models import User

COOKIE_NAME = "session"
SESSION_TTL_SECONDS = 60 * 60 * 12  # 12 hours
_PBKDF2_ITERATIONS = 260_000

# A dev-only fallback secret so the app still runs out of the box; set
# SESSION_SECRET in any real deployment (sessions won't survive a restart
# with the fallback, since it's re-randomised each boot).
SESSION_SECRET = os.environ.get("SESSION_SECRET") or base64.urlsafe_b64encode(
    os.urandom(32)
).decode()


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, _PBKDF2_ITERATIONS)
    return f"{salt.hex()}${digest.hex()}"


def verify_password(password: str, password_hash: str) -> bool:
    try:
        salt_hex, digest_hex = password_hash.split("$", 1)
    except ValueError:
        return False
    salt = bytes.fromhex(salt_hex)
    expected = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, _PBKDF2_ITERATIONS)
    return hmac.compare_digest(expected.hex(), digest_hex)


def _sign(payload: str) -> str:
    return hmac.new(SESSION_SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()


def make_token(username: str) -> str:
    expires = int(time.time()) + SESSION_TTL_SECONDS
    payload = f"{username}:{expires}"
    signature = _sign(payload)
    return base64.urlsafe_b64encode(f"{payload}:{signature}".encode()).decode()


def read_token(token: str) -> str | None:
    """Return the username if the token is well-formed, unexpired and
    correctly signed; None otherwise."""
    try:
        raw = base64.urlsafe_b64decode(token.encode()).decode()
        username, expires, signature = raw.rsplit(":", 2)
    except Exception:
        return None
    if not hmac.compare_digest(_sign(f"{username}:{expires}"), signature):
        return None
    if int(expires) < time.time():
        return None
    return username


def current_user(request: Request, db: DbSession = Depends(get_db)) -> User | None:
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        return None
    username = read_token(token)
    if username is None:
        return None
    return db.query(User).filter(User.username == username).one_or_none()


def require_admin(request: Request, db: DbSession = Depends(get_db)) -> User:
    user = current_user(request, db)
    if user is None:
        raise api_error(
            401, "authentication_required",
            "log in with an admin account to make changes",
        )
    return user
