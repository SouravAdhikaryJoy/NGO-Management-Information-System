"""Web UI pages, SEO plumbing, and the demo/runs convenience endpoints."""


def test_home_page_serves_seo_html(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    html = response.text
    assert "<title>" in html
    assert 'name="description"' in html
    assert 'property="og:title"' in html
    assert "application/ld+json" in html
    assert 'lang="en"' in html
    # the guide is on the page
    assert "How it works" in html


def test_timetable_page(client):
    response = client.get("/timetable")
    assert response.status_code == 200
    assert 'name="description"' in response.text


def test_static_assets(client):
    assert client.get("/static/styles.css").status_code == 200
    assert client.get("/static/app.js").status_code == 200
    assert client.get("/static/timetable.js").status_code == 200


def test_robots_and_sitemap(client):
    robots = client.get("/robots.txt")
    assert robots.status_code == 200
    assert "Sitemap:" in robots.text
    sitemap = client.get("/sitemap.xml")
    assert sitemap.status_code == 200
    assert "<urlset" in sitemap.text
    assert "/timetable" in sitemap.text


def test_demo_endpoint_loads_dataset(client):
    response = client.post("/api/v1/import/demo")
    assert response.status_code == 200
    body = response.json()
    assert body["ok"], body["errors"]
    assert body["counts"]["Courses"] == 10


def test_runs_listing(client):
    assert client.get("/api/v1/solve/runs").json() == {"runs": []}
    client.post("/api/v1/import/demo")
    client.patch("/api/v1/config/system", json={"config": [
        {"key": "phase2_time_budget_seconds", "value": "1"},
        {"key": "phase2_iteration_budget", "value": "200"},
    ]})
    job_id = client.post("/api/v1/solve").json()["job_id"]
    runs = client.get("/api/v1/solve/runs").json()["runs"]
    assert runs and runs[0]["job_id"] == job_id
    assert runs[0]["status"] == "COMPLETED"
