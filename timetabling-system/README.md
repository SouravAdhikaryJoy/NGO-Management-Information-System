# University Timetabling System

Automated weekly class-routine generation for a university: Excel in, solved
routine out, with a two-phase metaheuristic solver (feasibility, then quality)
behind a versioned FastAPI — plus a built-in web UI that walks you through the
whole workflow.

## Try it in 60 seconds

```bash
pip install -r requirements.txt
uvicorn app.main:app
```

Open **http://localhost:8000** and:

1. Press **“Try it now with demo data”** — loads a built-in sample university
   (10 courses, 8 teachers, 4 class groups). No file needed.
2. Press **“Run the solver”** — live status updates; a demo-sized dataset
   solves in seconds to a minute.
3. Press **“Open timetable view”** — browse the routine by day, room, teacher
   or class group, and download it as Excel, CSV, calendar (.ics) or PDF.

For real data: download the blank Excel template from the same page, fill one
sheet per entity, and upload it. Every row is validated first — errors are
reported with the exact sheet, row and field, and nothing is half-imported.

The full specification lives in [`timetabling_system_design.md`](timetabling_system_design.md)
— constraints, data model, algorithm, and output spec. The implementation
follows it field-for-field.

## Highlights

- **14 hard constraints + 19 soft constraints**, each its own class behind a
  shared interface, registered in
  `app/solver/constraints/registry.py`. Adding a constraint = one new class
  file + one registration line; no solver changes.
- **Runtime-configurable**: every weight, tier, and threshold comes from the
  `ConstraintWeight` / `SystemConfig` tables (seeded with defaults, editable
  via API or Excel). No numeric constants live in solver or constraint code.
- **Two-phase solver** (`app/solver/`):
  - *Phase 1*: most-constrained-first greedy construction + tabu/min-conflicts
    ejection repair; hard gate at 0 violations.
  - *Phase 2*: hyper-heuristic move selection (single swap, Kempe chain,
    ruin-and-recreate, day shift) with Late Acceptance Hill Climbing
    (Simulated Annealing pluggable via config). No accepted move may
    reintroduce a hard violation.
- **Excel round trip**: one import workbook (one sheet per entity, row-level
  validation errors, natural-key upsert re-import) and one export workbook
  (master Day×Slot×Room grid, per-teacher and per-group sheets, feasibility
  report, soft-penalty breakdown by tier).
- **Manual edit workflow**: edit the exported `MasterTimetable` sheet, re-upload
  to `/api/v1/import/edits`; each edit is re-validated against all hard
  constraints, invalid rows rejected individually, soft report recomputed.
- **Reproducibility**: every run logs seed, iteration counts, runtime, and full
  weight/config snapshots to `solver_runs`.

## Web UI

Served by the API itself (no separate frontend build):

- **`/` — Workbench**: guided 3-step flow (get data in → solve → results) with
  a how-it-works guide, template download, one-click demo data, live solver
  status, recent-runs ledger, and a plain-language FAQ on hard/soft
  constraints and manual editing.
- **`/timetable` — Routine viewer**: master Day × Slot × Room grid with day
  tabs, plus per-teacher and per-class-group personal week views; badges show
  clash count (always 0 for a completed run), quality penalty, and weekly
  class count.
- SEO-ready: semantic HTML, meta description/OpenGraph/Twitter tags, JSON-LD
  `SoftwareApplication` schema, `robots.txt` and `sitemap.xml`.

## Quick start (Docker / API-only)

```bash
# with Docker (Postgres + API)
docker compose up --build
# open http://localhost:8000  (UI)  or  http://localhost:8000/docs  (API)

# or locally (SQLite by default)
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

API flow (everything the UI does is plain `/api/v1` calls):

1. `GET /api/v1/import/template` — blank workbook, or `POST /api/v1/import/demo`
   for the built-in sample dataset
2. `POST /api/v1/import` — upload the filled workbook
3. `POST /api/v1/solve` — returns a `job_id`; poll `GET /api/v1/solve/{job_id}/status`
   (recent runs: `GET /api/v1/solve/runs`)
4. `GET /api/v1/timetable/{job_id}` (JSON) or
   `GET /api/v1/timetable/{job_id}/export?format=xlsx|csv|ics|pdf`

Other endpoints: `GET/PATCH /api/v1/config/weights`, `GET/PATCH
/api/v1/config/system`, `GET /api/v1/teacher/{id}/schedule`,
`GET /api/v1/group/{id}/schedule`, `PATCH /api/v1/session/{id}` (manual
override, hard-constraint validated, optional lock/pin), `POST
/api/v1/import/edits` (hand-edited MasterTimetable re-import).

All errors are structured JSON: `{"error": {"code", "message", "details"}}`.

## Tests

```bash
pytest -m "not scale"     # unit + integration (~20s)
pytest -m scale -s        # 500-course / 2,400-session Phase 1 profile run
```

The suite covers every hard and soft constraint in isolation with synthetic
conflict cases, Phase 1 feasibility, the Phase 2 hard invariant, Excel
import/export/manual-edit round trips, and the full API flow.

Current scale result: 500 courses / 2,400 sessions reach feasibility in ~35s
(greedy construction alone, zero repair iterations). Construction is the known
bottleneck at scale, as predicted; the next optimisation lever is caching
feasible-placement scans during ordering.

## Layout

```
app/
  models/            SQLAlchemy models (design doc section 3)
  schemas/           Pydantic request/response schemas
  api/v1/            FastAPI routers (import, solve, timetable, schedules, sessions, config)
  solver/
    domain.py        pure in-memory Problem/Timetable (constraint unit tests need no DB)
    phase1_construction.py / phase2_refinement.py / acceptance.py / engine.py
    constraints/hard/  one class per hard constraint (H01..H14)
    constraints/soft/  one class per soft constraint (S01..S19)
    constraints/registry.py  the single registration point
    moves/           swap, kempe_chain, ruin_recreate, day_shift
  excel/             import, export, manual-edit re-import, sample data
  config/            ConstraintWeight/SystemConfig defaults + seeding
  migrations/        Alembic (initial schema included)
tests/
```

Background solves use FastAPI `BackgroundTasks`; the documented upgrade path
for long runs is Celery + Redis (a commented-out service stub is in
`docker-compose.yml`).
