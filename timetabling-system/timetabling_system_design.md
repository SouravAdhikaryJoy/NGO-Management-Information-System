# University Timetabling System — Design Document

This document is the source of truth for constraints, data model, algorithm and
output specification. The implementation must follow it field-for-field.

## 1. Overview

The system produces a weekly class routine for a university: every required
class *session* (a single meeting of a course for a class group, taught by a
teacher) is assigned a **timeslot** (day + period) and a **room**, such that all
**hard constraints** hold (feasibility) and the weighted sum of **soft
constraint** penalties is minimised (quality).

Data flows in and out through Excel workbooks; a REST API wraps import, solve,
export, and manual-override operations.

Scheduling unit: a `Session` row. Sessions are derived from curriculum data:
for every `ClassGroup` and every `Course` the group is enrolled in (a group is
enrolled in all courses that share its `department` + `semester`), one session
is generated per `CourseSessionType.sessions_per_week`, with the session type's
`duration_slots` and `required_room_type`. Each session carries the teacher
assigned to that course/group (explicit `teacher_code` on the course, otherwise
auto-assigned from `TeacherCoursePreference`, highest preference first,
balancing weekly load).

A multi-slot session (`duration_slots > 1`) occupies consecutive slot indexes
on the same day in the same room.

## 2. Constraints

Every constraint is identified by a stable `key`. The `ConstraintWeight` table
drives `tier`, `weight`, `is_hard` and `enabled` per key at runtime; the values
below are the seeded defaults.

### 2.1 Hard constraints (14) — must all hold in any published timetable

| Key | Rule |
|---|---|
| `H01_room_occupancy` | No two sessions may occupy the same room in the same timeslot (any overlapping occupied slot). |
| `H02_teacher_clash` | A teacher cannot teach two sessions in overlapping timeslots. |
| `H03_group_clash` | A class group cannot attend two sessions in overlapping timeslots. |
| `H04_room_capacity` | Room capacity must be ≥ the class group size. |
| `H05_room_type_match` | The room's type must equal the session's `required_room_type` (e.g. LAB sessions in LAB rooms). |
| `H06_teacher_availability` | A session may not be placed in any slot the teacher marked UNAVAILABLE. |
| `H07_teacher_qualification` | The session's teacher must be qualified for the course: an explicit course `teacher_code`, or a `TeacherCoursePreference` row for that course. |
| `H08_session_completeness` | Every generated session must be placed — no course meeting may be dropped. |
| `H09_slot_validity` | A session's start slot must be an existing, non-break timeslot. |
| `H10_multislot_contiguity` | A multi-slot session must occupy contiguous slot indexes on one day, all existing and non-break, entirely within the day. |
| `H11_teacher_max_daily` | A teacher may not exceed their `max_sessions_per_day` (occupied slots counted). |
| `H12_group_max_daily` | A class group may not exceed `group_max_sessions_per_day` (SystemConfig) occupied slots per day. |
| `H13_course_once_per_day` | The same course may meet at most once per day for a given class group (a multi-slot session counts once). |
| `H14_locked_session` | A locked (pinned) session must remain at exactly its locked day/slot/room. |
| `H15_slot_type_scope` | A session may only occupy `TimeSlot`s whose `session_type_scope` (if set) includes its `session_type` — implements fixed, separate timeslot pools for lab vs. theory classes. |

### 2.2 Soft constraints (19) — weighted penalties, lower is better

Tier 1 = critical quality, Tier 2 = important, Tier 3 = nice-to-have.

