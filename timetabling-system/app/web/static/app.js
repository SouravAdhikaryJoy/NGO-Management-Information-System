/* Workbench page logic: demo load, import, solve with live status, runs list. */

const $ = (id) => document.getElementById(id);

function notice(el, kind, html) {
  el.innerHTML = `<div class="notice ${kind === "error" ? "error" : ""}">${html}</div>`;
}

async function api(path, options = {}) {
  const response = await fetch(path, options);
  let body = null;
  try { body = await response.json(); } catch { /* non-JSON */ }
  return { ok: response.ok, status: response.status, body };
}

/* ---- import ------------------------------------------------------------- */

function describeImport(el, body) {
  if (body.ok) {
    const loaded = Object.entries(body.counts)
      .filter(([, n]) => n > 0)
      .map(([sheet, n]) => `${sheet}&nbsp;(${n})`)
      .join(", ");
    notice(el, "ok", `<strong>Imported successfully.</strong> ${loaded}`);
  } else {
    const items = body.errors.slice(0, 8)
      .map((e) => `<li><strong>${e.sheet}</strong> row ${e.row ?? "—"}, ` +
                  `<em>${e.field}</em>: ${e.error}</li>`)
      .join("");
    const more = body.errors.length > 8
      ? `<li>…and ${body.errors.length - 8} more</li>` : "";
    notice(el, "error",
      `<strong>Nothing was saved — ${body.errors.length} problem(s) found:</strong>` +
      `<ul>${items}${more}</ul>`);
  }
}

async function loadDemo() {
  const el = $("import-result");
  notice(el, "ok", "Loading demo dataset…");
  const { body } = await api("/api/v1/import/demo", { method: "POST" });
  describeImport(el, body);
  document.querySelector("#workbench").scrollIntoView({ behavior: "smooth" });
}

$("btn-demo").addEventListener("click", loadDemo);
$("hero-demo").addEventListener("click", loadDemo);

$("btn-import").addEventListener("click", async () => {
  const el = $("import-result");
  const input = $("file-input");
  if (!input.files.length) {
    notice(el, "error", "Choose an .xlsx workbook first (or use the demo data).");
    return;
  }
  const form = new FormData();
  form.append("file", input.files[0]);
  notice(el, "ok", "Validating and importing…");
  const { body } = await api("/api/v1/import", { method: "POST", body: form });
  describeImport(el, body);
});

/* ---- solve -------------------------------------------------------------- */

let pollTimer = null;

function setSolveStatus(kind, text) {
  $("solve-dot").className = `dot ${kind}`;
  $("solve-text").textContent = text;
}

function showCompleted(status) {
  setSolveStatus("ok",
    `Solved in ${status.runtime_seconds?.toFixed(1)}s — 0 hard violations, ` +
    `quality penalty ${status.soft_penalty?.toFixed(0)}.`);
  $("solve-detail").innerHTML =
    `<div class="notice">Routine is ready. <a href="/timetable">Open the timetable</a> ` +
    `or download it from the Results card.</div>`;
  enableExports(status.job_id);
  refreshRuns();
}

async function poll(jobId) {
  const { body } = await api(`/api/v1/solve/${jobId}/status`);
  if (!body) return;
  if (body.status === "PENDING" || body.status === "RUNNING") {
    setSolveStatus("running", `Solving… (${body.status.toLowerCase()})`);
    pollTimer = setTimeout(() => poll(jobId), 1200);
  } else if (body.status === "COMPLETED") {
    showCompleted(body);
  } else {
    setSolveStatus("bad", `Run ended with status ${body.status}.`);
    if (body.error) {
      $("solve-detail").innerHTML =
        `<div class="notice error">${String(body.error).split("\n")[0]}</div>`;
    }
    refreshRuns();
  }
}

$("btn-solve").addEventListener("click", async () => {
  clearTimeout(pollTimer);
  $("solve-detail").innerHTML = "";
  setSolveStatus("running", "Starting solver…");
  const { ok, body } = await api("/api/v1/solve", { method: "POST" });
  if (!ok) {
    setSolveStatus("bad", body?.error?.message || "Could not start the solver.");
    return;
  }
  poll(body.job_id);
});

/* ---- results ------------------------------------------------------------ */

function enableExports(jobId) {
  $("export-row").hidden = false;
  for (const fmt of ["xlsx", "csv", "ics", "pdf"]) {
    $(`exp-${fmt}`).href = `/api/v1/timetable/${jobId}/export?format=${fmt}`;
  }
}

async function refreshRuns() {
  const { body } = await api("/api/v1/solve/runs?limit=6");
  const runs = body?.runs || [];
  const table = $("runs-table");
  if (!runs.length) { table.hidden = true; return; }
  table.hidden = false;
  table.querySelector("tbody").innerHTML = runs.map((r) => `
    <tr>
      <td class="mono">${r.job_id.slice(0, 8)}</td>
      <td><span class="chip ${r.status}">${r.status}</span></td>
      <td>${r.soft_penalty == null ? "—" : r.soft_penalty.toFixed(0)}</td>
      <td>${r.runtime_seconds == null ? "—" : r.runtime_seconds.toFixed(1) + "s"}</td>
    </tr>`).join("");
  const latest = runs.find((r) => r.status === "COMPLETED");
  if (latest) enableExports(latest.job_id);
}

refreshRuns();
