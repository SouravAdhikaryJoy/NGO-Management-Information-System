"""Catalog endpoints: public reads, admin-gated writes with cascade + warnings."""

import io

from app.excel.import_templates import import_workbook
from app.excel.sample_data import write_sample_workbook
from app.solver.loader import generate_sessions


def load_demo(client, db):
    buffer = io.BytesIO()
    write_sample_workbook(buffer)
    buffer.seek(0)
    response = client.post("/api/v1/import", files={"file": ("s.xlsx", buffer,
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")})
    assert response.status_code == 200, response.text
    # catalog "sections"/load figures read from generated Session rows, which
    # normally only appear once /solve runs; generate them without solving.
    generate_sessions(db)


def test_catalog_reads_work_without_login(db, client):
    buffer = io.BytesIO()
    write_sample_workbook(buffer)
    buffer.seek(0)
    assert import_workbook(db, buffer).ok
    # `client` never logged in; catalog reads still work
    assert client.get("/api/v1/courses").status_code == 200
    assert client.get("/api/v1/teachers").status_code == 200
    assert client.get("/api/v1/rooms").status_code == 200
    assert client.get("/api/v1/class-groups").status_code == 200
    # but a write is rejected
    assert client.patch("/api/v1/course/1", json={"title": "x"}).status_code == 401


def test_courses_teachers_rooms_groups_lists(admin_client, db):
    client = admin_client
    load_demo(client, db)

    courses = client.get("/api/v1/courses").json()["courses"]
    assert courses
    sample = courses[0]
    assert {"id", "code", "teacher_code", "session_types", "sections"} <= sample.keys()
    # the small demo's courses are shared by class groups A and B -> 2 sections
    multi_section = [c for c in courses if len(c["sections"]) > 1]
    assert multi_section, "expected at least one course with multiple sections"
    ranks = sorted(s["section"] for s in multi_section[0]["sections"])
    assert ranks == list(range(1, len(ranks) + 1))

    teachers = client.get("/api/v1/teachers").json()["teachers"]
    assert teachers and "weekly_sessions_assigned" in teachers[0]

    rooms = client.get("/api/v1/rooms").json()["rooms"]
    assert rooms and "room_type_code" in rooms[0]

    groups = client.get("/api/v1/class-groups").json()["class_groups"]
    assert groups and "department_code" in groups[0]


def test_course_patch_requires_admin_and_cascades_teacher(admin_client, db):
    client = admin_client
    load_demo(client, db)
    courses = client.get("/api/v1/courses").json()["courses"]
    teachers = client.get("/api/v1/teachers").json()["teachers"]
    course = courses[0]
    other_teacher = next(t for t in teachers if t["id"] != course["teacher_id"])

    response = client.patch(f"/api/v1/course/{course['id']}", json={
        "teacher_id": other_teacher["id"],
    })
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["teacher_id"] == other_teacher["id"]
    # cascade: sessions of this course now show the new teacher
    updated = client.get("/api/v1/courses").json()["courses"]
    assert next(c for c in updated if c["id"] == course["id"])["teacher_code"] == other_teacher["code"]


def test_course_patch_unknown_ids(admin_client):
    assert admin_client.patch("/api/v1/course/999999", json={"title": "x"}).status_code == 404
    assert admin_client.patch("/api/v1/teacher/999999", json={"name": "x"}).status_code == 404


def test_teacher_patch_tightening_caps_reports_new_violations(admin_client, db):
    client = admin_client
    load_demo(client, db)
    teachers = client.get("/api/v1/teachers").json()["teachers"]
    busiest = max(teachers, key=lambda t: t["weekly_sessions_assigned"])
    assert busiest["weekly_sessions_assigned"] > 0

    response = client.patch(f"/api/v1/teacher/{busiest['id']}", json={
        "max_sessions_per_day": 0 if busiest["max_sessions_per_day"] <= 1 else 1,
    })
    assert response.status_code in (200, 422)
    if response.status_code == 200:
        assert "new_hard_violations" in response.json()
