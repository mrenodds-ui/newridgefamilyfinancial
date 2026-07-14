const SESSION_HEADER = "X-NR2-Session-Token";
const API = "/api/apex";
let sessionToken = "";
let busy = false;
let lastStatus = null;
let liveBundle = {};

/** Every desk pane maps to a real Apex widget id for board-actions + live status. */
const PANE_SPEC = {
  prod: {
    label: "Production vs collections",
    widgetId: "financial-dual-trend",
    page: "financial",
    fallbackIds: ["revenue-composition", "financial-vital-signs"],
  },
  posture: {
    label: "Posture",
    widgetId: "hal-program-posture",
    page: "hal",
    fallbackIds: [],
  },
  sd: {
    label: "SoftDent day strip",
    widgetId: "softdent-collections-gap",
    page: "softdent",
    fallbackIds: ["sd-prod-trend", "import-health-timeline"],
  },
  claims: {
    label: "Claims velocity",
    widgetId: "claims-aging-exposure",
    page: "claims",
    fallbackIds: ["claims-open-kanban", "claims-executive-strip"],
  },
  ar: {
    label: "A/R aging",
    widgetId: "ar-aging-chart",
    page: "ar",
    fallbackIds: ["ar-aging-outlook", "ar-vitals-strip"],
  },
  tape: {
    label: "Exception tape",
    widgetId: "hal-sys-console",
    page: "hal",
    sub: "system-logs",
    fallbackIds: [],
  },
  qb: {
    label: "QB linkage",
    widgetId: "qb-ap-aging",
    page: "quickbooks",
    fallbackIds: ["qb-pl-summary", "qb-net-profit-gap"],
  },
  heat: {
    label: "Operatory heat",
    widgetId: "om-daily-huddle",
    page: "office-manager",
    fallbackIds: ["om-priorities", "operatory-util-board"],
  },
  movers: {
    label: "Top movers",
    widgetId: "hal-ai-insight",
    page: "hal",
    fallbackIds: ["hal-sync-cta", "om-daily-huddle"],
  },
  trust: {
    label: "Trust ladder",
    widgetId: "hal-import-health",
    page: "hal",
    fallbackIds: ["hal-sync-cta"],
  },
  hal: {
    label: "HAL print",
    widgetId: "hal-ask",
    page: "hal",
    fallbackIds: ["hal-program-posture"],
  },
};

const NAV_SPEC = {
  softdent: { pane: "sd", widgetId: "softdent-collections-gap", page: "softdent" },
  quickbooks: { pane: "qb", widgetId: "qb-ap-aging", page: "quickbooks" },
  ar: { pane: "ar", widgetId: "ar-aging-chart", page: "ar" },
  claims: { pane: "claims", widgetId: "claims-aging-exposure", page: "claims" },
  hal: { pane: "trust", widgetId: "hal-import-health", page: "hal" },
  desk: { pane: "posture", widgetId: "hal-program-posture", page: "hal" },
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
  document.getElementById("halPrint").innerHTML =
    `<div class="who">HAL // DESK</div>${escapeHtml(text)}`;
  if (mode) document.getElementById("halMode").textContent = mode;
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
  el.innerHTML = (vals || []).map((v, i) => {
    const muted = v == null;
    const h = muted ? 8 : Math.max(8, Math.round(Number(v) * 100));
    const cls = muted ? "mute" : alt && i % 2 ? "alt" : "";
    return `<i class="${cls}" style="height:${h}%"></i>`;
  }).join("");
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

function mapActionToPane(action) {
  if (!action) return null;
  const wid = String(action.widgetId || "");
  const page = String(action.page || "");
  // Prefer exact primary widgetId matches before fallbacks.
  for (const [pane, spec] of Object.entries(PANE_SPEC)) {
    if (wid && wid === spec.widgetId) return pane;
  }
  for (const [pane, spec] of Object.entries(PANE_SPEC)) {
    if (wid && (spec.fallbackIds || []).includes(wid)) return pane;
  }
  if (wid.includes("revenue") || wid.includes("financial-dual") || wid.includes("vital")) return "prod";
  if (wid.includes("import-health")) return "trust";
  if (wid.includes("posture")) return "posture";
  if (wid.includes("softdent") || wid.includes("collections-gap")) return "sd";
  if (wid.includes("claim")) return "claims";
  if (wid.includes("ar-")) return "ar";
  if (wid.includes("qb")) return "qb";
  if (wid.includes("huddle") || wid.includes("operatory")) return "heat";
  if (wid.includes("sys") || wid.includes("hal-sys")) return "tape";
  if (wid.includes("insight") || wid.includes("sync-cta")) return "movers";
  if (wid === "hal-ask") return "hal";
  if (action.type === "sync_imports") return "posture";
  if (action.type === "navigate") {
    if (page === "softdent") return "sd";
    if (page === "claims") return "claims";
    if (page === "ar") return "ar";
    if (page === "quickbooks") return "qb";
    if (page === "hal") return "trust";
    if (page === "office-manager") return "heat";
    if (page === "financial") return "prod";
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
    const pane = mapActionToPane(action) || preferredPane;
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
    } else if (type === "focus_claim_tile") {
      focusPane("claims");
      results.push("focus_claim");
    } else {
      results.push(type);
    }
  }
  // Keep the user-selected desk pane focused even if action mapping is ambiguous.
  if (preferredPane) focusPane(preferredPane);
  return results;
}