| Key | Tier | Default weight | Penalty (raw units, multiplied by weight) |
|---|---|---|---|
| `S01_teacher_preferred_slots` | 1 | 8 | 1 per occupied slot outside the teacher's PREFERRED set (only for teachers who declared any preferred slot). |
| `S02_teacher_course_preference` | 1 | 8 | `(5 − preference)` per session where the assigned teacher's preference for the course is < 5 (missing preference for explicitly assigned teachers counts as 3). |
| `S03_group_gaps` | 1 | 10 | 1 per idle slot between a group's first and last busy slot of a day. |
| `S04_teacher_gaps` | 2 | 5 | 1 per idle slot between a teacher's first and last busy slot of a day. |
| `S05_group_compact_days` | 2 | 4 | 1 per active day beyond the minimum days needed (`ceil(busy_slots / group_max_sessions_per_day)`). |
| `S06_teacher_compact_days` | 2 | 4 | Same measure applied to teachers (vs `max_sessions_per_day`). |
| `S07_course_spread` | 1 | 6 | 1 per pair of same course+group sessions on adjacent days (sessions of one course should spread across the week). |
| `S08_group_max_consecutive` | 1 | 7 | 1 per occupied slot beyond `max_consecutive_group` in any consecutive run of a group's day. |
| `S09_teacher_max_consecutive` | 1 | 7 | Same for teachers vs `max_consecutive_teacher`. |
| `S10_early_slot_avoidance` | 3 | 2 | 1 per session whose occupied slots include the first slot index of a day. |
| `S11_late_slot_avoidance` | 3 | 2 | 1 per session whose occupied slots include the last slot index of a day. |
| `S12_lunch_break` | 2 | 5 | 1 per group-day where every slot in the lunch window (`lunch_start_slot`..`lunch_end_slot`) is occupied. |
| `S13_room_stability` | 3 | 3 | Per group: distinct rooms used − 1. |
| `S14_building_travel` | 2 | 6 | 1 per pair of back-to-back sessions of one group in different buildings. |
| `S15_room_utilization_fit` | 3 | 2 | 1 per session where `room.capacity / group.size` > `room_fit_slack_threshold`. |
| `S16_teacher_load_balance` | 2 | 4 | Per teacher: `max_daily_count − min_daily_count` over active days, when active on ≥ 2 days. |
| `S17_group_load_balance` | 2 | 4 | Same measure for groups. |
| `S18_difficult_course_morning` | 2 | 5 | 1 per session of a course flagged `is_difficult` whose start slot index > `morning_end_slot`. |
| `S19_teacher_back_to_back` | 3 | 3 | For teachers with a declared `prefers_back_to_back`: if `False`, 1 per adjacent pair of their sessions; if `True`, 1 per isolated session on a day where they teach ≥ 2 sessions. |

## 3. Data model

Natural keys (used for Excel upsert) are marked **NK**. All entities get a
surrogate integer `id` primary key plus `created_at`/`updated_at`.

- **University** — `code` **NK**, `name`
- **Department** — `code` **NK**, `name`, `university_code` → University
- **Building** — `code` **NK**, `name`, `university_code` → University
- **RoomType** — `code` **NK** (e.g. LECTURE, LAB, SEMINAR), `name`
- **Room** — `code` **NK**, `name`, `building_code` → Building,
  `room_type_code` → RoomType, `capacity` (int > 0)
- **TimeSlot** — **NK** (`day_of_week`, `slot_index`); `day_of_week` in
  MON..SUN, `slot_index` ≥ 1 consecutive within a day, `start_time`,
  `end_time`, `is_break` (bool), `session_type_scope` (optional comma list of
  LECTURE|LAB|TUTORIAL; blank/null = any type may use the slot — see H15)
- **Course** — `code` **NK**, `title`, `department_code` → Department,
  `semester` (int), `credit_hours` (float), `is_difficult` (bool, default
  false), `teacher_code` (optional → Teacher; explicit assignment)
- **CourseSessionType** — **NK** (`course_code`, `session_type`);
  `session_type` in LECTURE|LAB|TUTORIAL, `sessions_per_week` (int ≥ 1),
  `duration_slots` (int ≥ 1), `required_room_type_code` → RoomType
- **ClassGroup** — `code` **NK**, `name`, `department_code` → Department,
  `semester` (int), `size` (int > 0)
- **Teacher** — `code` **NK**, `name`, `department_code` → Department,
  `max_sessions_per_day` (int ≥ 1), `max_sessions_per_week` (int ≥ 1),
  `employment_type` (FULL_TIME|PART_TIME|ADJUNCT),
  `prefers_back_to_back` (optional bool)
- **TeacherAvailability** — **NK** (`teacher_code`, `day_of_week`,
  `slot_index`); `availability` in UNAVAILABLE|AVAILABLE|PREFERRED. Missing
  rows mean AVAILABLE.
