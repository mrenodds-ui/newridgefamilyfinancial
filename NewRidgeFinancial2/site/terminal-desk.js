const SESSION_HEADER = "X-NR2-Session-Token";
const API = "/api/apex";
let sessionToken = "";
let busy = false;
let halQueue = Promise.resolve();
let lastStatus = null;
let liveBundle = {};
let currentDesk = "practice";
let lastHalText = "Booting multi-desk terminal…";
let lastHalMode = "…";

const DESKS = {
  practice: {
    id: "practice",
    label: "PRACTICE",
    title: "Practice desk",
    layout: "3x3",
    panes: [
      {
        id: "prod",
        title: "Production vs collections",
        widgetId: "financial-dual-trend",
        page: "financial",
        cls: "span2",
        kind: "dual",
      },
      {
        id: "sd",
        title: "SoftDent gaps",
        widgetId: "softdent-collections-gap",
        page: "softdent",
        kind: "status-bars",
      },
      {
        id: "claims",
        title: "Claims aging",
        widgetId: "claims-aging-exposure",
        page: "claims",
        kind: "claims-bars",
      },
      {
        id: "ar",
        title: "A/R aging",
        widgetId: "ar-aging-chart",
        page: "ar",
        kind: "ar-donut",
      },
      {
        id: "heat",
        title: "Huddle heat",
        widgetId: "om-daily-huddle",
        page: "office-manager",
        kind: "heat",
      },
      {
        id: "qb",
        title: "QB linkage",
        widgetId: "qb-ap-aging",
        page: "quickbooks",
        kind: "status-bars-alt",
      },
      {
        id: "movers",
        title: "Top movers",
        widgetId: "hal-ai-insight",
        page: "hal",
        kind: "movers",
      },
      {
        id: "tape",
        title: "Exception tape",
        widgetId: "hal-sys-console",
        page: "hal",
        sub: "system-logs",
        kind: "tape",
      },
    ],
  },
  close: {
    id: "close",
    label: "CLOSE",
    title: "Period close",
    layout: "3x3",
    panes: [
      {
        id: "vitals",
        title: "Financial vitals",
        widgetId: "financial-vital-signs",
        page: "financial",
        cls: "span2",
        kind: "vitals",
      },
      {
        id: "cmdstrip",
        title: "Close command strip",
        widgetId: "financial-command-strip",
        page: "financial",
        kind: "note",
      },
      {
        id: "ebitda",
        title: "EBITDA station",
        widgetId: "ebitda-station",
        page: "financial",
        kind: "note",
      },
      {
        id: "qbpl",
        title: "QB P&L / AP",
        widgetId: "qb-ap-aging",
        page: "quickbooks",
        kind: "status-bars-alt",
      },
      {
        id: "payroll",
        title: "Payroll gap",
        widgetId: "qb-payroll-gap",
        page: "financial",
        kind: "note",
      },
      {
        id: "recon",
        title: "Reconciliation",
        widgetId: "reconciliation-status",
        page: "financial",
        kind: "note",
      },
      {
        id: "dual",
        title: "Dual trend",
        widgetId: "financial-dual-trend",
        page: "financial",
        kind: "dual",
      },
      {
        id: "ops",
        title: "Financial ops",
        widgetId: "financial-ops-strip",
        page: "financial",
        kind: "note",
      },
    ],
  },
  claims: {
    id: "claims",
    label: "CLAIMS",
    title: "Claims desk",
    layout: "3x3",
    panes: [
      {
        id: "aging",
        title: "Aging exposure",
        widgetId: "claims-aging-exposure",
        page: "claims",
        cls: "span2",
        kind: "claims-bars",
      },
      {
        id: "exec",
        title: "Executive strip",
        widgetId: "claims-executive-strip",
        page: "claims",
        kind: "note",
      },
      {
        id: "kanban",
        title: "Open kanban",
        widgetId: "claims-open-kanban",
        page: "claims",
        kind: "note",
      },
      {
        id: "critical",
        title: "Critical actions",
        widgetId: "claims-top-critical",
        page: "claims",
        kind: "note",
      },
      {
        id: "era",
        title: "ERA gauge",
        widgetId: "claims-era-gauge",
        page: "claims",
        kind: "note",
      },
      {
        id: "denial",
        title: "Denial pareto",
        widgetId: "denial-pareto",
        page: "claims",
        kind: "note",
      },
      {
        id: "risk",
        title: "Risk analytics",
        widgetId: "claims-risk-analytics",
        page: "claims",
        kind: "note",
      },
      {
        id: "signoff",
        title: "Clinical sign-off",
        widgetId: "clinical-signoff-queue",
        page: "claims",
        kind: "note",
      },
    ],
  },
  ar: {
    id: "ar",
    label: "A/R",
    title: "A/R book",
    layout: "3x3",
    panes: [
      {
        id: "aging",
        title: "Aging chart",
        widgetId: "ar-aging-chart",
        page: "ar",
        cls: "span2",
        kind: "ar-donut",
      },
      {
        id: "vitals",
        title: "A/R vitals",
        widgetId: "ar-vitals-strip",
        page: "ar",
        kind: "note",
      },
      {
        id: "heat",
        title: "Balance heatmap",
        widgetId: "ar-heatmap-grid",
        page: "ar",
        kind: "note",
      },
      {
        id: "tasks",
        title: "Collection tasks",
        widgetId: "ar-collection-task-list",
        page: "ar",
        kind: "note",
      },
      {
        id: "outlook",
        title: "Aging outlook",
        widgetId: "ar-aging-outlook",
        page: "ar",
        kind: "note",
      },
      {
        id: "follow",
        title: "Follow-up",
        widgetId: "ar-follow-up",
        page: "ar",
        kind: "note",
      },
      {
        id: "waterfall",
        title: "Waterfall",
        widgetId: "ar-waterfall",
        page: "ar",
        kind: "note",
      },
      {
        id: "gauge",
        title: "Collections gauge",
        widgetId: "collections-gauge",
        page: "ar",
        kind: "note",
      },
    ],
  },
  trust: {
    id: "trust",
    label: "TRUST",
    title: "Import trust",
    layout: "2x3",
    panes: [
      {
        id: "health",
        title: "Import health",
        widgetId: "hal-import-health",
        page: "hal",
        kind: "trust-health",
      },
      {
        id: "sync",
        title: "Sync CTA",
        widgetId: "hal-sync-cta",
        page: "hal",
        kind: "note",
      },
      {
        id: "posture",
        title: "Program posture",
        widgetId: "hal-program-posture",
        page: "hal",
        kind: "note",
      },
      {
        id: "sdgap",
        title: "SoftDent gap",
        widgetId: "softdent-collections-gap",
        page: "softdent",
        kind: "note",
      },
      {
        id: "tape",
        title: "System log tape",
        widgetId: "hal-sys-console",
        page: "hal",
        sub: "system-logs",
        cls: "span2",
        kind: "tape",
      },
      {
        id: "insight",
        title: "AI insight",
        widgetId: "hal-ai-insight",
        page: "hal",
        kind: "movers",
      },
    ],
  },
};

