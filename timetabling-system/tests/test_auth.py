"""Auth: default admin seeding, login/logout, and write-endpoint gating."""

import io

from app.excel.sample_data import write_sample_workbook


def test_default_admin_seeded(db):
    from app.models import User

    admin = db.query(User).filter(User.username == "admin").one()
    assert admin.is_admin


def test_me_when_logged_out(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 200
    assert response.json() == {"authenticated": False}


def test_login_wrong_password(client):
    response = client.post("/api/v1/auth/login", json={
        "username": "admin", "password": "wrong",
    })
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "invalid_credentials"


def test_login_logout_flow(client):
    response = client.post("/api/v1/auth/login", json={
        "username": "admin", "password": "admin123",
    })
    assert response.status_code == 200
    assert response.json() == {"username": "admin", "is_admin": True}
    assert "session" in response.cookies

    me = client.get("/api/v1/auth/me")
    assert me.json() == {"authenticated": True, "username": "admin", "is_admin": True}

    logout = client.post("/api/v1/auth/logout")
    assert logout.status_code == 200
    me_after = client.get("/api/v1/auth/me")
    assert me_after.json() == {"authenticated": False}


def test_writes_require_auth_reads_stay_public(client):
    # reads work with no session at all
    assert client.get("/api/v1/config/weights").status_code == 200
    assert client.get("/api/v1/config/system").status_code == 200
    assert client.get("/api/v1/courses").status_code == 200
    assert client.get("/api/v1/teachers").status_code == 200
    assert client.get("/api/v1/rooms").status_code == 200
    assert client.get("/api/v1/class-groups").status_code == 200

    # writes are rejected without a session
    demo = client.post("/api/v1/import/demo")
    assert demo.status_code == 401
    assert demo.json()["error"]["code"] == "authentication_required"

    buffer = io.BytesIO()
    write_sample_workbook(buffer)
    buffer.seek(0)
    upload = client.post("/api/v1/import", files={"file": ("s.xlsx", buffer,
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")})
    assert upload.status_code == 401

    assert client.post("/api/v1/solve").status_code == 401
    assert client.patch("/api/v1/config/weights", json={"weights": []}).status_code == 401
    assert client.patch("/api/v1/config/system", json={"config": []}).status_code == 401
    assert client.patch("/api/v1/session/1", json={}).status_code == 401
    assert client.patch("/api/v1/course/1", json={}).status_code == 401
    assert client.patch("/api/v1/teacher/1", json={}).status_code == 401

    # log in, then the same writes succeed (demo import)
    client.post("/api/v1/auth/login", json={"username": "admin", "password": "admin123"})
    demo_ok = client.post("/api/v1/import/demo")
    assert demo_ok.status_code == 200
    assert demo_ok.json()["ok"]