- **TeacherCoursePreference** — **NK** (`teacher_code`, `course_code`);
  `preference` int 1..5 (5 = most preferred). A row also asserts
  qualification (H07).
- **ConstraintWeight** — `constraint_key` **NK**, `tier` (1..3), `weight`
  (float ≥ 0), `is_hard` (bool), `enabled` (bool)
- **SystemConfig** — `key` **NK**, `value` (string), `value_type`
  (int|float|str|bool), `description`
- **Session** (derived, not imported) — `course_id`, `class_group_id`,
  `teacher_id`, `session_type`, `duration_slots`, `required_room_type_id`,
  `sequence_no` (1..sessions_per_week), assignment fields `day_of_week`,
  `slot_index`, `room_id` (null until solved), `is_locked` (bool) and locked
  copies of the pin (`locked_day`, `locked_slot_index`, `locked_room_id`)
- **SolverRun** — `job_id` (uuid **NK**), `status`
  (PENDING|RUNNING|PHASE1_FAILED|COMPLETED|FAILED), `seed`,
  `phase1_iterations`, `phase2_iterations`, `runtime_seconds`,
  `hard_violations`, `soft_penalty`, `weights_snapshot` (JSON),
  `config_snapshot` (JSON), `error`, timestamps
- **User** — `username` **NK**, `password_hash`, `is_admin` (bool). Accounts
  gate every *write* operation (import, solve, manual edits, config changes,
  course/teacher reassignment); all read/view endpoints stay public with no
  account needed.

## 3.1 Display convention: course.section

A session's course code and **section** (the 1-based rank, alphabetical by
class-group code, of its class group among all groups taking that course)
are combined as `CODE.section`, e.g. `CSE123.3`. Cell labels in the routine
follow the row's fixed context so nothing is repeated redundantly:

| View (row is…) | Cell label |
|---|---|
| Room (MasterTimetable) | `CODE.section (TeacherCode)` |
| Individual teacher | `CODE.section (RoomCode)` |
| Class group | `CODE.section (TeacherCode) (RoomCode)` |

## 4. Solving algorithm — two phases

### Phase 1 — feasibility (0 hard violations, gate to Phase 2)

1. **Ordering** — Brélaz-style most-constrained-first: locked sessions first,
   then descending `duration_slots`, ascending count of feasible
   (timeslot, room) placements, descending group size.
2. **Greedy construction** — place each session at the first feasible
   placement (checked against all 14 hard constraints); leave unplaceable
   sessions pending.
3. **Repair** — Tabu-search / min-conflicts ejection: repeatedly take a
   pending session, choose the placement with the fewest conflicting placed
   sessions that is not tabu, eject the conflicters back to pending, mark the
   (session, day, slot) move tabu for `phase1_tabu_tenure` iterations. Stop at
   0 pending or `phase1_max_repair_iterations`.
4. **Gate** — Phase 2 runs only when `H08` reports 0 (everything placed) and
   all incremental hard checks pass; otherwise the run status is
   `PHASE1_FAILED` with diagnostics.

### Phase 2 — quality (soft-penalty minimisation)

- **Objective**: Σ over enabled soft constraints of `weight × raw_penalty`,
  weights read from `ConstraintWeight` at run start (never hardcoded).
- **Move set**: `single_swap` (swap or relocate one/two sessions),
  `kempe_chain` (conflict-chain exchange between two timeslot columns),
  `ruin_recreate` (remove `ruin_fraction` of sessions, greedy re-insert at
  best-penalty feasible placements), `day_shift` (move one session to another
  day).
- **Hyper-heuristic selection**: per move type, track recent success rate
  (accepted moves / attempts over a sliding window); select move types
  weighted-random by smoothed success.
- **Acceptance**: Late Acceptance Hill Climbing (LAHC) with history length
  `lahc_history_length`; the acceptance criterion is pluggable (Simulated
  Annealing provided as an alternative, selected by `acceptance_method`).
- **Invariant**: a candidate move is validated against all hard constraints
  before evaluation; any move that would reintroduce a hard violation is
  rejected outright.
