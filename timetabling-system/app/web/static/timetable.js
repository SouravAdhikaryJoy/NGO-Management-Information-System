/* Timetable viewer: day tabs + room/teacher/group/semester/department views,
 * conflict detection, and (when logged in) click-to-edit + drag-to-move. */

const $ = (id) => document.getElementById(id);
const DAY_ORDER = ["SAT", "SUN", "MON", "TUE", "WED", "THU", "FRI"];
const DAY_NAMES = { SAT: "Saturday", SUN: "Sunday", MON: "Monday", TUE: "Tuesday",
                    WED: "Wednesday", THU: "Thursday", FRI: "Friday" };
const CONSTRAINT_HINTS = {
  H01_room_occupancy: "the room is already in use at that time",
  H02_teacher_clash: "the teacher already has a class at that time",
  H03_group_clash: "the class group already has a class at that time",
  H04_room_capacity: "the room is too small for this class group",
  H05_room_type_match: "the room type doesn't match this session (lecture/lab)",
  H06_teacher_availability: "the teacher marked that time unavailable",
  H07_teacher_qualification: "this teacher isn't qualified for the course",
  H09_slot_validity: "that isn't a valid, non-break timeslot",
  H10_multislot_contiguity: "the session needs contiguous slots that fit in the day",
  H11_teacher_max_daily: "the teacher would exceed their daily class limit",
  H12_group_max_daily: "the group would exceed its daily class limit",
  H13_course_once_per_day: "this course already meets once that day for this group",
  H14_locked_session: "this session is locked to its current slot",
  H15_slot_type_scope: "that timeslot isn't designated for this session type (lab/theory)",
};

let data = null;          // /api/v1/timetable/{id} payload
let classGroups = [];     // /api/v1/class-groups
let roomList = [];        // /api/v1/rooms
let teacherList = [];     // /api/v1/teachers
let conflicts = new Map();// session_id -> Set(reason)
let activeDay = null;
let viewMode = "all";
let entity = null;

async function fetchJson(path) {
  const response = await fetch(path);
  if (!response.ok) return null;
  return response.json();
}

function scheduled() {
  return data.sessions.filter((s) => s.day_of_week && s.slot_index && s.room_code);
}

function days() {
  const present = new Set(scheduled().map((s) => s.day_of_week));
  return DAY_ORDER.filter((d) => present.has(d));
}

function slotIndexes() {
  let max = 0;
  for (const s of scheduled()) {
    max = Math.max(max, s.slot_index + s.duration_slots - 1);
  }
  return Array.from({ length: max }, (_, i) => i + 1);
}

/* ---- conflict detection (mirrors H01/H02/H03; should always be empty on a
   freshly solved routine — this is the safety net for edited/legacy data
   and the live preview while dragging) --------------------------------- */

function computeConflicts(sessions) {
  const byRoom = new Map(), byTeacher = new Map(), byGroup = new Map();
  const found = new Map();
  const bump = (map, key, sid) => { if (!map.has(key)) map.set(key, []); map.get(key).push(sid); };
  for (const s of sessions.filter((s) => s.day_of_week && s.slot_index)) {
    for (let i = 0; i < s.duration_slots; i += 1) {
      const idx = s.slot_index + i;
      if (s.room_id) bump(byRoom, `${s.room_id}|${s.day_of_week}|${idx}`, s.id);
      bump(byTeacher, `${s.teacher_id}|${s.day_of_week}|${idx}`, s.id);
      bump(byGroup, `${s.class_group_id}|${s.day_of_week}|${idx}`, s.id);
    }
  }
  const mark = (map, reason) => {
    for (const ids of map.values()) {
      if (ids.length > 1) {
        for (const id of ids) {
          if (!found.has(id)) found.set(id, new Set());
          found.get(id).add(reason);
        }
      }
    }
  };
  mark(byRoom, "Room double-booked");
  mark(byTeacher, "Teacher double-booked");
  mark(byGroup, "Group double-booked");
  return found;
}

function renderConflictBanner() {
  const el = $("conflict-banner");
  const hard = (data.feasibility_report || []).filter((r) => r.violations > 0);
  if (!hard.length) { el.innerHTML = ""; return; }
  const items = hard.map((r) => `<li><strong>${r.key}</strong>: ${r.description} — ${r.violations} case(s)</li>`).join("");
  el.innerHTML = `<div class="conflict-banner"><span class="mark">⚠</span>
    <div><strong>${hard.reduce((n, r) => n + r.violations, 0)} conflict(s) found in this routine.</strong>
    Cells involved are outlined in red below.<ul>${items}</ul></div></div>`;
}

/* ---- cell rendering ---------------------------------------------------- */