function toast(msg) {
  const el = document.getElementById("toast");
  el.textContent = msg;
  el.classList.add("show");
  clearTimeout(toast._t);
  toast._t = setTimeout(() => el.classList.remove("show"), 3200);
}

async function ensureSession() {
  const res = await fetch("/api/app-info", { cache: "no-store", credentials: "same-origin" });
  const refresh = res.headers.get("X-NR2-Session-Refresh") || res.headers.get(SESSION_HEADER) || "";
  if (refresh) sessionToken = refresh.trim();
  if (res.ok) {
    const info = await res.json().catch(() => ({}));
    sessionToken = String((info && (info.sessionToken || info.csrfToken)) || sessionToken || "").trim();
  }
  return sessionToken;
}

async function apexFetch(url, options, retried) {
  const opts = Object.assign({ credentials: "same-origin", cache: "no-store" }, options || {});
  opts.headers = Object.assign({}, opts.headers || {});
  if (!sessionToken) await ensureSession();
  if (sessionToken) opts.headers[SESSION_HEADER] = sessionToken;
  if (opts.body && !opts.headers["Content-Type"]) opts.headers["Content-Type"] = "application/json";
  const res = await fetch(url, opts);
  const rotated = res.headers.get("X-NR2-Session-Refresh") || res.headers.get(SESSION_HEADER) || "";
  if (rotated) sessionToken = rotated.trim();
  if (res.status === 403 && !retried) {
    sessionToken = "";
    await ensureSession();
    return apexFetch(url, options, true);
  }
  return res;
}