- **Stopping**: whichever of `phase2_time_budget_seconds` /
  `phase2_iteration_budget` is hit first.
- **Finisher**: the last `phase2_finisher_fraction` share of the budget
  switches acceptance to strict improve-only (candidate must beat the current
  cost), squeezing out the easy residual penalty LAHC/SA's looser acceptance
  criterion leaves behind. Same move set, same hard-invariant check.
- **Bookkeeping note**: `Timetable`'s per-slot occupancy indexes
  (`room_busy`/`teacher_busy`/`group_busy` and the derived
  `group_slots`/`teacher_slots`) are reference-counted, not single-valued.
  Move evaluation routinely places a candidate session onto a slot another
  session still legitimately holds (that overlap is exactly what hard-check
  is meant to catch) before rejecting and undoing it; a single-value/plain-set
  index would let that second occupant silently clobber the first one's
  bookkeeping on removal, permanently corrupting the soft-penalty count from
  then on even though `.placements` itself stayed correct.

Every run logs seed, iteration counts, runtime, and full weight/config
snapshots to `SolverRun` for reproducibility.

## 5. Output specification (Excel workbook)

- `MasterTimetable` — one grid per day: rows = rooms, columns = slot indexes,
  cell = `COURSE (TYPE) / GROUP / TEACHER`. Multi-slot sessions repeat across
  their occupied columns.
- One sheet per teacher (`T_<code>`) and one per class group (`G_<code>`):
  rows = days, columns = slots, cell = course/room details.
- `FeasibilityReport` — one row per hard constraint: key, description,
  violation count. A publishable routine must show 0 for every row.
- `SoftConstraintScoreReport` — one row per soft constraint: key, tier,
  weight, raw penalty, weighted penalty; subtotals per tier and grand total.

## 6. Default configuration

Constraint weights: as listed in section 2.2 (all `enabled`, hard rows
`is_hard=true`, `weight=0`, `tier=0`).

SystemConfig defaults:

| key | type | default | meaning |
|---|---|---|---|
| `group_max_sessions_per_day` | int | 6 | H12 cap |
| `max_consecutive_group` | int | 3 | S08 threshold |
| `max_consecutive_teacher` | int | 3 | S09 threshold |
| `lunch_start_slot` | int | 4 | S12 window start (slot index) |
| `lunch_end_slot` | int | 5 | S12 window end |
| `morning_end_slot` | int | 3 | S18: last "morning" slot index |
| `room_fit_slack_threshold` | float | 2.0 | S15 capacity/size ratio |
| `phase1_max_repair_iterations` | int | 20000 | repair budget |
| `phase1_tabu_tenure` | int | 25 | tabu tenure |
| `phase2_time_budget_seconds` | float | 60 | Phase 2 wall clock budget |
| `phase2_iteration_budget` | int | 200000 | Phase 2 iteration budget |
| `phase2_finisher_fraction` | float | 0.15 | share of the Phase 2 budget reserved for a strict improve-only descent pass at the end |
| `lahc_history_length` | int | 500 | LAHC list length |
| `acceptance_method` | str | lahc | `lahc` or `simulated_annealing` |
| `sa_initial_temp` | float | 10.0 | SA start temperature |
| `sa_cooling` | float | 0.999 | SA geometric cooling factor |
| `ruin_fraction` | float | 0.1 | share of sessions removed by ruin_recreate |
| `hyper_heuristic_window` | int | 100 | success-rate sliding window |
| `random_seed` | int | 42 | solver RNG seed (logged per run) |

## 7. Manual edit re-import

Admins may edit the exported `MasterTimetable` sheet (move a session's
day/slot/room, or change the teacher code in the cell). On re-import each
edited session is re-validated against all 14 hard constraints **in the
context of the otherwise-unchanged timetable**; a violating edit is rejected
row-by-row (constraint key + reason reported) while valid edits are applied,
after which the soft-penalty report is recomputed (no full re-solve).

## 8. API surface

Versioned under `/api/v1` exactly as listed in the build instructions; all
errors are structured JSON: `{"error": {"code": ..., "message": ...,
"details": [...]}}`.