function lessonHtml(s, labelField) {
  const type = s.session_type.toLowerCase();
  const reasons = conflicts.get(s.id);
  const editable = Auth.isAuthenticated();
  const cls = ["lesson", type];
  if (reasons) cls.push("conflict");
  if (editable) cls.push("editable");
  const tag = reasons ? `<span class="clash-tag">⚠ ${[...reasons].join(", ")}</span>` : "";
  return `<div class="${cls.join(" ")}" data-session-id="${s.id}"
    title="${s.course_title}" ${editable ? 'draggable="true"' : ""}>
    ${s[labelField]}${tag}</div>`;
}

function renderGrid() {
  const bySlot = new Map();
  const rooms = new Set();
  for (const s of scheduled()) {
    if (s.day_of_week !== activeDay) continue;
    rooms.add(s.room_code);
    for (let i = 0; i < s.duration_slots; i += 1) {
      bySlot.set(`${s.room_code}|${s.slot_index + i}`, s);
    }
  }
  const roomCodes = [...rooms].sort();
  const slots = slotIndexes();
  const times = new Map();
  for (const s of scheduled()) if (s.start_time) times.set(s.slot_index, s.start_time);

  const head = `<tr><th class="roomcol">Room</th>` +
    slots.map((i) => `<th>Slot ${i}${times.has(i) ? `<br>${times.get(i)}` : ""}</th>`).join("") +
    `</tr>`;
  const body = roomCodes.map((room) => {
    const cells = [];
    for (let i = 0; i < slots.length;) {
      const s = bySlot.get(`${room}|${slots[i]}`);
      if (s && s.slot_index === slots[i]) {
        cells.push(`<td colspan="${s.duration_slots}" data-room="${room}" data-slot="${slots[i]}">` +
          lessonHtml(s, "label_room_view") + `</td>`);
        i += s.duration_slots;
      } else if (s) {
        i += 1;
      } else {
        cells.push(`<td data-room="${room}" data-slot="${slots[i]}"></td>`);
        i += 1;
      }
    }
    return `<tr><th class="roomcol">${room}</th>${cells.join("")}</tr>`;
  }).join("");

  return `<div class="sheet"><table class="grid">
    <caption>${DAY_NAMES[activeDay]} — every room, every slot.
      Coloured edge: lecture (green), lab (sienna), tutorial (gold).
      ${Auth.isAuthenticated() ? "Drag a class onto an empty cell, or click it to edit." : ""}</caption>
    <thead>${head}</thead><tbody>${body}</tbody></table></div>`;
}

function renderPersonal(labelField, filterFn, captionLabel) {
  const mine = scheduled().filter(filterFn);
  const slots = slotIndexes();
  const head = `<tr><th class="roomcol">Day</th>` + slots.map((i) => `<th>Slot ${i}</th>`).join("") + `</tr>`;
  const body = days().map((day) => {
    const bySlot = new Map();
    for (const s of mine) { if (s.day_of_week === day) bySlot.set(s.slot_index, s); }
    const cells = [];
    for (let i = 0; i < slots.length;) {
      const s = bySlot.get(slots[i]);
      if (s) {
        cells.push(`<td colspan="${s.duration_slots}">${lessonHtml(s, labelField)}</td>`);
        i += s.duration_slots;
      } else {
        cells.push("<td></td>");
        i += 1;
      }
    }
    return `<tr><th class="roomcol">${DAY_NAMES[day]}</th>${cells.join("")}</tr>`;
  }).join("");
  return `<div class="sheet"><table class="grid">
    <caption>${captionLabel}</caption><thead>${head}</thead><tbody>${body}</tbody></table></div>`;
}

function renderCohort(groupCodes, captionLabel) {
  const slots = slotIndexes();
  const head = `<tr><th class="roomcol">Group</th>` + slots.map((i) => `<th>Slot ${i}</th>`).join("") + `</tr>`;
  const rows = groupCodes.map((code) => {
    const mine = scheduled().filter((s) => s.class_group_code === code && s.day_of_week === activeDay);
    const bySlot = new Map();
    for (const s of mine) bySlot.set(s.slot_index, s);
    const cells = [];
    for (let i = 0; i < slots.length;) {
      const s = bySlot.get(slots[i]);
      if (s) {
        cells.push(`<td colspan="${s.duration_slots}">${lessonHtml(s, "label_group_view")}</td>`);
        i += s.duration_slots;
      } else {
        cells.push("<td></td>");
        i += 1;
      }
    }
    return `<tr><th class="roomcol">${code}</th>${cells.join("")}</tr>`;
  }).join("");
  const tabs = days().map((d) =>
    `<button class="daytab ${d === activeDay ? "active" : ""}" data-day="${d}">${DAY_NAMES[d]}</button>`).join("");
  return `<div class="daytabs" role="tablist">${tabs}</div>
    <div class="sheet"><table class="grid">
    <caption>${captionLabel} — ${DAY_NAMES[activeDay]}</caption>
    <thead>${head}</thead><tbody>${rows}</tbody></table></div>`;
}

