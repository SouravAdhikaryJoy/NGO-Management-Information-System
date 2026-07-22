from fastapi import APIRouter, Depends, Response
from pydantic import BaseModel
from sqlalchemy.orm import Session as DbSession

from app.api.errors import api_error
from app.database import get_db
from app.models import User
from app.security import COOKIE_NAME, SESSION_TTL_SECONDS, current_user, make_token, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/login")
def login(payload: LoginRequest, response: Response, db: DbSession = Depends(get_db)):
    user = db.query(User).filter(User.username == payload.username).one_or_none()
    if user is None or not verify_password(payload.password, user.password_hash):
        raise api_error(401, "invalid_credentials", "username or password is incorrect")
    response.set_cookie(
        COOKIE_NAME, make_token(user.username),
        max_age=SESSION_TTL_SECONDS, httponly=True, samesite="lax",
    )
    return {"username": user.username, "is_admin": user.is_admin}


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(COOKIE_NAME)
    return {"ok": True}


@router.get("/me")
def me(user: User | None = Depends(current_user)):
    if user is None:
        return {"authenticated": False}
    return {"authenticated": True, "username": user.username, "is_admin": user.is_admin}