function escapeHtml(s) {
  return String(s || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

function setHalPrint(text, mode) {
  lastHalText = text;
  if (mode) lastHalMode = mode;
  const el = document.getElementById("halPrint");
  const modeEl = document.getElementById("halMode");
  if (el) el.innerHTML = `<div class="who">HAL // ${DESKS[currentDesk].label}</div>${escapeHtml(text)}`;
  if (modeEl && mode) modeEl.textContent = mode;
}

function focusPane(paneId) {
  document.querySelectorAll(".pane").forEach((p) => {
    p.classList.toggle("is-focus", p.dataset.pane === paneId);
    if (p.dataset.pane === paneId) {
      p.classList.remove("is-flash");
      void p.offsetWidth;
      p.classList.add("is-flash");
    }
  });
}

function mkBars(el, vals, alt) {
  if (!el) return;
  el.innerHTML = (vals || [])
    .map((v, i) => {
      const muted = v == null;
      const h = muted ? 8 : Math.max(8, Math.round(Number(v) * 100));
      const cls = muted ? "mute" : alt && i % 2 ? "alt" : "";
      return `<i class="${cls}" style="height:${h}%"></i>`;
    })
    .join("");
}

function pointsToPolyline(points, width, height) {
  const pts = (points || []).filter((p) => p != null && Number.isFinite(Number(p)));
  if (!pts.length) return "";
  const max = Math.max(...pts.map(Number), 1);
  const min = Math.min(...pts.map(Number), 0);
  const span = Math.max(max - min, 1e-6);
  return pts
    .map((v, i) => {
      const x = pts.length === 1 ? width / 2 : (i / (pts.length - 1)) * width;
      const y = height - ((Number(v) - min) / span) * (height - 16) - 8;
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    })
    .join(" ");
}

function widgetById(id) {
  return liveBundle.byId && liveBundle.byId[id] ? liveBundle.byId[id] : null;
}

function widgetStatusLabel(w) {
  if (!w) return "—";
  const st = String(w.status || "").toLowerCase();
  if (st === "empty" || w.emptyMessage) return "GATED";
  if (st === "warn" || st === "warning") return "WARN";
  if (st === "partial") return "PARTIAL";
  if (st === "ok" || st === "ready") return "LIVE";
  return (st || "LIVE").toUpperCase();
}

function paneBodyHtml(pane) {
  switch (pane.kind) {
    case "dual":
      return `<div class="legend"><span style="color:var(--amber)">Production</span><span style="color:var(--blue)">Collections</span><span class="blocked" data-role="gate">…</span></div>
        <svg class="chart" viewBox="0 0 640 160" preserveAspectRatio="none">
          <rect width="640" height="160" fill="rgba(255,255,255,0.02)"/>
          <polyline data-role="prod" fill="none" stroke="#f5a623" stroke-width="2" points="20,120 620,120"/>
          <polyline data-role="coll" fill="none" stroke="#4da3ff" stroke-width="2" points="20,132 620,132"/>
        </svg>`;
    case "status-bars":
    case "status-bars-alt":
      return `<div class="bars" data-role="bars"></div><div class="legend"><span data-role="gate">…</span></div>`;
    case "claims-bars":
      return `<svg class="chart" data-role="claims" viewBox="0 0 300 120" preserveAspectRatio="none"></svg>`;
    case "ar-donut":
      return `<svg class="chart" viewBox="0 0 220 120">
          <circle cx="70" cy="60" r="40" fill="none" stroke="#2a3340" stroke-width="16"/>
          <circle cx="70" cy="60" r="40" fill="none" stroke="#3dd68c" stroke-width="16" stroke-dasharray="60 251" transform="rotate(-90 70 60)" opacity=".45"/>
          <circle cx="70" cy="60" r="40" fill="none" stroke="#f5a623" stroke-width="16" stroke-dasharray="40 251" stroke-dashoffset="-60" transform="rotate(-90 70 60)" opacity=".45"/>
          <circle cx="70" cy="60" r="40" fill="none" stroke="#ff5c5c" stroke-width="16" stroke-dasharray="30 251" stroke-dashoffset="-100" transform="rotate(-90 70 60)" opacity=".35"/>
          <text x="120" y="48" fill="#8b97a8" font-size="10" font-family="ui-monospace, monospace">0-30</text>
          <text x="120" y="66" fill="#f5a623" font-size="10" font-family="ui-monospace, monospace" data-role="gate">…</text>
          <text x="120" y="84" fill="#ff5c5c" font-size="10" font-family="ui-monospace, monospace">90+ · no invent</text>
        </svg>`;
    case "heat":
      return `<div class="heat" data-role="heat"></div>`;
    case "tape":
      return `<table class="dense"><thead><tr><th>Src</th><th>Event</th><th>Lvl</th></tr></thead><tbody data-role="tape"></tbody></table>`;
    case "movers":
      return `<table class="dense"><thead><tr><th>Signal</th><th>Δ</th><th>State</th></tr></thead><tbody data-role="movers"></tbody></table>`;
    case "vitals":
      return `<div class="kpis" data-role="vitals" style="grid-template-columns:repeat(3,1fr)"></div>`;
    case "trust-health":
      return `<div class="kpis"><div class="kpi"><div class="l">Connected</div><div class="n" data-role="conn">—</div><div class="s">datasets</div></div>
        <div class="kpi"><div class="l">Missing</div><div class="n blocked" data-role="miss">—</div><div class="s">empty ≠ $0</div></div></div>
        <div class="note" data-role="gate">…</div>`;
    case "note":
    default:
      return `<div class="note" data-role="gate">Loading widget…</div><div class="list" data-role="list"></div>`;
  }
}

function renderStage() {
  const desk = DESKS[currentDesk];
  const stage = document.getElementById("stage");
  stage.dataset.layout = desk.layout || "3x3";
  stage.innerHTML = desk.panes
    .map((pane) => {
      const cls = pane.cls ? ` ${pane.cls}` : "";
      return `<div class="pane${cls}" data-pane="${pane.id}" data-widget="${pane.widgetId}" data-page="${pane.page}" data-kind="${pane.kind}">
        <div class="ph"><span>${escapeHtml(pane.title)}</span><span class="val" data-role="val">…</span></div>
        <div class="pb">${paneBodyHtml(pane)}</div>
      </div>`;
    })
    .join("");

  stage.querySelectorAll(".pane").forEach((el) => {
    el.addEventListener("click", () => activatePane(el.dataset.pane));
  });

  // persistent side HAL panes
  document.querySelectorAll(".side .pane").forEach((el) => {
    if (el.dataset.wired === "1") return;
    el.dataset.wired = "1";
    el.addEventListener("click", () => {
      const ask = "explain this widget";
      focusPane(el.dataset.pane);
      document.getElementById("q").value = `${ask} · ${el.dataset.widget}`;
      runHal(ask, {
        widgetId: el.dataset.widget,
        page: el.dataset.page || "hal",
        deskPane: el.dataset.pane,
      });
    });
  });

  document.getElementById("kpiDesk").textContent = desk.label;
  document.getElementById("kpiDeskS").textContent = desk.title;
  setHalPrint(lastHalText, lastHalMode);
  applyLiveToStage();
}

function parseDeskFromLocation() {
  const hash = String(location.hash || "").replace(/^#\/?/, "").toLowerCase();
  if (DESKS[hash]) return hash;
  const q = new URLSearchParams(location.search || "");
  const desk = String(q.get("desk") || "").toLowerCase();
  if (DESKS[desk]) return desk;
  return "practice";
}

function setDesk(deskId, pushHash) {
  if (!DESKS[deskId]) deskId = "practice";
  currentDesk = deskId;
  document.querySelectorAll("#tabs [data-desk], #nav [data-desk]").forEach((btn) => {
    btn.classList.toggle("active", btn.getAttribute("data-desk") === deskId);
  });
  if (pushHash !== false) {
    const next = `#/${deskId}`;
    if (location.hash !== next) history.pushState({ desk: deskId }, "", next);
  }
  renderStage();
  document.getElementById("cmdStatus").textContent = `TERMINAL · ${DESKS[deskId].label} · HAL wired`;
}

function activatePane(paneId) {
  const desk = DESKS[currentDesk];
  const pane = (desk.panes || []).find((p) => p.id === paneId);
  if (!pane) return;
  focusPane(paneId);
  const ask = "explain this widget";
  document.getElementById("q").value = `${ask} · ${pane.title} · ${pane.widgetId}`;
  runHal(ask, {
    widgetId: pane.widgetId,
    page: pane.page,
    deskPane: paneId,
    label: pane.title,
  });
}

function mapActionToPane(action) {
  if (!action) return null;
  const wid = String(action.widgetId || "");
  const desk = DESKS[currentDesk];
  for (const pane of desk.panes || []) {
    if (wid && wid === pane.widgetId) return pane.id;
  }
  return null;
}

async function applyActions(actions, preferredPane) {
  const list = Array.isArray(actions) ? actions : [];
  const results = [];
  if (preferredPane) focusPane(preferredPane);
  for (const action of list) {
    if (!action || !action.type) continue;
    const type = String(action.type);
    if (type === "navigate") {
      const page = String(action.page || "");
      if (page === "claims") setDesk("claims");
      else if (page === "ar") setDesk("ar");
      else if (page === "financial" || page === "taxes") setDesk("close");
      else if (page === "hal") setDesk("trust");
      else if (page === "softdent" || page === "office-manager") setDesk("practice");
      results.push(`navigate:${page}`);
      continue;
    }
    const pane = mapActionToPane(action);
    if (pane) focusPane(pane);
    if (type === "sync_imports") {
      try {
        const res = await apexFetch(`${API}/sync/trigger`, {
          method: "POST",
          body: JSON.stringify({ fullSync: true, source: "terminal-desk" }),
        });
        const data = await res.json().catch(() => ({}));
        results.push(data.ok === false ? "sync_fail" : "synced");
        toast(data.ok === false ? "Sync failed" : "Sync triggered");
        await refreshAll();
      } catch (err) {
        results.push("sync_err");
        toast("Sync error: " + err.message);
      }
    } else if (
      type === "focus_widget" ||
      type === "highlight_widget" ||
      type === "navigate" ||
      type === "refresh_page" ||
      type === "set_status_banner"
    ) {
      results.push(
        `${type}${action.widgetId ? ":" + action.widgetId : ""}${action.page ? ":" + action.page : ""}`
      );
    } else {
      results.push(type);
    }
  }
  if (preferredPane) focusPane(preferredPane);
  return results;
}

function runHal(query, context) {
  halQueue = halQueue.then(() => runHalNow(query, context)).catch(() => {});
  return halQueue;
}

async function runHalNow(query, context) {
  busy = true;
  const btn = document.getElementById("execBtn");
  btn.disabled = true;
  document.getElementById("cmdStatus").textContent = `TERMINAL · ${DESKS[currentDesk].label} · board-actions…`;
  setHalPrint("Running board-actions…", "BUSY");
  const preferredPane = context && context.deskPane;

  // Desk navigation commands
  const deskJump = String(query || "").toLowerCase().match(
    /\b(?:go to|open|switch to)\s+(practice|close|claims|a\/?r|trust)\b/
  );
  if (deskJump) {
    const raw = deskJump[1].replace("/", "");
    const d = raw === "ar" ? "ar" : raw;
    setDesk(d);
    setHalPrint(`Switched to ${DESKS[currentDesk].title}.`, "BOARD");
    busy = false;
    btn.disabled = false;
    return;
  }

  try {
    const page = (context && context.page) || "hal";
    const res = await apexFetch(`${API}/hal/board-actions`, {
      method: "POST",
      body: JSON.stringify({ query, page, context: context || {} }),
    });
    const board = await res.json().catch(() => ({}));
    let actions = Array.isArray(board.actions) ? board.actions.slice() : [];
    if (context && context.widgetId) {
      const hasFocus = actions.some(
        (a) => a && (a.type === "focus_widget" || a.type === "highlight_widget")
      );
      if (!hasFocus) {
        actions = [
          { type: "focus_widget", widgetId: context.widgetId },
          { type: "highlight_widget", widgetId: context.widgetId, ms: 4000 },
        ].concat(actions);
      }
    }
    const results = actions.length
      ? await applyActions(actions, preferredPane)
      : (preferredPane && focusPane(preferredPane), []);
    let reply = "";
    let mode = "BOARD";
    if (board.handled || (context && context.widgetId && results.length)) {
      reply = String(
        board.reply ||
          (Array.isArray(board.notes) && board.notes.join(" ")) ||
          (context && context.widgetId
            ? `Focusing widget \`${context.widgetId}\` on ${DESKS[currentDesk].title} (import-backed only).`
            : "Board updated.")
      );
    } else {
      mode = "CHAT";
      try {
        const chatRes = await apexFetch("/api/hal/evaluate-query", {
          method: "POST",
          body: JSON.stringify({
            query,
            lane: "chat8b",
            shiftContext: {
              page,
              desk: currentDesk,
              widgetId: context && context.widgetId,
              honesty: "Do not invent financial dollar amounts. Prefer import-backed facts.",
            },
          }),
        });
        const chat = await chatRes.json().catch(() => ({}));
        reply = String((chat && (chat.text || chat.reply || (chat.message && chat.message.content))) || "");
        if (!reply && chat && chat.error) {
          reply = /connection refused|ECONNREFUSED|hub|offline|fetch failed/i.test(String(chat.error))
            ? "Hub offline. Grounded tools still work across desks: Sync, Trust, board focus. Empty ≠ $0."
            : "HAL unavailable: " + chat.error;
        }
      } catch (err) {
        reply = "Hub unreachable. Board-actions still live on every desk. " + err.message;
      }
      if (!reply) reply = "No conversational reply — board path only.";
    }
    const receipt = results.length ? `\n\n[actions: ${results.join(", ")}]` : "";
    setHalPrint(reply + receipt, mode);
    document.getElementById("cmdStatus").textContent =
      `TERMINAL · ${DESKS[currentDesk].label} · ${mode === "BOARD" ? "board" : "chat"} · ${results.length} actions`;
    document.getElementById("liveDot").classList.remove("off");
  } catch (err) {
    setHalPrint("Board-actions failed: " + err.message, "ERR");
    document.getElementById("liveDot").classList.add("off");
    document.getElementById("cmdStatus").textContent = "TERMINAL · error";
    toast(err.message);
  } finally {
    busy = false;
    btn.disabled = false;
  }
}

async function fetchWidgets(page, sub) {
  const qs = sub ? `?sub=${encodeURIComponent(sub)}` : "";
  const res = await apexFetch(`${API}/widgets/${page}${qs}`);
  const data = await res.json().catch(() => ({}));
  const list = data.widgets || data.items || [];
  const map = {};
  (Array.isArray(list) ? list : []).forEach((w) => {
    if (w && w.id) map[w.id] = w;
  });
  return map;
}

function fillNote(el, w) {
  if (!el) return;
  const gate = el.querySelector('[data-role="gate"]');
  const list = el.querySelector('[data-role="list"]');
  const val = el.querySelector('[data-role="val"]');
  if (!w) {
    if (gate) gate.textContent = "Widget unavailable";
    if (val) val.textContent = "—";
    return;
  }
  if (val) {
    val.textContent = widgetStatusLabel(w);
    val.className = "val " + (w.status === "empty" ? "blocked" : w.status === "warn" ? "blocked" : "up");
  }
  if (gate) {
    gate.textContent = String(w.emptyMessage || w.message || w.hint || w.label || w.id).slice(0, 140);
  }
  if (list) {
    const bits = [];
    if (w.gapCode) bits.push(`gap ${w.gapCode}`);
    if (Array.isArray(w.priorities)) w.priorities.slice(0, 4).forEach((p) => bits.push(String(p)));
    if (Array.isArray(w.checks)) w.checks.slice(0, 4).forEach((c) => bits.push(String(c.label || c)));
    if (Array.isArray(w.pills)) {
      w.pills.slice(0, 4).forEach((p) => {
        bits.push(`${p.label}: ${p.empty || p.value == null ? "empty" : p.value}`);
      });
    }
    list.innerHTML = bits.map((b) => `<div>${escapeHtml(b)}</div>`).join("") || "<div>No detail rows</div>";
  }
}

function applyLiveToStage() {
  const desk = DESKS[currentDesk];
  (desk.panes || []).forEach((pane) => {
    const el = document.querySelector(`#stage .pane[data-pane="${pane.id}"]`);
    if (!el) return;
    const w = widgetById(pane.widgetId);
    const val = el.querySelector('[data-role="val"]');
    const gate = el.querySelector('[data-role="gate"]');

    if (pane.kind === "dual") {
      const empty = !w || w.status === "empty";
      if (val) {
        val.textContent = empty ? "GATED" : "LIVE";
        val.className = "val " + (empty ? "blocked" : "up");
      }
      if (gate) gate.textContent = empty ? String((w && (w.emptyMessage || w.hint)) || "Need periods").slice(0, 72) : "Import-backed";
      if (w && !empty) {
        const prod = Array.isArray(w.production) ? w.production.map((p) => (p && p.y != null ? p.y : p)) : [];
        const coll = Array.isArray(w.collections) ? w.collections.map((p) => (p && p.y != null ? p.y : p)) : [];
        const pEl = el.querySelector('[data-role="prod"]');
        const cEl = el.querySelector('[data-role="coll"]');
        if (pEl && prod.length) pEl.setAttribute("points", pointsToPolyline(prod, 640, 160));
        if (cEl && coll.length) cEl.setAttribute("points", pointsToPolyline(coll, 640, 160));
      }
      return;
    }

    if (pane.kind === "status-bars" || pane.kind === "status-bars-alt") {
      const empty = !w || w.status === "empty";
      if (val) {
        val.textContent = empty ? "GATED" : "LIVE";
        val.className = "val " + (empty ? "blocked" : "up");
      }
      if (gate) gate.textContent = String((w && (w.emptyMessage || w.gapCode || w.hint)) || "…").slice(0, 64);
      mkBars(el.querySelector('[data-role="bars"]'), empty ? [null, null, null, null, null, null, null] : [0.7, 0.8, 0.65, 0.75, 0.7, 0.85, 0.6], pane.kind === "status-bars-alt");
      return;
    }

    if (pane.kind === "claims-bars") {
      const svg = el.querySelector('[data-role="claims"]');
      const cols = w && Array.isArray(w.columns) ? w.columns : [];
      const counts = cols.map((c) => Number(c.count || 0));
      const gated = !w || w.status === "empty" || !cols.length || counts.every((n) => n === 0);
      if (val) {
        val.textContent = gated ? "GATED 0" : `n=${counts.reduce((a, b) => a + b, 0)}`;
        val.className = "val " + (gated ? "blocked" : "up");
      }
      if (!svg) return;
      if (!cols.length) {
        svg.innerHTML = `<text x="20" y="60" fill="#f5a623" font-size="11" font-family="ui-monospace, monospace">${escapeHtml(
          String((w && w.emptyMessage) || "No claims aging")
        ).slice(0, 48)}</text>`;
        return;
      }
      const max = Math.max(1, ...counts);
      const colors = { cyan: "#4da3ff", amber: "#f5a623", rose: "#ff5c5c" };
      svg.innerHTML = cols
        .map((c, i) => {
          const h = gated ? 10 : Math.max(8, Math.round((Number(c.count || 0) / max) * 90));
          const x = 24 + i * 50;
          const y = 110 - h;
          return `<rect x="${x}" y="${y}" width="36" height="${h}" fill="${colors[c.tone] || "#4da3ff"}" opacity="${gated ? 0.35 : 1}"/>
            <text x="${x}" y="14" fill="#8b97a8" font-size="9" font-family="ui-monospace, monospace">${escapeHtml(String(c.label || c.bucket).slice(0, 6))}</text>
            <text x="${x + 10}" y="${y - 4}" fill="#8b97a8" font-size="9" font-family="ui-monospace, monospace">${Number(c.count || 0)}</text>`;
        })
        .join("");
      return;
    }

    if (pane.kind === "ar-donut") {
      const empty = !w || w.status === "empty" || !Array.isArray(w.series) || !w.series.length;
      if (val) {
        val.textContent = empty ? "GATED" : "LIVE";
        val.className = "val " + (empty ? "blocked" : "up");
      }
      if (gate) gate.textContent = empty ? String((w && w.emptyMessage) || "blocked").slice(0, 24) : "import-backed";
      return;
    }

    if (pane.kind === "heat") {
      const heat = el.querySelector('[data-role="heat"]');
      const priorities = w && Array.isArray(w.priorities) ? w.priorities : [];
      if (val) val.textContent = priorities.length ? `${priorities.length} pri` : widgetStatusLabel(w);
      if (heat) {
        heat.innerHTML = Array.from({ length: 18 }, (_, i) => {
          const p = priorities[i];
          const cls = p ? (/missing|gap|stale|NO_PERIOD|error/i.test(String(p)) ? "r2" : "g2") : i % 5 === 0 ? "r1" : "g1";
          const title = p ? ` title="${escapeHtml(String(p))}"` : "";
          return `<b class="${cls}"${title}>${i + 1}</b>`;
        }).join("");
      }
      return;
    }

    if (pane.kind === "tape") {
      const body = el.querySelector('[data-role="tape"]');
      const lines = w && Array.isArray(w.lines) ? w.lines : liveBundle.consoleLines || [];
      if (val) val.textContent = `${Math.min(lines.length, 8)} rows`;
      if (body) {
        body.innerHTML = lines
          .slice(0, 8)
          .map((line) => {
            const lvl = String(line.level || "info").toLowerCase();
            const cls = lvl === "error" ? "dn" : lvl === "warn" || lvl === "warning" ? "blocked" : "flat";
            const lab = lvl === "error" ? "ERR" : lvl === "warn" || lvl === "warning" ? "WARN" : "INFO";
            return `<tr><td>${escapeHtml(String(line.source || "sys").slice(0, 10))}</td><td>${escapeHtml(
              String(line.message || "").slice(0, 48)
            )}</td><td class="${cls}">${lab}</td></tr>`;
          })
          .join("") || `<tr><td>—</td><td>No lines</td><td class="flat">SYS</td></tr>`;
      }
      return;
    }

    if (pane.kind === "movers") {
      const body = el.querySelector('[data-role="movers"]');
      const huddle = widgetById("om-daily-huddle");
      const sync = widgetById("hal-sync-cta");
      const rows = [];
      ((huddle && huddle.priorities) || []).slice(0, 3).forEach((p, i) => {
        rows.push({
          s: String(p).slice(0, 28),
          d: `#${i + 1}`,
          st: "Huddle",
          cls: /missing|gap|stale|NO_PERIOD/i.test(String(p)) ? "dn" : "flat",
        });
      });
      if (sync) rows.push({ s: "Sync CTA", d: sync.syncImports ? "RUN" : "—", st: widgetStatusLabel(sync), cls: "blocked" });
      if (w) rows.push({ s: "Insight", d: w.status === "empty" ? "none" : "ready", st: widgetStatusLabel(w), cls: "flat" });
      if (val) val.textContent = "LIVE";
      if (body) {
        body.innerHTML = rows
          .slice(0, 5)
          .map(
            (r) =>
              `<tr><td>${escapeHtml(r.s)}</td><td class="${r.cls}">${escapeHtml(r.d)}</td><td>${escapeHtml(r.st)}</td></tr>`
          )
          .join("");
      }
      return;
    }

    if (pane.kind === "vitals") {
      const box = el.querySelector('[data-role="vitals"]');
      const pills = w && Array.isArray(w.pills) ? w.pills : [];
      if (val) val.textContent = pills.length ? `${pills.length} kpi` : widgetStatusLabel(w);
      if (box) {
        box.innerHTML = pills
          .slice(0, 6)
          .map((p) => {
            const empty = p.empty || p.value == null;
            return `<div class="kpi"><div class="l">${escapeHtml(p.label || p.id)}</div><div class="n ${
              empty ? "blocked" : "up"
            }">${empty ? "—" : escapeHtml(String(p.value))}</div><div class="s">${empty ? "empty ≠ $0" : "import"}</div></div>`;
          })
          .join("") || `<div class="note">${escapeHtml((w && w.emptyMessage) || "No vitals")}</div>`;
      }
      return;
    }

    if (pane.kind === "trust-health") {
      const summary = liveBundle.summary || {};
      const conn = el.querySelector('[data-role="conn"]');
      const miss = el.querySelector('[data-role="miss"]');
      if (conn) conn.textContent = `${summary.connected || 0}/${summary.total || 19}`;
      if (miss) miss.textContent = String(summary.missing || 0);
      if (val) val.textContent = w && w.value != null ? String(w.value) : `${summary.connected || 0}/${summary.total || 19}`;
      if (gate) gate.textContent = String((w && w.hint) || "Import summary is staff-facing truth").slice(0, 120);
      return;
    }

    fillNote(el, w);
  });
}

function renderTicker(summary) {
  const s = summary || {};
  const connected = Number(s.connected || 0);
  const missing = Number(s.missing || 0);
  const total = Number(s.total || 19);
  const degraded = missing > 0;
  const items = [
    ["DESK", DESKS[currentDesk].label, "flat"],
    ["IMP", `${connected}/${total}`, degraded ? "dn" : "up"],
    ["SD", widgetStatusLabel(widgetById("softdent-collections-gap")), "blocked"],
    ["QB", widgetStatusLabel(widgetById("qb-ap-aging")), "blocked"],
    ["CLM", widgetStatusLabel(widgetById("claims-aging-exposure")), "flat"],
    ["AR", widgetStatusLabel(widgetById("ar-aging-chart")), "blocked"],
    ["SYNC", "READY", "up"],
    ["HAL", "READY", "flat"],
  ];
  document.getElementById("ticker").innerHTML = items
    .map(([k, v, c]) => `<span><b>${k}</b><span class="${c}">${escapeHtml(String(v))}</span></span>`)
    .join("");
}

async function loadLiveWidgets() {
  const [financial, softdent, claims, ar, qb, om, hal, logs] = await Promise.all([
    fetchWidgets("financial"),
    fetchWidgets("softdent"),
    fetchWidgets("claims"),
    fetchWidgets("ar"),
    fetchWidgets("quickbooks"),
    fetchWidgets("office-manager"),
    fetchWidgets("hal"),
    fetchWidgets("hal", "system-logs"),
  ]);
  const byId = Object.assign({}, financial, softdent, claims, ar, qb, om, hal, logs);
  const consoleW = logs["hal-sys-console"];
  liveBundle = {
    byId,
    consoleLines: consoleW && Array.isArray(consoleW.lines) ? consoleW.lines : [],
    summary: liveBundle.summary || {},
  };
  applyLiveToStage();
}

async function refreshStatus() {
  const res = await apexFetch(`${API}/hal/status`);
  const data = await res.json().catch(() => ({}));
  lastStatus = data;
  const metrics = (data && data.metrics) || {};
  const summary = (data.readiness && data.readiness.summary) || data.summary || {};
  const connected = Number(summary.connected != null ? summary.connected : metrics.importConnected || 0);
  const missing = Number(summary.missing != null ? summary.missing : metrics.importMissing || 0);
  const total = Number(summary.total != null ? summary.total : metrics.importTotal || 19);
  const degraded = missing > 0 || /missing import/i.test(String(data.suggestion || ""));
  liveBundle.summary = { connected, missing, total, degraded };

  document.getElementById("kpiImp").textContent = `${connected}/${total}`;
  document.getElementById("kpiImp").className = "n " + (degraded ? "blocked" : "up");
  document.getElementById("kpiImpS").textContent = degraded ? `${missing} missing` : "connected";
  document.getElementById("postureVal").textContent = degraded ? "DEGRADED" : "READY";
  document.getElementById("postureVal").className = "val " + (degraded ? "dn" : "up");
  document.getElementById("halTools").textContent = "Tools OK";
  document.getElementById("halTools").className = "up";
  const orchOn = !!(data.orchestrator && data.orchestrator.enabled);
  document.getElementById("halHubLbl").textContent = orchOn ? "Orch ON" : "Hub —";
  document.getElementById("liveDot").classList.remove("off");
  renderTicker(liveBundle.summary);

  if (!document.getElementById("halPrint").dataset.seeded) {
    setHalPrint(
      `Multi-desk terminal online · page ${DESKS[currentDesk].title}. Click panes for board focus. Type "go to claims" / "go to trust". Empty ≠ $0.` +
        (data.suggestion ? `\n\n${data.suggestion}` : ""),
      "READY"
    );
    document.getElementById("halPrint").dataset.seeded = "1";
  }
}

async function refreshAll() {
  await refreshStatus();
  try {
    await loadLiveWidgets();
  } catch (err) {
    toast("Widget load: " + err.message);
  }
  renderTicker(liveBundle.summary || {});
}

function tickClock() {
  const d = new Date();
  document.getElementById("clock").textContent =
    d.toLocaleDateString("en-GB", { day: "2-digit", month: "short", year: "numeric" }).toUpperCase() +
    " · " +
    d.toLocaleTimeString("en-GB", { hour12: false }) +
    " ET";
}

function wireChrome() {
  document.querySelectorAll("#tabs [data-desk], #nav [data-desk]").forEach((btn) => {
    btn.addEventListener("click", () => setDesk(btn.getAttribute("data-desk")));
  });
  window.addEventListener("popstate", () => setDesk(parseDeskFromLocation(), false));
  window.addEventListener("hashchange", () => setDesk(parseDeskFromLocation(), false));

  document.getElementById("cmd").addEventListener("submit", (e) => {
    e.preventDefault();
    const input = document.getElementById("q");
    let q = input.value.trim();
    if (!q) return;
    const focused = document.querySelector("#stage .pane.is-focus, .side .pane.is-focus");
    const ctx = focused
      ? {
          widgetId: focused.getAttribute("data-widget"),
          page: focused.getAttribute("data-page") || "hal",
          deskPane: focused.dataset.pane,
        }
      : { page: "hal" };
    if (focused && /^(explain|what is this|help)$/i.test(q)) q = "explain this widget";
    runHal(q, ctx);
  });

  tickClock();
  setInterval(tickClock, 1000);
}

async function boot() {
  try {
    wireChrome();
    await ensureSession();
    setDesk(parseDeskFromLocation(), false);
    if (!location.hash) history.replaceState({ desk: currentDesk }, "", `#/${currentDesk}`);
    await refreshAll();
    setInterval(() => refreshAll().catch(() => {}), 60000);
  } catch (err) {
    document.getElementById("liveDot").classList.add("off");
    setHalPrint("Terminal boot failed: " + (err && err.message ? err.message : err), "ERR");
    document.getElementById("cmdStatus").textContent = "TERMINAL · boot failed";
  }
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", boot);
} else {
  boot();
}