function render() {
  const container = $("content");
  if (viewMode === "all") {
    const tabs = days().map((d) =>
      `<button class="daytab ${d === activeDay ? "active" : ""}" data-day="${d}">${DAY_NAMES[d]}</button>`).join("");
    container.innerHTML = `<div class="daytabs" role="tablist">${tabs}</div>${renderGrid()}`;
    container.querySelectorAll(".daytab").forEach((b) =>
      b.addEventListener("click", () => { activeDay = b.dataset.day; render(); }));
  } else if (viewMode === "teacher") {
    container.innerHTML = renderPersonal("label_teacher_view",
      (s) => s.teacher_code === entity, `Personal week for teacher <strong>${entity}</strong>.`);
  } else if (viewMode === "group") {
    container.innerHTML = renderPersonal("label_group_view",
      (s) => s.class_group_code === entity, `Personal week for class group <strong>${entity}</strong>.`);
  } else if (viewMode === "semester") {
    const codes = classGroups.filter((g) => String(g.semester) === String(entity))
      .map((g) => g.code).sort();
    container.innerHTML = renderCohort(codes, `Semester ${entity} — all class groups`);
    bindCohortDayTabs();
  } else if (viewMode === "department") {
    const codes = classGroups.filter((g) => g.department_code === entity)
      .map((g) => g.code).sort();
    container.innerHTML = renderCohort(codes, `Department ${entity} — all class groups`);
    bindCohortDayTabs();
  }
  bindLessonInteractions();
}

function bindCohortDayTabs() {
  document.querySelectorAll(".daytab").forEach((b) =>
    b.addEventListener("click", () => { activeDay = b.dataset.day; render(); }));
}

function fillEntitySelect() {
  const select = $("entity-select");
  if (viewMode === "all") { select.hidden = true; return; }
  let values;
  if (viewMode === "group") values = [...new Set(scheduled().map((s) => s.class_group_code))].sort();
  else if (viewMode === "teacher") values = [...new Set(scheduled().map((s) => s.teacher_code))].sort();
  else if (viewMode === "semester") values = [...new Set(classGroups.map((g) => g.semester))].sort((a, b) => a - b);
  else values = [...new Set(classGroups.map((g) => g.department_code))].sort();
  select.innerHTML = values.map((v) => `<option>${v}</option>`).join("");
  select.hidden = false;
  entity = select.value;
}

/* ---- click-to-edit drawer ----------------------------------------------- */

function closeDrawer() {
  document.getElementById("edit-drawer")?.remove();
  document.getElementById("edit-backdrop")?.remove();
}

function openEditDrawer(sessionId) {
  const session = data.sessions.find((s) => s.id === Number(sessionId));
  if (!session) return;
  closeDrawer();

  const backdrop = document.createElement("div");
  backdrop.id = "edit-backdrop";
  backdrop.className = "drawer-backdrop";
  backdrop.addEventListener("click", closeDrawer);
  document.body.appendChild(backdrop);

  const maxSlot = Math.max(...data.sessions.filter((s) => s.slot_index).map((s) => s.slot_index), session.slot_index || 1);

  const drawer = document.createElement("div");
  drawer.id = "edit-drawer";
  drawer.className = "drawer";
  drawer.innerHTML = `
    <button class="close-x" id="drawer-close" aria-label="Close">&times;</button>
    <h3>${session.code_section}</h3>
    <div class="meta">${session.course_title}<br>${session.session_type} · ${session.duration_slots} slot(s)</div>
    <label>Day
      <select id="f-day">${DAY_ORDER.map((d) => `<option value="${d}" ${d === session.day_of_week ? "selected" : ""}>${DAY_NAMES[d]}</option>`).join("")}</select>
    </label>
    <label>Slot
      <select id="f-slot">${Array.from({ length: maxSlot }, (_, i) => i + 1)
        .map((i) => `<option value="${i}" ${i === session.slot_index ? "selected" : ""}>Slot ${i}</option>`).join("")}</select>
    </label>
    <label>Room
      <select id="f-room">${roomList.map((r) => `<option value="${r.id}" ${r.id === session.room_id ? "selected" : ""}>${r.code} (${r.room_type_code}, cap ${r.capacity})</option>`).join("")}</select>
    </label>
    <label>Teacher
      <select id="f-teacher">${teacherList.map((t) => `<option value="${t.id}" ${t.id === session.teacher_id ? "selected" : ""}>${t.code} — ${t.name}</option>`).join("")}</select>
    </label>
    <label><input type="checkbox" id="f-lock" ${session.is_locked ? "checked" : ""}> Lock this session in place</label>
    <div id="edit-error"></div>
    <div class="actions">
      <button class="btn quiet" id="drawer-cancel">Cancel</button>
      <button class="btn primary" id="drawer-save">Save</button>
    </div>`;
  document.body.appendChild(drawer);
  document.getElementById("drawer-close").addEventListener("click", closeDrawer);
  document.getElementById("drawer-cancel").addEventListener("click", closeDrawer);
  document.getElementById("drawer-save").addEventListener("click", () => saveEdit(session.id));
}

