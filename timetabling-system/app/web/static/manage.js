/* Manage page: course/teacher tables, public read, admin-gated edits. */

const $ = (id) => document.getElementById(id);

async function fetchJson(path) {
  const response = await fetch(path);
  if (!response.ok) return null;
  return response.json();
}

function warn(el, rows) {
  if (!rows || !rows.length) { el.innerHTML = ""; return; }
  const items = rows.map((r) => `<li><strong>${r.key}</strong>: ${r.description} — ${r.violations} case(s)</li>`).join("");
  el.innerHTML = `<div class="conflict-banner" style="margin-bottom:16px">
    <span class="mark">⚠</span>
    <div><strong>This change created new conflicts:</strong><ul>${items}</ul>
    Fix them on the <a href="/timetable">timetable page</a> or re-run the solver.</div></div>`;
}

async function loadCourses() {
  const body = await fetchJson("/api/v1/courses");
  const teachers = (await fetchJson("/api/v1/teachers"))?.teachers || [];
  const courses = body?.courses || [];
  const tbody = document.querySelector("#courses-table tbody");
  if (!courses.length) {
    tbody.innerHTML = `<tr><td colspan="8" class="pill-count">No courses yet — import data on the <a href="/">workbench</a>.</td></tr>`;
    return;
  }
  const teacherOptions = teachers.map((t) => `<option value="${t.id}">${t.code} — ${t.name}</option>`).join("");
  tbody.innerHTML = courses.map((c) => `
    <tr data-course-id="${c.id}">
      <td class="mono">${c.code}</td>
      <td>${c.title}</td>
      <td>${c.department_code}</td>
      <td>${c.semester}</td>
      <td>${c.session_types.map((st) => `${st.session_type} ×${st.sessions_per_week}`).join(", ")}</td>
      <td class="pill-count">${c.sections.length} section(s)</td>
      <td>
        <select class="course-teacher" ${Auth.isAuthenticated() ? "" : "disabled"}>
          ${teacherOptions}
        </select>
      </td>
      <td><button class="btn small save-btn course-save" ${Auth.isAuthenticated() ? "" : "disabled"}>Save</button></td>
    </tr>`).join("");
  for (const row of tbody.querySelectorAll("tr[data-course-id]")) {
    const courseId = row.dataset.courseId;
    const course = courses.find((c) => String(c.id) === courseId);
    row.querySelector(".course-teacher").value = course.teacher_id ?? "";
  }
  tbody.querySelectorAll(".course-save").forEach((btn) => {
    btn.addEventListener("click", async () => {
      if (!Auth.requireLogin()) return;
      const row = btn.closest("tr");
      const courseId = row.dataset.courseId;
      const teacherId = Number(row.querySelector(".course-teacher").value);
      const response = await fetch(`/api/v1/course/${courseId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ teacher_id: teacherId }),
      });
      const respBody = await response.json().catch(() => null);
      if (!response.ok) {
        alert(`Couldn't save: ${respBody?.error?.message || "unknown error"}`);
        return;
      }
      warn($("course-warning"), respBody.new_hard_violations);
      await loadCourses();
      await loadTeachers();
    });
  });
}

async function loadTeachers() {
  const body = await fetchJson("/api/v1/teachers");
  const teachers = body?.teachers || [];
  const tbody = document.querySelector("#teachers-table tbody");
  if (!teachers.length) {
    tbody.innerHTML = `<tr><td colspan="7" class="pill-count">No teachers yet.</td></tr>`;
    return;
  }
  tbody.innerHTML = teachers.map((t) => `
    <tr data-teacher-id="${t.id}">
      <td class="mono">${t.code}</td>
      <td>${t.name}</td>
      <td>${t.department_code}</td>
      <td class="pill-count">${t.weekly_sessions_assigned} session(s)</td>
      <td><input type="number" min="1" class="t-max-day" value="${t.max_sessions_per_day}"
        style="width:64px" ${Auth.isAuthenticated() ? "" : "disabled"}></td>
      <td><input type="number" min="1" class="t-max-week" value="${t.max_sessions_per_week}"
        style="width:64px" ${Auth.isAuthenticated() ? "" : "disabled"}></td>
      <td><button class="btn small save-btn teacher-save" ${Auth.isAuthenticated() ? "" : "disabled"}>Save</button></td>
    </tr>`).join("");
  tbody.querySelectorAll(".teacher-save").forEach((btn) => {
    btn.addEventListener("click", async () => {
      if (!Auth.requireLogin()) return;
      const row = btn.closest("tr");
      const teacherId = row.dataset.teacherId;
      const response = await fetch(`/api/v1/teacher/${teacherId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          max_sessions_per_day: Number(row.querySelector(".t-max-day").value),
          max_sessions_per_week: Number(row.querySelector(".t-max-week").value),
        }),
      });
      const respBody = await response.json().catch(() => null);
      if (!response.ok) {
        alert(`Couldn't save: ${respBody?.error?.message || "unknown error"}`);
        return;
      }
      warn($("teacher-warning"), respBody.new_hard_violations);
      await loadTeachers();
    });
  });
}

async function boot() {
  await Promise.all([loadCourses(), loadTeachers()]);
  document.addEventListener("auth-changed", async () => {
    await Promise.all([loadCourses(), loadTeachers()]);
  });
}

boot();
