# University Timetabling System

Automated weekly class-routine generation for a university: Excel in, solved
routine out, with a two-phase metaheuristic solver (feasibility, then quality)
behind a versioned FastAPI — plus a built-in web UI that walks you through the
whole workflow, with login-gated editing and public read-only viewing.

## Try it in 60 seconds

```bash
pip install -r requirements.txt
uvicorn app.main:app
```

Open **http://localhost:8000** and:

1. Press **"Try it now with demo data"** — you'll be asked to log in
   (`admin` / `admin123` by default, see [Accounts](#accounts) below), then it
   loads a built-in sample university (10 courses, 8 teachers, 4 class groups).
2. Press **"Run the solver"** — live status updates; a demo-sized dataset
   solves in seconds to a minute.
3. Press **"Open timetable view"** — browse the routine by room, teacher,
   class group, semester or department; download it as Excel, CSV, calendar
   (.ics) or PDF. No login needed just to look.

For real data: download the blank Excel template from the same page, fill one
sheet per entity, and upload it. Every row is validated first — errors are
reported with the exact sheet, row and field, and nothing is half-imported.

The full specification lives in [`timetabling_system_design.md`](timetabling_system_design.md)
— constraints, data model, algorithm, and output spec. The implementation
follows it field-for-field.

## Accounts

Viewing the routine (any page, any export) never needs an account. Anything
that *changes* data — import, demo load, solve, manual edits, drag-and-drop,
reassigning a teacher, editing config — requires a login.

A default admin account is seeded on first startup: username `admin`,
password `admin123`, **unless** you set `ADMIN_USERNAME` / `ADMIN_PASSWORD`
env vars before the first run (a startup log warning reminds you if you
didn't). Sessions are signed cookies; set `SESSION_SECRET` in any real
deployment so logins survive a restart.

## Highlights

- **15 hard constraints + 19 soft constraints**, each its own class behind a
  shared interface, registered in
  `app/solver/constraints/registry.py`. Adding a constraint = one new class
  file + one registration line; no solver changes. (H15 is the newest: fixed,
  separate timeslot pools for lab vs. theory classes, via
  `TimeSlot.session_type_scope`.)
- **Runtime-configurable**: every weight, tier, and threshold comes from the
  `ConstraintWeight` / `SystemConfig` tables (seeded with defaults, editable
  via API, Excel, or the Manage page). No numeric constants live in solver or
  constraint code.
- **Two-phase solver** (`app/solver/`):
  - *Phase 1*: most-constrained-first greedy construction + tabu/min-conflicts
    ejection repair; hard gate at 0 violations.
  - *Phase 2*: hyper-heuristic move selection (single swap, Kempe chain,
    ruin-and-recreate, day shift) with Late Acceptance Hill Climbing
    (Simulated Annealing pluggable via config), finishing with a bounded
    strict-improve-only descent pass (`phase2_finisher_fraction`) to squeeze
    out easy residual penalty. No accepted move may reintroduce a hard
    violation — occupancy bookkeeping is reference-counted specifically so a
    rejected/undone overlapping move can never corrupt an unrelated
    session's slot record.
- **Display convention**: every cell is `CODE.section` (e.g. `CSE123.3`,
  section = the class group's rank among groups taking that course), with the
  teacher/room named only where the row doesn't already fix it — see design
  doc §3.1.
- **Excel round trip**: one import workbook (one sheet per entity, row-level
  validation errors, natural-key upsert re-import) and one export workbook
  (Summary sheet, master Day×Slot×Room grid, per-teacher and per-group
  sheets, feasibility report, soft-penalty breakdown by tier).
- **Manual edit workflow**: edit the exported `MasterTimetable` sheet, re-upload
  to `/api/v1/import/edits` (admin login required); each edit is re-validated
  against all hard constraints, invalid rows rejected individually, soft
  report recomputed.
- **Reproducibility**: every run logs seed, iteration counts, runtime, and full
  weight/config snapshots to `solver_runs`; every completed run exposes a
  `summary` (sessions placed, hard violations, soft penalty by tier, how many
  of the 19 soft constraints still carry any penalty).

## Web UI

Served by the API itself (no separate frontend build):

- **`/` — Workbench**: guided 3-step flow (get data in → solve → results) with
  a how-it-works guide, template download, one-click demo data, live solver
  status, recent-runs ledger, and a plain-language FAQ on hard/soft
  constraints and manual editing. Import/solve buttons prompt for login if
  you're not signed in.
- **`/timetable` — Routine viewer**: master Day × Slot × Room grid with day
  tabs, plus **room / teacher / class group / semester / department** views;
  badges show clash count, quality penalty, and weekly class count. Any hard
  violation is called out in a banner and the specific cells are outlined in
  red with a reason tag (e.g. "⚠ TEACHER DOUBLE-BOOKED") — this fires for real
  if an edit creates a clash, not just as a static label. When logged in,
  click any class to open an edit drawer (day/slot/room/teacher/lock,
  validated against every hard constraint with readable errors), or
  drag-and-drop a class onto an empty cell in the room view for a quick
  same-day move.
- **`/manage` — Course & teacher catalog**: everyone can see course
  offerings (with section breakdown) and teacher loads; logging in enables
  reassigning a course's teacher or editing a teacher's daily/weekly caps.
  Either change is checked against the live routine and reports any new
  clash immediately.
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

API flow (everything the UI does is plain `/api/v1` calls; POST/PATCH need a
logged-in session cookie, GET never does):

1. `GET /api/v1/import/template` — blank workbook, or `POST /api/v1/import/demo`
   for the built-in sample dataset
2. `POST /api/v1/import` — upload the filled workbook
3. `POST /api/v1/solve` — returns a `job_id`; poll `GET /api/v1/solve/{job_id}/status`
   (recent runs: `GET /api/v1/solve/runs`)
4. `GET /api/v1/timetable/{job_id}` (JSON, includes a `summary` block) or
   `GET /api/v1/timetable/{job_id}/export?format=xlsx|csv|ics|pdf`

Other endpoints: `POST /api/v1/auth/login|logout`, `GET /api/v1/auth/me`,
`GET/PATCH /api/v1/config/weights`, `GET/PATCH /api/v1/config/system`,
`GET /api/v1/courses|teachers|rooms|class-groups` (public lists),
`PATCH /api/v1/course/{id}` / `PATCH /api/v1/teacher/{id}` (admin, reports any
new hard violations the change causes), `GET /api/v1/teacher/{id}/schedule`,
`GET /api/v1/group/{id}/schedule`, `PATCH /api/v1/session/{id}` (manual
override, hard-constraint validated, optional lock/pin), `POST
/api/v1/import/edits` (hand-edited MasterTimetable re-import).

All errors are structured JSON: `{"error": {"code", "message", "details"}}`.

## Tests

```bash
pytest -m "not scale"     # unit + integration (~35s, 74 tests)
pytest -m scale -s        # 500-course profile run + the 60-teacher stress demo
```

The suite covers every hard and soft constraint in isolation with synthetic
conflict cases, Phase 1 feasibility, the Phase 2 hard invariant (including a
regression test for the occupancy reference-counting fix), Excel
import/export/manual-edit round trips, auth gating, catalog cascade
warnings, and the full API/UI flow.

### Scale results

- **500 courses / 2,400 sessions**: Phase 1 reaches feasibility in ~35–46s
  (greedy construction alone, zero repair iterations needed).
- **60-teacher stress demo** (`scripts/run_stress_demo.py` —
  `tests/test_stress_demo.py` is the permanent regression form): 240 theory +
  120 lab sessions/week, 40 teachers with a Friday–Saturday weekend and 20
  with Thursday–Friday, fixed separate timeslot pools for labs vs. theory
  (H15), run at the **minimal room count a search found still feasible** (7
  theory rooms, 10 lab rooms — a few rooms below the naive slot-capacity
  lower bound of 6/9, since teacher-availability and daily-cap constraints
  eat into the naive bound).

  **Result: 0 hard violations, every one of the 360 sessions placed.** Phase 2
  cuts soft penalty ~57–58% (7608 → ~3200) in two minutes. Run it yourself:
  `python scripts/run_stress_demo.py` (searches room counts, then does a full
  solve and prints the complete report — takes a few minutes).

  **Soft penalty does not reach zero, and at this room count it plateaus
  quickly** — a 5× longer Phase 2 budget (120s → 300s) only shaved off
  another ~2%. That's not a solver-quality gap: the dominant remaining terms
  (`S13_room_stability`, `S05`/`S06_compact_days`, `S16`/`S17_load_balance`)
  are a direct, structural consequence of the room count being deliberately
  the *minimum feasible* — with almost no spare room-slot capacity, a group's
  sessions are forced into whatever rooms happen to be free, scattered across
  more of the week than a slack-rich schedule would need. **Verified**: giving
  the same problem a modest buffer (+2 theory, +2 lab rooms — about 20% more
  supply) drops the same-budget soft penalty a further ~38% (3275 → 2033) and
  makes Phase 1 solve almost instantly. If a real deployment lands at a
  similarly tight room count and wants a materially better routine, the most
  effective lever is a small room-capacity buffer, not a bigger time budget or
  different weights — the two are complementary (more time still helps once
  there's slack to search).

## Layout

```
app/
  models/            SQLAlchemy models (design doc section 3) + auth.User
  schemas/           Pydantic request/response schemas
  api/v1/            FastAPI routers (auth, catalog, import, solve, timetable, schedules, sessions, config)
  labels.py           course.section computation shared by the API and Excel export
  security.py         password hashing + signed session cookies + require_admin
  solver/
    domain.py        pure in-memory Problem/Timetable (constraint unit tests need no DB)
    phase1_construction.py / phase2_refinement.py / acceptance.py / engine.py
    constraints/hard/  one class per hard constraint (H01..H15)
    constraints/soft/  one class per soft constraint (S01..S19)
    constraints/registry.py  the single registration point + build_summary()
    moves/           swap, kempe_chain, ruin_recreate, day_shift
  excel/             import, export, manual-edit re-import, sample + stress-demo data generators
  config/            ConstraintWeight/SystemConfig defaults + seeding (incl. default admin)
  web/               server-rendered pages (/, /timetable, /manage) + static JS/CSS
  migrations/        Alembic (initial schema + auth/H15 migration included)
tests/
scripts/run_stress_demo.py   60-teacher room-count search + full solve report
```

Background solves use FastAPI `BackgroundTasks`; the documented upgrade path
for long runs is Celery + Redis (a commented-out service stub is in
`docker-compose.yml`).