async function saveEdit(sessionId) {
  const errEl = $("edit-error");
  errEl.innerHTML = "";
  const payload = {
    day_of_week: document.getElementById("f-day").value,
    slot_index: Number(document.getElementById("f-slot").value),
    room_id: Number(document.getElementById("f-room").value),
    teacher_id: Number(document.getElementById("f-teacher").value),
    lock: document.getElementById("f-lock").checked,
  };
  const response = await fetch(`/api/v1/session/${sessionId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const body = await response.json().catch(() => null);
  if (!response.ok) {
    const details = (body?.error?.details || [])
      .map((key) => `<li><strong>${key}</strong> — ${CONSTRAINT_HINTS[key] || "violates a scheduling rule"}</li>`)
      .join("");
    errEl.innerHTML = `<div class="notice error"><strong>Couldn't save:</strong>
      ${body?.error?.message || "unknown error"}${details ? `<ul>${details}</ul>` : ""}</div>`;
    return;
  }
  closeDrawer();
  await reloadTimetable();
}

/* ---- drag-and-drop (room view, same day) --------------------------------- */

function bindLessonInteractions() {
  document.querySelectorAll(".lesson[data-session-id]").forEach((el) => {
    el.addEventListener("click", () => {
      if (!Auth.requireLogin()) return;
      openEditDrawer(el.dataset.sessionId);
    });
    el.addEventListener("dragstart", (e) => {
      e.dataTransfer.setData("text/plain", el.dataset.sessionId);
    });
  });
  document.querySelectorAll("td[data-room][data-slot]").forEach((td) => {
    td.addEventListener("dragover", (e) => { e.preventDefault(); td.classList.add("drag-over"); });
    td.addEventListener("dragleave", () => td.classList.remove("drag-over"));
    td.addEventListener("drop", async (e) => {
      e.preventDefault();
      td.classList.remove("drag-over");
      if (!Auth.requireLogin()) return;
      const sessionId = e.dataTransfer.getData("text/plain");
      if (td.querySelector(".lesson")) return; // only drop on empty cells
      const response = await fetch(`/api/v1/session/${sessionId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ day_of_week: activeDay, slot_index: Number(td.dataset.slot),
          room_id: roomList.find((r) => r.code === td.dataset.room)?.id }),
      });
      if (!response.ok) {
        const body = await response.json().catch(() => null);
        alert(`Couldn't move it there: ${body?.error?.message || "hard constraint violated"}`);
        return;
      }
      await reloadTimetable();
    });
  });
}

/* ---- boot ----------------------------------------------------------------- */

async function reloadTimetable() {
  const runs = (await fetchJson("/api/v1/solve/runs?limit=20"))?.runs || [];
  const latest = runs.find((r) => r.status === "COMPLETED");
  if (!latest) return;
  data = await fetchJson(`/api/v1/timetable/${latest.job_id}`);
  if (!data) return;
  conflicts = computeConflicts(data.sessions);
  renderConflictBanner();
  const violations = data.feasibility_report.reduce((n, r) => n + r.violations, 0);
  $("badge-feasible").textContent = violations === 0 ? "✓ 0 clashes" : `⚠ ${violations} violations`;
  const penalty = data.summary?.soft_penalty_total ?? 0;
  $("badge-penalty").innerHTML = `Quality penalty <strong>${penalty.toFixed(0)}</strong>`;
  $("badge-sessions").textContent = `${scheduled().length} classes / week`;
  if (!activeDay || !days().includes(activeDay)) activeDay = days()[0];
  render();
}

async function boot() {
  const [runs, groups, rooms, teachers] = await Promise.all([
    fetchJson("/api/v1/solve/runs?limit=20"),
    fetchJson("/api/v1/class-groups"),
    fetchJson("/api/v1/rooms"),
    fetchJson("/api/v1/teachers"),
  ]);
  classGroups = groups?.class_groups || [];
  roomList = rooms?.rooms || [];
  teacherList = teachers?.teachers || [];

  const latest = (runs?.runs || []).find((r) => r.status === "COMPLETED");
  if (!latest) return; // keep the empty state
  $("toolbar").hidden = false;
  await reloadTimetable();

  $("view-mode").addEventListener("change", (e) => {
    viewMode = e.target.value;
    fillEntitySelect();
    render();
  });
  $("entity-select").addEventListener("change", (e) => {
    entity = e.target.value;
    render();
  });
  document.addEventListener("auth-changed", () => render());
}

boot();