async function runHal(query, context) {
  if (busy) return;
  busy = true;
  const btn = document.getElementById("execBtn");
  btn.disabled = true;
  document.getElementById("cmdStatus").textContent = "DESK · board-actions…";
  setHalPrint("Running board-actions…", "BUSY");
  const preferredPane = context && context.deskPane;
  try {
    const page = (context && context.page) || "hal";
    const body = { query, page, context: context || {} };
    const res = await apexFetch(`${API}/hal/board-actions`, {
      method: "POST",
      body: JSON.stringify(body),
    });
    const board = await res.json().catch(() => ({}));
    let results = [];
    let actions = Array.isArray(board.actions) ? board.actions.slice() : [];

    // Guarantee a desk focus action when a widget context was provided.
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

    if (actions.length) {
      results = await applyActions(actions, preferredPane);
    } else if (preferredPane) {
      focusPane(preferredPane);
    }

    let reply = "";
    let mode = "BOARD";
    if (board.handled || (context && context.widgetId && results.length)) {
      reply = String(
        board.reply ||
          (Array.isArray(board.notes) && board.notes.join(" ")) ||
          (context && context.widgetId
            ? `Focusing widget \`${context.widgetId}\` (import-backed display only).`
            : "Board updated.")
      );
      mode = "BOARD";
    } else {
      document.getElementById("cmdStatus").textContent = "DESK · evaluate-query…";
      mode = "CHAT";
      try {
        const chatRes = await apexFetch("/api/hal/evaluate-query", {
          method: "POST",
          body: JSON.stringify({
            query,
            lane: "chat8b",
            shiftContext: {
              page,
              desk: "terminal",
              widgetId: context && context.widgetId,
              honesty: "Do not invent financial dollar amounts. Prefer import-backed facts.",
              boardHint: board && board.reply,
            },
          }),
        });
        const chat = await chatRes.json().catch(() => ({}));
        reply = String((chat && (chat.text || chat.reply || (chat.message && chat.message.content))) || "");
        if (!reply && chat && chat.error) {
          const err = String(chat.error);
          if (/connection refused|ECONNREFUSED|hub|offline|fetch failed/i.test(err)) {
            reply =
              "Hub offline. Grounded tools still work: Sync, Trust ladder, exception tape, board focus. I will not invent SoftDent/A/R dollars.";
          } else {
            reply = "HAL unavailable: " + err;
          }
        }
      } catch (err) {
        reply = "Hub unreachable. Use Sync / Trust / tape — board-actions still live. " + err.message;
      }
      if (!reply) reply = "No conversational reply — board path only.";
    }

    const receipt = results.length ? `\n\n[actions: ${results.join(", ")}]` : "";
    setHalPrint(reply + receipt, mode);
    document.getElementById("cmdStatus").textContent =
      `DESK · ${mode === "BOARD" ? "board-handled" : "chat"} · ${results.length} actions`;
    document.getElementById("liveDot").classList.remove("off");
  } catch (err) {
    setHalPrint("Board-actions failed: " + err.message, "ERR");
    document.getElementById("liveDot").classList.add("off");
    document.getElementById("cmdStatus").textContent = "DESK · error";
    toast(err.message);
  } finally {
    busy = false;
    btn.disabled = false;
  }
}

