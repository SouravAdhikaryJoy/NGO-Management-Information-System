"""Non-xlsx export formats: csv, ics, and a minimal dependency-free pdf."""

from __future__ import annotations

import csv
import io
from typing import List

DAY_TO_ICS = {"MON": "MO", "TUE": "TU", "WED": "WE", "THU": "TH", "FRI": "FR",
              "SAT": "SA", "SUN": "SU"}
# arbitrary anchor week (Monday) for weekly-recurring events
ICS_ANCHOR = {"MON": "20260105", "TUE": "20260106", "WED": "20260107",
              "THU": "20260108", "FRI": "20260109", "SAT": "20260110", "SUN": "20260104"}

CSV_FIELDS = [
    "session_id", "course_code", "course_title", "session_type", "class_group_code",
    "teacher_code", "teacher_name", "day_of_week", "slot_index", "duration_slots",
    "room_code", "start_time", "end_time",
]


def to_csv(rows: List[dict]) -> str:
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=CSV_FIELDS, extrasaction="ignore")
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    return buffer.getvalue()


def to_ics(rows: List[dict]) -> str:
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//university-timetabling//routine//EN",
    ]
    for row in rows:
        day = row.get("day_of_week")
        start = (row.get("start_time") or "09:00").replace(":", "")
        end = (row.get("end_time") or "09:50").replace(":", "")
        if not day:
            continue
        lines += [
            "BEGIN:VEVENT",
            f"UID:session-{row['session_id']}@timetabling",
            f"SUMMARY:{row['course_code']} ({row['session_type']}) {row['class_group_code']}",
            f"LOCATION:{row.get('room_code') or ''}",
            f"DESCRIPTION:Teacher {row.get('teacher_name') or ''}",
            f"DTSTART:{ICS_ANCHOR[day]}T{start}00",
            f"DTEND:{ICS_ANCHOR[day]}T{end}00",
            f"RRULE:FREQ=WEEKLY;BYDAY={DAY_TO_ICS[day]}",
            "END:VEVENT",
        ]
    lines.append("END:VCALENDAR")
    return "\r\n".join(lines) + "\r\n"


def _pdf_escape(text: str) -> str:
    return text.replace("\\", r"\\").replace("(", r"\(").replace(")", r"\)")


def to_pdf(rows: List[dict], title: str = "University Routine") -> bytes:
    """Minimal single-font PDF: one line per scheduled session, grouped by day."""
    day_order = ["SAT", "SUN", "MON", "TUE", "WED", "THU", "FRI"]
    rows = sorted(
        [r for r in rows if r.get("day_of_week")],
        key=lambda r: (day_order.index(r["day_of_week"]), r["slot_index"], r.get("room_code") or ""),
    )
    lines = [title, ""]
    current_day = None
    for row in rows:
        if row["day_of_week"] != current_day:
            current_day = row["day_of_week"]
            lines += ["", f"--- {current_day} ---"]
        lines.append(
            f"slot {row['slot_index']}  {row['course_code']} ({row['session_type']})  "
            f"{row['class_group_code']}  {row.get('teacher_code') or ''}  "
            f"@ {row.get('room_code') or '?'}"
        )

    pages, page = [], []
    for line in lines:
        page.append(line)
        if len(page) >= 54:
            pages.append(page)
            page = []
    if page or not pages:
        pages.append(page)

    objects: List[bytes] = []

    def add(obj: bytes) -> int:
        objects.append(obj)
        return len(objects)

    font_id = add(b"<< /Type /Font /Subtype /Type1 /BaseFont /Courier >>")
    content_ids, page_ids = [], []
    for page_lines in pages:
        parts = ["BT", "/F1 9 Tf", "1 0 0 1 40 800 Tm", "12 TL"]
        for line in page_lines:
            parts.append(f"({_pdf_escape(line)}) Tj T*")
        parts.append("ET")
        stream = "\n".join(parts).encode("latin-1", "replace")
        content_ids.append(add(
            b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream"
        ))
    pages_id = len(objects) + len(pages) + 1
    for content_id in content_ids:
        page_ids.append(add(
            f"<< /Type /Page /Parent {pages_id} 0 R /MediaBox [0 0 595 842] "
            f"/Contents {content_id} 0 R /Resources << /Font << /F1 {font_id} 0 R >> >> >>"
            .encode()
        ))
    kids = " ".join(f"{pid} 0 R" for pid in page_ids)
    assert add(
        f"<< /Type /Pages /Kids [{kids}] /Count {len(page_ids)} >>".encode()
    ) == pages_id
    catalog_id = add(f"<< /Type /Catalog /Pages {pages_id} 0 R >>".encode())

    out = io.BytesIO()
    out.write(b"%PDF-1.4\n")
    offsets = []
    for i, obj in enumerate(objects, start=1):
        offsets.append(out.tell())
        out.write(f"{i} 0 obj\n".encode() + obj + b"\nendobj\n")
    xref_pos = out.tell()
    out.write(f"xref\n0 {len(objects) + 1}\n".encode())
    out.write(b"0000000000 65535 f \n")
    for offset in offsets:
        out.write(f"{offset:010d} 00000 n \n".encode())
    out.write(
        f"trailer\n<< /Size {len(objects) + 1} /Root {catalog_id} 0 R >>\n"
        f"startxref\n{xref_pos}\n%%EOF\n".encode()
    )
    return out.getvalue()
