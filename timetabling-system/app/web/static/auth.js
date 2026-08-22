/* Shared login/logout used by every page. Reads are always public; this only
 * gates the controls that call mutating endpoints. */

const Auth = (() => {
  let current = null; // {authenticated, username, is_admin} | null (unknown yet)

  async function refresh() {
    const response = await fetch("/api/v1/auth/me");
    current = await response.json();
    renderBadge();
    document.dispatchEvent(new CustomEvent("auth-changed", { detail: current }));
    return current;
  }

  function isAuthenticated() {
    return !!(current && current.authenticated);
  }

  function renderBadge() {
    const el = document.getElementById("auth-badge");
    if (!el) return;
    if (isAuthenticated()) {
      el.innerHTML = `<span class="mono">${current.username}</span> ` +
        `<button class="btn quiet small" id="auth-logout-btn">Log out</button>`;
      document.getElementById("auth-logout-btn").addEventListener("click", async () => {
        await fetch("/api/v1/auth/logout", { method: "POST" });
        await refresh();
      });
    } else {
      el.innerHTML = `<button class="btn quiet small" id="auth-login-btn">Admin login</button>`;
      document.getElementById("auth-login-btn").addEventListener("click", openModal);
    }
  }

  function ensureModal() {
    if (document.getElementById("login-modal")) return;
    const wrap = document.createElement("div");
    wrap.id = "login-modal";
    wrap.className = "modal-backdrop";
    wrap.hidden = true;
    wrap.innerHTML = `
      <form class="modal-card" id="login-form">
        <h3>Admin login</h3>
        <p class="hint">Sign in to import data, run the solver, or edit the routine.
        Viewing the timetable never requires an account.</p>
        <label>Username<input name="username" autocomplete="username" required></label>
        <label>Password<input name="password" type="password" autocomplete="current-password" required></label>
        <div id="login-error" class="notice error" hidden></div>
        <div class="row" style="justify-content:flex-end">
          <button type="button" class="btn quiet" id="login-cancel">Cancel</button>
          <button type="submit" class="btn primary">Log in</button>
        </div>
      </form>`;
    document.body.appendChild(wrap);
    wrap.addEventListener("click", (e) => { if (e.target === wrap) closeModal(); });
    document.getElementById("login-cancel").addEventListener("click", closeModal);
    document.getElementById("login-form").addEventListener("submit", async (e) => {
      e.preventDefault();
      const form = new FormData(e.target);
      const errEl = document.getElementById("login-error");
      errEl.hidden = true;
      const response = await fetch("/api/v1/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          username: form.get("username"), password: form.get("password"),
        }),
      });
      if (!response.ok) {
        const body = await response.json().catch(() => null);
        errEl.textContent = body?.error?.message || "Login failed.";
        errEl.hidden = false;
        return;
      }
      closeModal();
      await refresh();
    });
  }

  function openModal() {
    ensureModal();
    document.getElementById("login-modal").hidden = false;
    document.querySelector("#login-form input[name=username]").focus();
  }

  function closeModal() {
    const modal = document.getElementById("login-modal");
    if (modal) modal.hidden = true;
  }

  /** Call before a write action. Returns true if already logged in; if not,
   * opens the login modal and returns false (caller should abort). */
  function requireLogin() {
    if (isAuthenticated()) return true;
    ensureModal();
    openModal();
    return false;
  }

  return { refresh, isAuthenticated, requireLogin, current: () => current };
})();

document.addEventListener("DOMContentLoaded", () => Auth.refresh());