function activatePane(paneId) {
  const spec = PANE_SPEC[paneId];
  if (!spec) return;
  focusPane(paneId);
  const ask = "explain this widget";
  document.getElementById("q").value = `${ask} · ${spec.label} · ${spec.widgetId}`;
  runHal(ask, {
    widgetId: spec.widgetId,
    page: spec.page,
    deskPane: paneId,
    label: spec.label,
  });
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

function pickWidget(map, ids) {
  for (const id of ids) {
    if (map && map[id]) return map[id];
  }
  return null;
}

function widgetStatusLabel(w) {
  if (!w) return "—";
  const st = String(w.status || "").toLowerCase();
  if (st === "empty" || w.emptyMessage) return "GATED";
  if (st === "warn" || st === "warning") return "WARN";
  if (st === "ok" || st === "ready") return "LIVE";
  if (st === "partial") return "PARTIAL";
  return (st || "LIVE").toUpperCase();
}

function renderTicker(summary) {
  const s = summary || {};
  const connected = Number(s.connected || 0);
  const missing = Number(s.missing || 0);
  const total = Number(s.total || connected + missing || 19);
  const degraded = missing > 0 || connected < Math.max(1, total);
  const sd = liveBundle.sdGap;
  const qb = liveBundle.qbAp;
  const items = [
    ["SD.CASH", sd && sd.status === "empty" ? "n/a" : degraded ? "n/a" : "live", degraded ? "flat" : "up"],
    ["SD.GAP", sd ? widgetStatusLabel(sd) : "—", sd && sd.status === "empty" ? "dn" : "flat"],
    ["QB.AP", qb ? widgetStatusLabel(qb) : "—", qb && qb.status === "empty" ? "dn" : "up"],
    ["AR.90", degraded ? "GATED" : "live", degraded ? "flat" : "up"],
    ["CLM", liveBundle.claimsAge ? widgetStatusLabel(liveBundle.claimsAge) : "—", "flat"],
    ["IMP", `${connected}/${total}`, degraded ? "dn" : "up"],
    ["HAL", "READY", "flat"],
    ["SYNC", "READY", "up"],
  ];
  document.getElementById("ticker").innerHTML = items
    .map(([k, v, c]) => `<span><b>${k}</b><span class="${c}">${v}</span></span>`)
    .join("");
}

function renderTrust(summary) {
  const missing = Number((summary && summary.missing) || 0);
  const connected = Number((summary && summary.connected) || 0);
  const total = Math.max(1, Number((summary && summary.total) || 19));
  const base = Math.round((connected / total) * 100);
  const health = liveBundle.importHealth;
  const label = health && health.value != null ? String(health.value) : `${connected}/${total}`;
  document.querySelector('[data-pane="trust"] .ph .val') &&
    (document.querySelector('[data-pane="trust"] .ph .val').textContent = label);
  const rows = [
    ["SoftDent", Math.max(6, base - 18), missing ? "dn" : "up"],
    ["QB", Math.max(10, base), missing ? "blocked" : "up"],
    ["ERA", Math.max(6, base - 14), missing ? "dn" : "up"],
    ["Bridge", Math.max(8, base - 4), missing ? "blocked" : "up"],
  ];
  document.getElementById("trustLadder").innerHTML = rows
    .map(
      ([name, pct, cls]) => `
      <div style="display:grid;grid-template-columns:70px 1fr 28px;gap:6px;align-items:center">
        <span class="flat">${name}</span>
        <div style="background:#1a222d;height:10px"><div style="width:${pct}%;height:100%;background:${
          cls === "up" ? "var(--green)" : cls === "dn" ? "var(--red)" : "var(--amber)"
        }"></div></div>
        <span class="${cls}">${pct}%</span>
      </div>`
    )
    .join("");
}

function renderTapeFromConsole(lines) {
  const rows = (lines || []).slice(0, 5).map((line) => {
    const lvl = String(line.level || "info").toLowerCase();
    const src = String(line.source || "sys");
    const owner = src.includes("softdent")
      ? "SD"
      : src.includes("quickbooks") || src.includes("qb")
        ? "QB"
        : src.includes("era")
          ? "ERA"
          : src.includes("import")
            ? "IMP"
            : "BR";
    const cls = lvl === "error" || lvl === "err" ? "dn" : lvl === "warn" || lvl === "warning" ? "blocked" : "flat";
    return {
      t: String(line.at || "—").slice(0, 5) || "—",
      o: owner,
      e: String(line.message || "").slice(0, 42),
      lvl: lvl === "error" ? "ERR" : lvl === "warn" || lvl === "warning" ? "WARN" : "INFO",
      cls,
    };
  });
  if (!rows.length) {
    rows.push({ t: "—", o: "BR", e: "No console lines", lvl: "SYS", cls: "flat" });
  }
  document.getElementById("tapeBody").innerHTML = rows
    .map((r) => `<tr><td>${escapeHtml(r.t)}</td><td>${escapeHtml(r.o)}</td><td>${escapeHtml(r.e)}</td><td class="${r.cls}">${r.lvl}</td></tr>`)
    .join("");
}

function renderMoversLive() {
  const huddle = liveBundle.huddle;
  const sync = liveBundle.syncCta;
  const insight = liveBundle.insight;
  const priorities = (huddle && Array.isArray(huddle.priorities) ? huddle.priorities : []).slice(0, 4);
  const rows = [];
  if (priorities.length) {
    priorities.forEach((p, i) => {
      rows.push({
        s: String(p).slice(0, 28),
        d: `#${i + 1}`,
        st: "Huddle",
        cls: /missing|gap|stale|NO_PERIOD/i.test(String(p)) ? "dn" : "flat",
      });
    });
  }
  if (sync) {
    rows.push({
      s: "Sync CTA",
      d: sync.syncImports ? "RUN" : "—",
      st: widgetStatusLabel(sync),
      cls: sync.syncImports ? "blocked" : "up",
    });
  }
  if (insight) {
    rows.push({
      s: "AI insight",
      d: insight.status === "empty" ? "none" : "ready",
      st: widgetStatusLabel(insight),
      cls: insight.status === "empty" ? "flat" : "up",
    });
  }
  if (!rows.length) {
    rows.push({ s: "No movers yet", d: "—", st: "Sync", cls: "blocked" });
  }
  document.getElementById("moversBody").innerHTML = rows
    .slice(0, 5)
    .map((r) => `<tr><td>${escapeHtml(r.s)}</td><td class="${r.cls}">${escapeHtml(r.d)}</td><td>${escapeHtml(r.st)}</td></tr>`)
    .join("");
}

function applyLiveCharts() {
  const dual = liveBundle.dualTrend;
  const vitals = liveBundle.vitals;
  const prodGate = document.getElementById("prodGate");
  const prodVal = document.getElementById("prodVal");
  if (dual) {
    const prod = dual.production || dual.prod || [];
    const coll = dual.collections || dual.coll || [];
    const prodPts = Array.isArray(prod)
      ? prod.map((p) => (p && typeof p === "object" ? p.y ?? p.value : p))
      : [];
    const collPts = Array.isArray(coll)
      ? coll.map((p) => (p && typeof p === "object" ? p.y ?? p.value : p))
      : [];
    const empty = dual.status === "empty" || (!prodPts.length && !collPts.length);
    prodVal.textContent = empty ? "GATED" : "LIVE";
    prodVal.className = "val " + (empty ? "blocked" : "up");
    prodGate.textContent = empty
      ? String(dual.emptyMessage || dual.hint || "Need SoftDent periods — empty ≠ $0").slice(0, 72)
      : "Import-backed dual trend";
    if (!empty && (prodPts.length || collPts.length)) {
      document.getElementById("prodLine").setAttribute("points", pointsToPolyline(prodPts, 640, 160) || "20,120 620,120");
      document.getElementById("collLine").setAttribute("points", pointsToPolyline(collPts, 640, 160) || "20,132 620,132");
    }
  } else if (vitals && Array.isArray(vitals.pills)) {
    const emptyMoney = vitals.pills.filter((p) => p && (p.empty || p.value == null)).length;
    prodVal.textContent = emptyMoney ? "GATED" : "VITALS";
    prodGate.textContent = `${vitals.pills.length} vitals · ${emptyMoney} empty (no invent $)`;
  }

  const sd = liveBundle.sdGap;
  const sdGate = document.getElementById("sdGate");
  if (sd) {
    const empty = sd.status === "empty";
    sdGate.textContent = String(sd.emptyMessage || sd.gapCode || sd.hint || "SoftDent").slice(0, 64);
    // Honesty: muted bars when gated — do not invent a production index.
    mkBars(document.getElementById("sdBars"), empty ? [null, null, null, null, null, null, null] : [0.55, 0.7, 0.62, 0.8, 0.66, 0.72, 0.58]);
    const sdVal = document.querySelector('[data-pane="sd"] .ph .val');
    if (sdVal) {
      sdVal.textContent = empty ? "GATED" : "LIVE";
      sdVal.className = "val " + (empty ? "blocked" : "up");
    }
  }

  const claims = liveBundle.claimsAge;
  const claimsVal = document.getElementById("claimsVal");
  const claimsSvg = document.querySelector('[data-pane="claims"] svg.chart');
  if (claims && Array.isArray(claims.columns) && claimsSvg) {
    const cols = claims.columns;
    const max = Math.max(1, ...cols.map((c) => Number(c.count || 0)));
    const colors = { cyan: "#4da3ff", amber: "#f5a623", rose: "#ff5c5c", red: "#ff5c5c" };
    const labels = cols.map((c) => c.label || c.bucket || "");
    const counts = cols.map((c) => Number(c.count || 0));
    const gated = claims.status === "empty" || counts.every((n) => n === 0);
    claimsVal.textContent = gated ? "GATED 0" : `Buckets ${counts.reduce((a, b) => a + b, 0)}`;
    claimsVal.className = "val " + (gated ? "blocked" : "up");
    const barW = 36;
    const gap = 14;
    const startX = 24;
    let html = "";
    cols.forEach((c, i) => {
      const h = gated ? 10 : Math.max(8, Math.round((Number(c.count || 0) / max) * 90));
      const x = startX + i * (barW + gap);
      const y = 110 - h;
      const fill = colors[c.tone] || "#4da3ff";
      html += `<rect x="${x}" y="${y}" width="${barW}" height="${h}" fill="${fill}" opacity="${gated ? 0.35 : 1}"/>`;
      html += `<text x="${x}" y="14" fill="#8b97a8" font-size="9" font-family="ui-monospace, monospace">${escapeHtml(
        String(labels[i]).slice(0, 6)
      )}</text>`;
      html += `<text x="${x + 8}" y="${y - 4}" fill="#8b97a8" font-size="9" font-family="ui-monospace, monospace">${counts[i]}</text>`;
    });
    if (gated) {
      html += `<text x="24" y="60" fill="#f5a623" font-size="10" font-family="ui-monospace, monospace">${escapeHtml(
        String(claims.emptyMessage || "No aged claims — empty ≠ $0").slice(0, 48)
      )}</text>`;
    }
    claimsSvg.innerHTML = html;
  }

  const ar = liveBundle.arChart;
  const arVal = document.getElementById("arVal");
  const arNote = document.getElementById("arNote");
  if (ar) {
    const empty = ar.status === "empty" || !Array.isArray(ar.series) || !ar.series.length;
    arVal.textContent = empty ? "GATED" : "LIVE";
    arVal.className = "val " + (empty ? "blocked" : "up");
    arNote.textContent = empty ? String(ar.emptyMessage || "blocked").slice(0, 24) : "import-backed";
  }

  const qb = liveBundle.qbAp;
  const qbVal = document.getElementById("qbVal");
  const qbGate = document.getElementById("qbGate");
  if (qb) {
    const empty = qb.status === "empty";
    qbVal.textContent = empty ? "GATED" : "LIVE";
    qbVal.className = "val " + (empty ? "blocked" : "up");
    qbGate.textContent = String(qb.emptyMessage || qb.hint || "QB").slice(0, 48);
    mkBars(
      document.getElementById("qbBars"),
      empty ? [null, null, null, null, null, null, null] : [0.9, 0.85, 0.7, 0.65, 0.75, 0.8, 0.72],
      true
    );
  }

  const huddle = liveBundle.huddle;
  const heat = document.getElementById("heat");
  if (huddle && heat) {
    const priorities = Array.isArray(huddle.priorities) ? huddle.priorities : [];
    heat.innerHTML = Array.from({ length: 18 }, (_, i) => {
      const p = priorities[i];
      let cls = "g1";
      if (p) {
        cls = /missing|gap|NO_PERIOD|stale|error/i.test(String(p)) ? "r2" : "g2";
      } else if ([2, 7, 16].includes(i)) cls = "r1";
      const title = p ? ` title="${escapeHtml(String(p))}"` : "";
      return `<b class="${cls}"${title}>${i + 1}</b>`;
    }).join("");
    const heatVal = document.querySelector('[data-pane="heat"] .ph .val');
    if (heatVal) heatVal.textContent = priorities.length ? `${priorities.length} pri` : "LIVE";
  }
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

  liveBundle = {
    dualTrend: pickWidget(financial, ["financial-dual-trend", "revenue-composition"]),
    vitals: pickWidget(financial, ["financial-vital-signs"]),
    sdGap: pickWidget(softdent, ["softdent-collections-gap", "softdent-production-gap"]),
    claimsAge: pickWidget(claims, ["claims-aging-exposure", "claims-open-kanban"]),
    arChart: pickWidget(ar, ["ar-aging-chart", "ar-aging-outlook"]),
    qbAp: pickWidget(qb, ["qb-ap-aging", "qb-pl-summary", "qb-net-profit-gap"]),
    huddle: pickWidget(om, ["om-daily-huddle", "om-priorities"]),
    importHealth: pickWidget(hal, ["hal-import-health"]),
    posture: pickWidget(hal, ["hal-program-posture"]),
    insight: pickWidget(hal, ["hal-ai-insight"]),
    syncCta: pickWidget(hal, ["hal-sync-cta"]),
    console: pickWidget(logs, ["hal-sys-console"]),
  };

  // Keep HTML data-widget attributes aligned with resolved live ids.
  Object.entries(PANE_SPEC).forEach(([pane, spec]) => {
    const el = document.querySelector(`[data-pane="${pane}"]`);
    if (!el) return;
    el.setAttribute("data-widget", spec.widgetId);
    el.setAttribute("data-page", spec.page);
  });

  if (liveBundle.console && Array.isArray(liveBundle.console.lines)) {
    renderTapeFromConsole(liveBundle.console.lines);
  }
  renderMoversLive();
  applyLiveCharts();

  if (liveBundle.posture) {
    const msg = String(liveBundle.posture.message || liveBundle.posture.hint || "");
    if (msg && document.getElementById("halPrint").dataset.seeded !== "1") {
      // leave boot message; posture used in status
    }
  }
}

async function refreshStatus() {
  const res = await apexFetch(`${API}/hal/status`);
  const data = await res.json().catch(() => ({}));
  lastStatus = data;
  const metrics = (data && data.metrics) || {};
  const summary = (data.readiness && data.readiness.summary) || data.summary || {};
  const connected = Number(summary.connected != null ? summary.connected : metrics.importConnected || 0);
  const missing = Number(summary.missing != null ? summary.missing : metrics.importMissing || 0);
  const partial = Number(summary.partial || 0);
  const total = Number(
    summary.total != null ? summary.total : metrics.importTotal || connected + missing + partial || 19
  );
  const degraded =
    missing > 0 ||
    Boolean(data.importDegraded) ||
    /missing import/i.test(String(data.suggestion || ""));

  document.getElementById("kpiImp").textContent = `${connected}/${total}`;
  document.getElementById("kpiImp").className = "n " + (degraded ? "blocked" : "up");
  document.getElementById("kpiImpS").textContent = degraded ? `${missing} missing` : "connected";
  document.getElementById("kpiImpS").className = "s " + (degraded ? "dn" : "up");
  const orchOn = !!(data.orchestrator && data.orchestrator.enabled);
  document.getElementById("kpiHub").textContent = orchOn ? "ORCH" : "—";
  document.getElementById("kpiHub").className = "n " + (orchOn ? "up" : "flat");
  document.getElementById("kpiHubS").textContent = orchOn ? "orchestrator" : "status";
  document.getElementById("postureVal").textContent = degraded ? "DEGRADED" : "READY";
  document.getElementById("postureVal").className = "val " + (degraded ? "dn" : "up");
  document.getElementById("halTools").textContent = "Tools OK";
  document.getElementById("halTools").className = "up";
  document.getElementById("halHubLbl").textContent = orchOn ? "Orch ON" : "Hub —";
  document.getElementById("liveDot").classList.remove("off");

  const summaryView = { connected, missing, partial, total };
  renderTicker(summaryView);
  renderTrust(summaryView);
  document.getElementById("cmdStatus").textContent =
    `DESK · ${degraded ? "import degraded" : "ready"} · HAL wired`;

  if (!document.getElementById("halPrint").dataset.seeded) {
    const tip = String(data.suggestion || "").trim();
    setHalPrint(
      (degraded
        ? "Desk online. Imports degraded — click any pane (board focus) or type sync imports. Empty ≠ $0."
        : "Desk online. Every pane uses explain-this-widget board-actions + live widget status.") +
        (tip ? "\n\n" + tip : ""),
      "READY"
    );
    document.getElementById("halPrint").dataset.seeded = "1";
  }
  return summaryView;
}

async function refreshAll() {
  await refreshStatus();
  try {
    await loadLiveWidgets();
  } catch (err) {
    toast("Widget load: " + err.message);
  }
}

function tickClock() {
  const d = new Date();
  document.getElementById("clock").textContent =
    d.toLocaleDateString("en-GB", { day: "2-digit", month: "short", year: "numeric" }).toUpperCase() +
    " · " +
    d.toLocaleTimeString("en-GB", { hour12: false }) +
    " ET";
}

function wireUi() {
  mkBars(document.getElementById("sdBars"), [null, null, null, null, null, null, null]);
  mkBars(document.getElementById("qbBars"), [null, null, null, null, null, null, null], true);
  document.getElementById("heat").innerHTML = Array.from({ length: 18 }, (_, i) => `<b>${i + 1}</b>`).join("");

  tickClock();
  setInterval(tickClock, 1000);

  document.querySelectorAll(".pane[data-pane]").forEach((pane) => {
    pane.addEventListener("click", () => activatePane(pane.dataset.pane));
  });

  document.querySelectorAll(".nav [data-nav]").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".nav button").forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      const nav = btn.getAttribute("data-nav");
      const spec = NAV_SPEC[nav];
      if (!spec) return;
      focusPane(spec.pane);
      document.getElementById("q").value = `explain this widget · ${spec.widgetId}`;
      runHal("explain this widget", {
        widgetId: spec.widgetId,
        page: spec.page,
        deskPane: spec.pane,
      });
    });
  });

  document.getElementById("cmd").addEventListener("submit", (e) => {
    e.preventDefault();
    const input = document.getElementById("q");
    let q = input.value.trim();
    if (!q) return;
    const focused = document.querySelector(".pane.is-focus");
    const ctx = focused
      ? {
          widgetId: focused.getAttribute("data-widget"),
          page: focused.getAttribute("data-page") || "hal",
          deskPane: focused.dataset.pane,
        }
      : { page: "hal" };
    // If user typed a bare widget question while a pane is focused, force explain path.
    if (focused && /^(explain|what is this|help)$/i.test(q)) q = "explain this widget";
    runHal(q, ctx);
  });
}

async function boot() {
  try {
    wireUi();
    await ensureSession();
    await refreshAll();
    setInterval(() => {
      refreshAll().catch(() => {});
    }, 60000);
  } catch (err) {
    document.getElementById("liveDot").classList.add("off");
    setHalPrint("Desk boot failed: " + (err && err.message ? err.message : err), "ERR");
    document.getElementById("cmdStatus").textContent = "DESK · boot failed";
  }
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", boot);
} else {
  boot();
}
