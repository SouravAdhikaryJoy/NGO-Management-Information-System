"""Server-rendered web UI: dashboard, timetable viewer, and SEO plumbing.

The pages are static HTML shells (semantic, crawlable, meta-tagged); live data
is fetched client-side from /api/v1. No template engine needed.
"""

from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import FileResponse, PlainTextResponse, Response

PAGES_DIR = Path(__file__).parent / "pages"

router = APIRouter(include_in_schema=False)


@router.get("/")
def index():
    return FileResponse(PAGES_DIR / "index.html", media_type="text/html")


@router.get("/timetable")
def timetable_page():
    return FileResponse(PAGES_DIR / "timetable.html", media_type="text/html")


@router.get("/robots.txt")
def robots():
    return PlainTextResponse(
        "User-agent: *\n"
        "Allow: /\n"
        "Disallow: /api/\n"
        "Sitemap: /sitemap.xml\n"
    )


@router.get("/sitemap.xml")
def sitemap(request: Request):
    base = str(request.base_url).rstrip("/")
    urls = "".join(
        f"<url><loc>{base}{path}</loc><changefreq>weekly</changefreq></url>"
        for path in ("/", "/timetable")
    )
    return Response(
        content=(
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
            f"{urls}</urlset>"
        ),
        media_type="application/xml",
    )
