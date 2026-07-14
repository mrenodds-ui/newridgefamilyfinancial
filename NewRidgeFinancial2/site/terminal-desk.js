    const SESSION_HEADER = "X-NR2-Session-Token";
    const API = "/api/apex";
    let sessionToken = "";
    let busy = false;
    let lastStatus = null;

    const PANES = {
      prod: { label: "Production vs collections" },
      posture: { label: "Posture" },
      sd: { label: "SoftDent day strip" },
      claims: { label: "Claims velocity" },
      ar: { label: "A/R aging" },
      tape: { label: "Exception tape" },
      qb: { label: "QB linkage" },
      heat: { label: "Operatory heat" },
      movers: { label: "Top movers" },
      trust: { label: "Trust ladder" },
      hal: { label: "HAL print" },
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

    function mkBars(el, vals, alt) {
      el.innerHTML = vals.map((v, i) => {
        const muted = v == null;
        const h = muted ? 8 : Math.max(8, Math.round(v * 100));
        const cls = muted ? "mute" : alt && i % 2 ? "alt" : "";
        return `<i class="${cls}" style="height:${h}%"></i>`;
      }).join("");
    }

    function setHalPrint(text, mode) {
      document.getElementById("halPrint").innerHTML =
        `<div class="who">HAL // DESK</div>${escapeHtml(text)}`;
      if (mode) document.getElementById("halMode").textContent = mode;
    }

    function escapeHtml(s) {
      return String(s || "")
        .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
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

    function mapActionToPane(action) {
      if (!action) return null;
      const wid = String(action.widgetId || "");
      const page = String(action.page || "");
      if (wid.includes("revenue") || wid.includes("financial")) return "prod";
      if (wid.includes("import-health") || wid === "hal-import-health") return "trust";
      if (wid.includes("posture") || wid === "hal-program-posture") return "posture";
      if (wid.includes("softdent") || wid.includes("sd-") || wid.includes("collections-gap")) return "sd";
      if (wid.includes("claim") || page === "claims") return "claims";
      if (wid.includes("ar-") || page === "ar") return "ar";
      if (wid.includes("qb") || page === "quickbooks") return "qb";
      if (wid.includes("huddle") || page === "office-manager") return "heat";
      if (wid.includes("sys") || wid.includes("hal-sys")) return "tape";
      if (wid.includes("insight")) return "movers";
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

    async function applyActions(actions) {
      const list = Array.isArray(actions) ? actions : [];
      const results = [];
      for (const action of list) {
        if (!action || !action.type) continue;
        const type = String(action.type);
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
            await refreshStatus();
          } catch (err) {
            results.push("sync_err");
            toast("Sync error: " + err.message);
          }
        } else if (type === "focus_widget" || type === "highlight_widget" || type === "navigate" || type === "refresh_page") {
          results.push(`${type}${action.widgetId ? ":" + action.widgetId : ""}${action.page ? ":" + action.page : ""}`);
        } else if (type === "focus_claim_tile") {
          focusPane("claims");
          results.push("focus_claim");
        } else {
          results.push(type);
        }
      }
      return results;
    }

    async function runHal(query, context) {
      if (busy) return;
      busy = true;
      const btn = document.getElementById("execBtn");
      btn.disabled = true;
      document.getElementById("cmdStatus").textContent = "DESK · board-actions…";
      setHalPrint("Running board-actions…", "BUSY");
      try {
        const page = (context && context.page) || "hal";
        const body = { query, page, context: context || {} };
        const res = await apexFetch(`${API}/hal/board-actions`, {
          method: "POST",
          body: JSON.stringify(body),
        });
        const board = await res.json().catch(() => ({}));
        let results = [];
        if (Array.isArray(board.actions) && board.actions.length) {
          // Stay on terminal desk — apply focus locally; still run sync.
          const localActions = board.actions.filter(
            (a) => a && (a.type === "sync_imports" || a.type === "focus_widget" || a.type === "highlight_widget" || a.type === "navigate" || a.type === "focus_claim_tile" || a.type === "set_status_banner")
          );
          results = await applyActions(localActions);
        }
        let reply = "";
        if (board.handled) {
          reply = String(board.reply || (Array.isArray(board.notes) && board.notes.join(" ")) || "Board updated.");
        } else {
          // Conversational fallback — evaluate-query (may be hub-offline)
          document.getElementById("cmdStatus").textContent = "DESK · evaluate-query…";
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
                reply = "Hub offline. Grounded tools still work: Sync, Trust ladder, exception tape, board focus. I will not invent SoftDent/A/R dollars.";
                document.getElementById("kpiHub").textContent = "OFF";
                document.getElementById("kpiHub").className = "n dn";
              } else {
                reply = "HAL unavailable: " + err;
              }
            }
          } catch (err) {
            reply = "Hub unreachable. Use Sync / Trust / tape — board-actions still live. " + err.message;
          }
          if (!reply) reply = "No conversational reply — board path only.";
        }
        if (Array.isArray(board.notes) && board.notes.length && board.handled) {
          // reply already from board
        }
        const receipt = results.length ? `\n\n[actions: ${results.join(", ")}]` : "";
        setHalPrint(reply + receipt, board.handled ? "BOARD" : "CHAT");
        document.getElementById("cmdStatus").textContent =
          `DESK · ${board.handled ? "board-handled" : "chat"} · ${results.length} actions`;
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

    function renderTicker(summary) {
      const s = summary || {};
      const connected = Number(s.connected || 0);
      const missing = Number(s.missing || 0);
      const total = Number(s.total || connected + missing || 19);
      const degraded = missing > 0 || connected < Math.max(1, total);
      const items = [
        ["SD.CASH", degraded ? "n/a" : "live", degraded ? "flat" : "up"],
        ["SD.PROD", "idx", "up"],
        ["QB.COA", "OK", "up"],
        ["QB.PNL", missing ? "GAP" : "OK", missing ? "dn" : "up"],
        ["AR.90", degraded ? "GATED" : "live", degraded ? "flat" : "up"],
        ["CLM.DEN", "watch", "dn"],
        ["IMP", `${connected}/${total}`, degraded ? "dn" : "up"],
        ["HAL", lastStatus && lastStatus.hubOnline === false ? "GROUNDED" : "READY", "flat"],
        ["SYNC", "READY", "up"],
      ];
      document.getElementById("ticker").innerHTML = items
        .map(([k, v, c]) => `<span><b>${k}</b><span class="${c}">${v}</span></span>`)
        .join("");
    }

    function renderTrust(summary) {
      // Approximate owner bars from overall posture when per-owner detail unavailable
      const missing = Number((summary && summary.missing) || 0);
      const connected = Number((summary && summary.connected) || 0);
      const total = Math.max(1, Number((summary && summary.total) || 19));
      const base = Math.round((connected / total) * 100);
      const rows = [
        ["SoftDent", Math.max(8, base - 20), missing ? "dn" : "up"],
        ["QB", Math.max(12, base), missing ? "blocked" : "up"],
        ["ERA", Math.max(8, base - 15), missing ? "dn" : "up"],
        ["Bridge", Math.max(10, base - 5), missing ? "blocked" : "up"],
      ];
      document.getElementById("trustLadder").innerHTML = rows
        .map(([name, pct, cls]) => `
          <div style="display:grid;grid-template-columns:70px 1fr 28px;gap:6px;align-items:center">
            <span class="flat">${name}</span>
            <div style="background:#1a222d;height:10px"><div style="width:${pct}%;height:100%;background:${cls === "up" ? "var(--green)" : cls === "dn" ? "var(--red)" : "var(--amber)"}"></div></div>
            <span class="${cls}">${pct}%</span>
          </div>`)
        .join("");
    }

    function renderTape(lines) {
      const rows = lines && lines.length ? lines : [
        { t: "—", o: "BR", e: "Awaiting diagnostics", lvl: "SYS", cls: "flat" },
      ];
      document.getElementById("tapeBody").innerHTML = rows
        .slice(0, 5)
        .map((r) => `<tr><td>${r.t}</td><td>${r.o}</td><td>${r.e}</td><td class="${r.cls}">${r.lvl}</td></tr>`)
        .join("");
    }

    function renderMovers(summary) {
      const missing = Number((summary && summary.missing) || 0);
      const rows = [
        { s: "Denied claims", d: "watch", st: "Work", cls: "dn" },
        { s: "ERA lag", d: missing ? "+gap" : "ok", st: missing ? "Stale" : "OK", cls: missing ? "dn" : "up" },
        { s: "SD cash", d: "n/a", st: missing ? "Gate" : "Live", cls: "blocked" },
        { s: "Import gaps", d: String(missing), st: missing ? "Sync" : "Clear", cls: missing ? "dn" : "up" },
        { s: "Hub", d: lastStatus && lastStatus.hubOnline === false ? "OFF" : "ON", st: "Path", cls: "flat" },
      ];
      document.getElementById("moversBody").innerHTML = rows
        .map((r) => `<tr><td>${r.s}</td><td class="${r.cls}">${r.d}</td><td>${r.st}</td></tr>`)
        .join("");
    }

    async function refreshStatus() {
      try {
        const res = await apexFetch(`${API}/hal/status`);
        const data = await res.json().catch(() => ({}));
        lastStatus = data;
        const metrics = (data && data.metrics) || {};
        const summary =
          (data.readiness && data.readiness.summary) ||
          data.importSummary ||
          data.summary ||
          {};
        const connected = Number(
          summary.connected != null ? summary.connected : metrics.importConnected || 0
        );
        const missing = Number(
          summary.missing != null ? summary.missing : metrics.importMissing || 0
        );
        const partial = Number(summary.partial || 0);
        const total = Number(
          summary.total != null
            ? summary.total
            : metrics.importTotal || connected + missing + partial || 19
        );
        const degraded =
          missing > 0 ||
          Boolean(data.importDegraded) ||
          String(data.statusLabel || "").toLowerCase().includes("degraded") ||
          /missing import/i.test(String(data.suggestion || ""));
        document.getElementById("kpiImp").textContent = `${connected}/${total}`;
        document.getElementById("kpiImp").className = "n " + (degraded ? "blocked" : "up");
        document.getElementById("kpiImpS").textContent = degraded ? `${missing} missing` : "connected";
        document.getElementById("kpiImpS").className = "s " + (degraded ? "dn" : "up");
        const orchOn = !!(data.orchestrator && data.orchestrator.enabled);
        const hubLabel = orchOn ? "ORCH" : "—";
        document.getElementById("kpiHub").textContent = hubLabel;
        document.getElementById("kpiHub").className = "n " + (orchOn ? "up" : "flat");
        document.getElementById("kpiHubS").textContent = orchOn ? "orchestrator" : "status";
        document.getElementById("postureVal").textContent = degraded ? "DEGRADED" : "READY";
        document.getElementById("postureVal").className = "val " + (degraded ? "dn" : "up");
        document.getElementById("arVal").textContent = degraded ? "GATED" : "LIVE";
        document.getElementById("arNote").textContent = degraded ? "blocked" : "import-backed";
        document.getElementById("prodGate").textContent = degraded
          ? "Series honesty: gaps gated"
          : "Import-backed series";
        document.getElementById("qbGate").textContent = degraded ? "P&L may gap" : "linked";
        document.getElementById("halTools").textContent = "Tools OK";
        document.getElementById("halTools").className = "up";
        document.getElementById("halHubLbl").textContent = hubLabel === "ORCH" ? "Orch ON" : "Hub —";
        document.getElementById("halHubLbl").className = "flat";
        document.getElementById("liveDot").classList.toggle("off", false);
        const summaryView = { connected, missing, partial, total };
        renderTicker(summaryView);
        renderTrust(summaryView);
        renderMovers(summaryView);
        const now = new Date();
        const t = now.toLocaleTimeString("en-GB", { hour: "2-digit", minute: "2-digit", hour12: false });
        renderTape([
          {
            t,
            o: "IMP",
            e: degraded ? `MISSING_${missing}` : "IMPORT_OK",
            lvl: degraded ? "WARN" : "OK",
            cls: degraded ? "blocked" : "up",
          },
          {
            t,
            o: "SD",
            e: degraded ? "DAY_SHEET_RISK" : "SD_OK",
            lvl: degraded ? "ERR" : "OK",
            cls: degraded ? "dn" : "up",
          },
          { t, o: "QB", e: "COA_LINK", lvl: "SYS", cls: "flat" },
          { t, o: "HAL", e: boardModeLabel(data), lvl: "SYS", cls: "flat" },
          { t, o: "BR", e: String(data.statusLabel || "HAL").slice(0, 28), lvl: "SYS", cls: "flat" },
        ]);
        document.getElementById("cmdStatus").textContent =
          `DESK · ${degraded ? "import degraded" : "ready"} · HAL wired`;
        if (!document.getElementById("halPrint").dataset.seeded) {
          const tip = String(data.suggestion || "").trim();
          setHalPrint(
            (degraded
              ? "Desk online. Imports degraded — click any pane or type sync imports. I will not invent SoftDent/A/R dollars."
              : "Desk online. All panes call live board-actions. Click a chart or EXEC a command.") +
              (tip ? "\n\n" + tip : ""),
            "READY"
          );
          document.getElementById("halPrint").dataset.seeded = "1";
        }
      } catch (err) {
        document.getElementById("liveDot").classList.add("off");
        document.getElementById("cmdStatus").textContent = "DESK · status failed";
        setHalPrint("Could not load /api/apex/hal/status: " + err.message, "ERR");
      }
    }

    function boardModeLabel(data) {
      if (!data) return "STATUS";
      if (data.hubOnline === false) return "GROUNDED";
      return "LIVE";
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
      mkBars(document.getElementById("sdBars"), [0.55, 0.7, null, 0.62, 0.8, null, 0.45]);
      mkBars(document.getElementById("qbBars"), [0.9, 0.85, 0.4, null, 0.7, 0.75, 0.68], true);
      document.getElementById("heat").innerHTML = Array.from({ length: 18 }, (_, i) => {
        const cls = [0, 3, 8, 13].includes(i) ? "r1" : [2, 7, 16].includes(i) ? "r2" : i % 3 === 0 ? "g2" : "g1";
        return `<b class="${cls}">${i + 1}</b>`;
      }).join("");

      tickClock();
      setInterval(tickClock, 1000);

      document.querySelectorAll(".pane[data-ask]").forEach((pane) => {
        pane.addEventListener("click", () => {
          const ask = pane.getAttribute("data-ask");
          const widgetId = pane.getAttribute("data-widget");
          const page = pane.getAttribute("data-page") || "hal";
          focusPane(pane.dataset.pane);
          document.getElementById("q").value = ask;
          runHal(ask, {
            widgetId,
            page,
            deskPane: pane.dataset.pane,
            label: (PANES[pane.dataset.pane] || {}).label,
          });
        });
      });

      document.querySelectorAll(".nav [data-ask]").forEach((btn) => {
        btn.addEventListener("click", () => {
          document.querySelectorAll(".nav button").forEach((b) => b.classList.remove("active"));
          btn.classList.add("active");
          const ask = btn.getAttribute("data-ask");
          document.getElementById("q").value = ask;
          runHal(ask, { page: btn.getAttribute("data-nav") || "hal" });
        });
      });

      document.getElementById("cmd").addEventListener("submit", (e) => {
        e.preventDefault();
        const input = document.getElementById("q");
        const q = input.value.trim();
        if (!q) return;
        const focused = document.querySelector(".pane.is-focus");
        runHal(
          q,
          focused
            ? {
                widgetId: focused.getAttribute("data-widget"),
                page: focused.getAttribute("data-page") || "hal",
                deskPane: focused.dataset.pane,
              }
            : { page: "hal" }
        );
      });
    }

    async function boot() {
      try {
        wireUi();
        await ensureSession();
        await refreshStatus();
        setInterval(() => {
          refreshStatus().catch(() => {});
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
