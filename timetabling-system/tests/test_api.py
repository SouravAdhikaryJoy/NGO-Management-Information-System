"""End-to-end API tests: import -> solve -> timetable -> exports -> overrides."""

import io

from app.excel.sample_data import write_sample_workbook


def upload_sample(client):
    buffer = io.BytesIO()
    write_sample_workbook(buffer)
    buffer.seek(0)
    response = client.post(
        "/api/v1/import",
        files={"file": ("sample.xlsx", buffer,
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["ok"], body["errors"]
    return body


def shrink_budgets(client):
    response = client.patch("/api/v1/config/system", json={"config": [
        {"key": "phase2_time_budget_seconds", "value": "2"},
        {"key": "phase2_iteration_budget", "value": "800"},
    ]})
    assert response.status_code == 200, response.text


def solve(client):
    response = client.post("/api/v1/solve")
    assert response.status_code == 202
    job_id = response.json()["job_id"]
    # TestClient runs BackgroundTasks synchronously before returning
    status = client.get(f"/api/v1/solve/{job_id}/status").json()
    assert status["status"] == "COMPLETED", status
    assert status["hard_violations"] == 0
    return job_id


def test_full_flow(client):
    upload_sample(client)
    shrink_budgets(client)
    job_id = solve(client)

    # canonical JSON timetable
    response = client.get(f"/api/v1/timetable/{job_id}")
    assert response.status_code == 200
    body = response.json()
    assert body["run"]["job_id"] == job_id
    assert len(body["sessions"]) > 40
    assert all(row["violations"] == 0 for row in body["feasibility_report"])
    assert len(body["soft_constraint_report"]) == 19

    # exports
    for fmt, content_type in [
        ("xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
        ("csv", "text/csv"),
        ("ics", "text/calendar"),
        ("pdf", "application/pdf"),
    ]:
        response = client.get(f"/api/v1/timetable/{job_id}/export?format={fmt}")
        assert response.status_code == 200, (fmt, response.text)
        assert response.headers["content-type"].startswith(content_type)
        assert len(response.content) > 100
    assert client.get(f"/api/v1/timetable/{job_id}/export?format=doc").status_code == 400

    # per-teacher / per-group schedules
    session = body["sessions"][0]
    teachers = client.get("/api/v1/config/weights")  # warm-up sanity
    assert teachers.status_code == 200

    schedule = client.get("/api/v1/teacher/1/schedule")
    assert schedule.status_code == 200
    assert all(row["teacher_code"] == schedule.json()["teacher"]["code"]
               for row in schedule.json()["sessions"])

    schedule = client.get("/api/v1/group/1/schedule")
    assert schedule.status_code == 200
    assert len(schedule.json()["sessions"]) > 0


def test_solve_status_not_found(client):
    response = client.get("/api/v1/solve/nope/status")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "job_not_found"


def test_timetable_requires_completed_run(client):
    upload_sample(client)
    response = client.get("/api/v1/timetable/nope")
    assert response.status_code == 404
    assert "error" in response.json()


def test_session_patch_validates_hard_constraints(client):
    upload_sample(client)
    shrink_budgets(client)
    job_id = solve(client)
    sessions = client.get(f"/api/v1/timetable/{job_id}").json()["sessions"]

    # find two singleton sessions taught by the same teacher in different slots
    by_teacher = {}
    for row in sessions:
        if row["duration_slots"] == 1:
            by_teacher.setdefault(row["teacher_code"], []).append(row)
    pair = next(rows for rows in by_teacher.values() if len(rows) >= 2)
    a, b = pair[0], pair[1]

    # moving a onto b's slot creates a teacher clash -> structured 409
    response = client.patch(f"/api/v1/session/{a['id']}", json={
        "day_of_week": b["day_of_week"], "slot_index": b["slot_index"],
    })
    assert response.status_code == 409, response.text
    body = response.json()["error"]
    assert body["code"] == "hard_constraint_violation"
    assert "H02_teacher_clash" in body["details"]

    # a no-op patch (same assignment) is accepted
    response = client.patch(f"/api/v1/session/{a['id']}", json={
        "day_of_week": a["day_of_week"], "slot_index": a["slot_index"],
    })
    assert response.status_code == 200, response.text
    assert "soft_penalty" in response.json()


def test_weights_and_config_endpoints(client):
    weights = client.get("/api/v1/config/weights").json()
    assert len(weights) == 33  # 14 hard + 19 soft
    response = client.patch("/api/v1/config/weights", json={"weights": [
        {"constraint_key": "S03_group_gaps", "weight": 20.0},
    ]})
    assert response.status_code == 200
    updated = {w["constraint_key"]: w for w in response.json()}
    assert updated["S03_group_gaps"]["weight"] == 20.0

    assert client.patch("/api/v1/config/weights", json={"weights": [
        {"constraint_key": "NOPE", "weight": 1.0},
    ]}).status_code == 404

    config = client.get("/api/v1/config/system").json()
    assert any(c["key"] == "random_seed" for c in config)
    response = client.patch("/api/v1/config/system", json={"config": [
        {"key": "random_seed", "value": "7"},
    ]})
    assert response.status_code == 200
    assert client.patch("/api/v1/config/system", json={"config": [
        {"key": "random_seed", "value": "not-an-int"},
    ]}).status_code == 422

    # template download
    response = client.get("/api/v1/import/template")
    assert response.status_code == 200
    assert len(response.content) > 1000
