/* Timetable viewer: day tabs + room grid built from the canonical JSON API. */

const $ = (id) => document.getElementById(id);
const DAY_ORDER = ["SAT", "SUN", "MON", "TUE", "WED", "THU", "FRI"];
const DAY_NAMES = { SAT: "Saturday", SUN: "Sunday", MON: "Monday", TUE: "Tuesday",
                    WED: "Wednesday", THU: "Thursday", FRI: "Friday" };

let data = null;        // /api/v1/timetable/{id} payload
let activeDay = null;
let viewMode = "all";
let entity = null;      // selected group/teacher code

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

function lessonHtml(s, mode) {
  const type = s.session_type.toLowerCase();
  const dim = entity && (
    (viewMode === "group" && s.class_group_code !== entity) ||
    (viewMode === "teacher" && s.teacher_code !== entity)
  );
  const meta = mode === "teacher"
    ? `${s.class_group_code} · ${s.room_code}`
    : `${s.class_group_code} · ${s.teacher_code}`;
  return `<div class="lesson ${type} ${dim ? "dim" : ""}" title="${s.course_title}">
    <span class="c">${s.course_code}</span> <span class="m">(${s.session_type})</span><br>
    <span class="m">${meta}</span></div>`;
}

function renderGrid() {
  const bySlot = new Map(); // `${room}|${slot}` -> session (expanded over duration)
  const rooms = new Set();
  for (const s of scheduled()) {
    if (s.day_of_week !== activeDay) continue;
    rooms.add(s.room_code);
    for (let i = 0; i < s.duration_slots; i += 1) {
      bySlot.set(`${s.room_code}|${s.slot_index + i}`, s);
    }
  }
  const roomList = [...rooms].sort();
  const slots = slotIndexes();
  const times = new Map();
  for (const s of scheduled()) {
    if (s.start_time) times.set(s.slot_index, s.start_time);
  }

  const head = `<tr><th class="roomcol">Room</th>` +
    slots.map((i) => `<th>Slot ${i}${times.has(i) ? `<br>${times.get(i)}` : ""}</th>`).join("") +
    `</tr>`;
  const body = roomList.map((room) => {
    const cells = [];
    for (let i = 0; i < slots.length;) {
      const s = bySlot.get(`${room}|${slots[i]}`);
      if (s && s.slot_index === slots[i]) {
        cells.push(`<td colspan="${s.duration_slots}">${lessonHtml(s, "all")}</td>`);
        i += s.duration_slots;
      } else if (s) { // continuation of a multi-slot session (already spanned)
        i += 1;
      } else {
        cells.push("<td></td>");
        i += 1;
      }
    }
    return `<tr><th class="roomcol">${room}</th>${cells.join("")}</tr>`;
  }).join("");

  return `<div class="sheet"><table class="grid">
    <caption>${DAY_NAMES[activeDay]} — every room, every slot.
      Coloured edge: lecture (green), lab (sienna), tutorial (gold).</caption>
    <thead>${head}</thead><tbody>${body}</tbody></table></div>`;
}

function renderPersonal() {
  const mine = scheduled().filter((s) =>
    viewMode === "group" ? s.class_group_code === entity : s.teacher_code === entity);
  const slots = slotIndexes();
  const head = `<tr><th class="roomcol">Day</th>` +
    slots.map((i) => `<th>Slot ${i}</th>`).join("") + `</tr>`;
  const body = days().map((day) => {
    const bySlot = new Map();
    for (const s of mine) {
      if (s.day_of_week !== day) continue;
      bySlot.set(s.slot_index, s);
    }
    const cells = [];
    for (let i = 0; i < slots.length;) {
      const s = bySlot.get(slots[i]);
      if (s) {
        cells.push(`<td colspan="${s.duration_slots}">${lessonHtml(s, viewMode)}</td>`);
        i += s.duration_slots;
      } else {
        cells.push("<td></td>");
        i += 1;
      }
    }
    return `<tr><th class="roomcol">${DAY_NAMES[day]}</th>${cells.join("")}</tr>`;
  }).join("");
  const label = viewMode === "group" ? "class group" : "teacher";
  return `<div class="sheet"><table class="grid">
    <caption>Personal week for ${label} <strong>${entity}</strong>.</caption>
    <thead>${head}</thead><tbody>${body}</tbody></table></div>`;
}

function render() {
  const container = $("content");
  if (viewMode === "all") {
    const tabs = days().map((d) =>
      `<button class="daytab ${d === activeDay ? "active" : ""}" data-day="${d}">
         ${DAY_NAMES[d]}</button>`).join("");
    container.innerHTML = `<div class="daytabs" role="tablist">${tabs}</div>${renderGrid()}`;
    container.querySelectorAll(".daytab").forEach((b) =>
      b.addEventListener("click", () => { activeDay = b.dataset.day; render(); }));
  } else {
    container.innerHTML = renderPersonal();
  }
}

function fillEntitySelect() {
  const select = $("entity-select");
  if (viewMode === "all") { select.hidden = true; return; }
  const key = viewMode === "group" ? "class_group_code" : "teacher_code";
  const values = [...new Set(scheduled().map((s) => s[key]))].sort();
  select.innerHTML = values.map((v) => `<option>${v}</option>`).join("");
  select.hidden = false;
  entity = select.value;
}

async function boot() {
  const runs = (await fetchJson("/api/v1/solve/runs?limit=20"))?.runs || [];
  const latest = runs.find((r) => r.status === "COMPLETED");
  if (!latest) return; // keep the empty state
  data = await fetchJson(`/api/v1/timetable/${latest.job_id}`);
  if (!data) return;

  $("toolbar").hidden = false;
  const violations = data.feasibility_report.reduce((n, r) => n + r.violations, 0);
  $("badge-feasible").textContent = violations === 0
    ? "✓ 0 clashes" : `⚠ ${violations} violations`;
  const penalty = data.soft_constraint_report
    .reduce((n, r) => n + r.weighted_penalty, 0);
  $("badge-penalty").innerHTML = `Quality penalty <strong>${penalty.toFixed(0)}</strong>`;
  $("badge-sessions").textContent = `${scheduled().length} classes / week`;

  activeDay = days()[0];
  render();

  $("view-mode").addEventListener("change", (e) => {
    viewMode = e.target.value;
    fillEntitySelect();
    render();
  });
  $("entity-select").addEventListener("change", (e) => {
    entity = e.target.value;
    render();
  });
}

boot();
