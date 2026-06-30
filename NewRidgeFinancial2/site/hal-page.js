/**
 * HAL Command Center — client-side screen renderer (no backend).
 * Values come from hal-manager.json / hal-models.json and session audit log only.
 */
const HalPage = (function () {
  function esc(value) {
    return String(value == null ? "" : value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  function iconsApi() {
    if (typeof AppIcons !== "undefined") return AppIcons;
    if (typeof globalThis !== "undefined" && globalThis.AppIcons) return globalThis.AppIcons;
    if (typeof window !== "undefined" && window.AppIcons) return window.AppIcons;
    return null;
  }

  function uiIcon(key) {
    const api = iconsApi();
    if (!api) return "";
    const icon = api.ui(key);
    return icon ? api.wrap("hp-ico", icon) : "";
  }

  function widgetIcon(key) {
    const api = iconsApi();
    if (!api) return "";
    const icon = api.widget(key);
    return icon ? api.wrap("hp-ico hp-ico--widget", icon) : "";
  }

  function navIcon(pageId) {
    const api = iconsApi();
    if (!api) return "";
    const icon = api.nav(pageId);
    return icon ? api.wrap("hp-ico", icon) : "";
  }

  function cardIconRaw(type, key) {
    const api = iconsApi();
    if (!api) return "";
    if (type === "nav") return api.nav(key) || "";
    if (type === "widget") return api.widget(key) || "";
    if (type === "ui") return api.ui(key) || "";
    if (type === "hal") return api.hal() || "";
    return "";
  }

  function cardIcon(type, key) {
    const icon = cardIconRaw(type, key);
    const api = iconsApi();
    return icon && api ? api.wrap("hp-card__ico", icon) : "";
  }

  function promptIcon(text) {
    const q = String(text || "").toLowerCase();
    if (q.includes("sidenote")) return navIcon("sidenotes");
    if (q.includes("widget") || q.includes("fill all") || q.includes("missing data by widget")) {
      return widgetIcon("officeManagerPriorities");
    }
    if (q.includes("claim")) return navIcon("claims");
    if (q.includes("journal") || q.includes("accounting") || q.includes("reconcil")) return navIcon("documents");
    if (q.includes("import") || q.includes("pull") || q.includes("softdent") || q.includes("quickbooks")) {
      return navIcon("softdent");
    }
    if (q.includes("briefing") || q.includes("attention") || q.includes("plan for today")) {
      return navIcon("office-manager");
    }
    if (q.includes("firewall")) return uiIcon("shield");
    if (q.includes("snapshot") || q.includes("program") || q.includes("blocked") || q.includes("ready")) {
      return cardIcon("hal");
    }
    if (q.includes("task")) return widgetIcon("officeManagerTasks");
    if (q.includes("library") || q.includes("search") || q.includes("narrative")) return navIcon("narratives");
    if (q.includes("readiness") || q.includes("smoke") || q.includes("handoff")) return uiIcon("check");
    if (q.includes("monitor")) return uiIcon("monitor");
    return uiIcon("send");
  }

  function actionChip(label, attrs) {
    return `<button type="button" class="hp-action hp-action--icon" ${attrs}>${promptIcon(label)}<span class="hp-action__text">${esc(label)}</span></button>`;
  }

  function cardHead(titleHtml, drawerKey, drawerLabel, iconSvg) {
    const iconPart = iconSvg
      ? `<button type="button" class="hp-card__ico hp-card__ico--btn" data-hal-drawer="${esc(drawerKey)}" title="${esc(drawerLabel)}" aria-label="${esc(drawerLabel)}">${iconSvg}</button>`
      : "";
    return `<div class="hp-card__head"><h3>${iconPart}${titleHtml}</h3>${drawerInfoBtn(drawerKey, drawerLabel)}</div>`;
  }

  function surfNavTarget(item) {
    const target = item && item.target;
    if (target === "hal" || target === "sidenotes") return "sidenotes";
    return target || "";
  }

  function surfNavIcon(item) {
    const target = surfNavTarget(item);
    if (target === "sidenotes") return navIcon("sidenotes");
    return navIcon(item && item.target);
  }

  function drawerInfoBtn(panelKey, label) {
    return `<button type="button" class="hp-info" data-hal-drawer="${esc(panelKey)}" title="${esc(label)}" aria-label="${esc(label)}">${uiIcon("info")}<span class="hp-info__label">i</span></button>`;
  }

  function formatStatus(value) {
    return String(value || "unknown")
      .replace(/_/g, " ")
      .replace(/\b\w/g, (c) => c.toUpperCase());
  }

  function mapSourceStatus(item) {
    const sync = String(item.syncState || "").toLowerCase();
    if (sync.includes("blocked")) return "blocked";
    if (sync.includes("pending")) return "pending";
    if (item.warning) return "error";
    return "unknown";
  }

  // Live import health → source-intake status label.
  function mapLiveSourceStatus(live) {
    if (!live || !live.hasData) return "not loaded";
    if (live.status === "SUCCESS") return "current";
    if (live.status === "DEGRADED") return "needs review";
    return "not loaded";
  }

  // Widget status → friendly staff-surface state.
  function mapSurfaceState(status) {
    if (status === "SUCCESS") return "Ready";
    if (status === "DEGRADED") return "Needs review";
    if (status === "FAILED") return "No data";
    return "unknown";
  }

  function emptyNote(message) {
    return `<p class="hp-live-note">${esc(message)}</p>`;
  }

  function isSideNotesInboxLive(inbox) {
    const mon = inbox && inbox.monitor;
    if (!mon) return false;
    const checkedMs = mon.checkedAt ? Date.parse(mon.checkedAt) : NaN;
    return Number.isFinite(checkedMs) && Date.now() - checkedMs < 45000;
  }

  function stationRosterHtml(inbox) {
    const stations = (inbox && inbox.monitor && inbox.monitor.stations) || [];
    if (!stations.length) {
      return `<p class="hp-sn-empty">No workstation watchers registered yet. Run <code>run-sidenotes-helper.bat</code> on each SideNotesIM PC.</p>`;
    }
    const rows = stations
      .map((station) => {
        const live = station.live === true;
        const badge = live
          ? '<span class="hp-sn-badge hp-sn-badge--ok">LIVE</span>'
          : '<span class="hp-sn-badge hp-sn-badge--off">OFFLINE</span>';
        const flags = [
          station.announce ? "voice" : "silent",
          station.bellSuppressed ? "bell muted" : "bell on",
        ].join(" · ");
        const checked = station.checkedAt ? esc(station.checkedAt.slice(11, 19)) + " UTC" : "—";
        return `<tr>
          <td><strong>${esc(station.station || "—")}</strong></td>
          <td>${badge}</td>
          <td>${esc(flags)}</td>
          <td>${esc(checked)}</td>
        </tr>`;
      })
      .join("");
    return `<div class="hp-sn-stations-wrap">
      <table class="hp-table hp-sn-stations"><thead><tr><th>Station</th><th>Watcher</th><th>Mode</th><th>Checked</th></tr></thead><tbody>${rows}</tbody></table>
    </div>`;
  }

  function sideNotesHubFootnote(hubPath, online) {
    const hub = hubPath ? `<code>${esc(hubPath)}</code>` : "<code>NR2_SIDENOTES_HUB_DATA</code> (not configured)";
    return `<p class="hp-sn-foot">Shared hub: ${hub} · external SideNotesIM helper · routing metadata only · ${online ? "network feed active" : "waiting for watchers"}</p>`;
  }

  function liveSideNotesHtml(inbox) {
    // Live feed from the SideNotesIM watcher helper (routing metadata only —
    // message bodies are never read). `inbox` is null when the helper is offline.
    const mon = (inbox && inbox.monitor) || {};
    const online = isSideNotesInboxLive(inbox);
    const items = (inbox && Array.isArray(inbox.items) ? inbox.items : []).slice().reverse();
    const statusBadge = online
      ? '<span class="hp-sn-badge hp-sn-badge--ok">LIVE</span>'
      : '<span class="hp-sn-badge hp-sn-badge--off">OFFLINE</span>';
    const stationText =
      mon.stationCount && mon.stationCount > 1
        ? `${mon.stationCount}/${mon.totalStations || mon.stationCount} stations live`
        : `station ${mon.station || "—"}`;
    const flags = online
      ? `<span class="hp-sn-stat">${mon.announce ? "voice on" : "voice off"} · ${mon.bellSuppressed ? "bell muted" : "bell on"} · ${esc(stationText)}${mon.voiceStyle === "hal9000" ? " · HAL 9000 voice" : ""}</span>`
      : '<span class="hp-sn-stat">watcher not running</span>';
    const voiceBtn =
      `<button type="button" class="hp-sn-voice" data-hal-voice-test title="Test HAL 9000 voice" aria-label="Test HAL 9000 voice">${uiIcon("voice")} TEST VOICE</button>`;
    const checked = online && mon.checkedAt ? esc(mon.checkedAt.slice(11, 19)) + " UTC" : "—";
    let listHtml;
    if (!online) {
      listHtml =
        '<li class="hp-sn-empty">SideNotesIM watcher offline. Run <code>run-sidenotes-helper.bat</code> to let HAL announce incoming messages.</li>';
    } else if (!items.length) {
      listHtml = '<li class="hp-sn-empty">No new messages since the watcher started.</li>';
    } else {
      listHtml = items
        .slice(0, 8)
        .map((m) => {
          const kind = m.broadcast
            ? '<span class="hp-sn-tag hp-sn-tag--cast">ALL</span>'
            : '<span class="hp-sn-tag">DM</span>';
          const dot = m.unread ? '<span class="hp-sn-dot" title="unread"></span>' : "";
          const when = esc([m.date, m.time].filter(Boolean).join(" "));
          const sender = m.senderLabel || m.sender || "Unknown";
          const recipient = m.recipientLabel || m.recipient || "—";
          const source = m.sourceStation ? ` · via ${esc(m.sourceStation)}` : "";
          return `<li class="hp-sn-item hp-sn-item--live">
              ${dot}${kind}
              <span class="hp-sn-item__text"><strong>${esc(sender)}</strong> <span class="hp-sn-arrow">→ ${esc(recipient)}</span></span>
              <span class="hp-sn-item__meta">${when}${source}</span>
            </li>`;
        })
        .join("");
    }
    return `<div class="hp-sn-live">
      <div class="hp-sn-head">
        <h4>SIDENOTESIM MONITOR</h4>
        ${statusBadge}
        ${flags}
        ${voiceBtn}
        <span class="hp-sn-time">checked ${checked}</span>
      </div>
      <ul class="hp-sn-list">${listHtml}</ul>
      <p class="hp-sn-foot">HAL 9000 voice announces sender only · message text is never read</p>
    </div>`;
  }

  function sideNotesMonitorHtml(halSideNotes, halSideNoteMonitor, halSideNotesInbox, hubPath) {
    const notes = halSideNotes || [];
    const mon = halSideNoteMonitor || { activeCount: 0, openCount: 0, pinnedCount: 0, highPriorityCount: 0 };
    const active = notes.filter((n) => n.status !== "archived");
    const changeBadge = mon.hasChanges
      ? '<span class="hp-sn-badge hp-sn-badge--change">CHANGED</span>'
      : '<span class="hp-sn-badge hp-sn-badge--ok">WATCHING</span>';
    const listHtml = active.length
      ? active
          .slice(0, 5)
          .map(
            (n) => `<li class="hp-sn-item hp-sn-item--${esc(n.status)}">
              <span class="hp-sn-item__text">${esc(n.text)}</span>
              <span class="hp-sn-item__meta">${esc(n.priority)}</span>
              <button type="button" class="hp-sn-btn" data-hal-sidenote-pin="${esc(n.noteId)}" title="Pin or unpin" aria-label="Pin or unpin sidenote">${n.status === "pinned" ? uiIcon("pin") : uiIcon("unpin")}</button>
              <button type="button" class="hp-sn-btn hp-sn-btn--dim" data-hal-sidenote-archive="${esc(n.noteId)}" title="Archive" aria-label="Archive sidenote">${uiIcon("close")}</button>
            </li>`,
          )
          .join("")
      : '<li class="hp-sn-empty">No local notes — add one below or ask HAL.</li>';
    return `<div class="hp-sidenotes-monitor" data-panel="sidenotes">
      ${liveSideNotesHtml(halSideNotesInbox)}
      ${stationRosterHtml(halSideNotesInbox)}
      <div class="hp-sn-head hp-sn-head--local">
        <h4>LOCAL NOTES</h4>
        ${changeBadge}
        <span class="hp-sn-stat">${mon.activeCount || 0} active · ${mon.pinnedCount || 0} pinned</span>
      </div>
      <ul class="hp-sn-list">${listHtml}</ul>
      <form class="hp-sn-form" id="hpSideNoteForm" onsubmit="return false">
        <input class="hp-sn-input" id="hpSideNoteInput" type="text" maxlength="500" placeholder="Quick sidenote — local only, HAL monitors changes" aria-label="Add sidenote" />
        <button type="button" class="hp-sn-add" data-hal-sidenote-add>${uiIcon("add")} ADD</button>
      </form>
      <div class="hp-chips hp-sn-actions">
        <button type="button" class="hp-action hp-action--icon" data-hal-cmd="Monitor sidenotes">${uiIcon("monitor")} Monitor</button>
        <button type="button" class="hp-action hp-action--icon" data-hal-cmd="Show sidenotes">${navIcon("sidenotes")} Show notes</button>
        <button type="button" class="hp-action hp-action--icon" data-hal-drawer="sidenotes">${uiIcon("info")} Setup</button>
      </div>
      ${sideNotesHubFootnote(hubPath, isSideNotesInboxLive(halSideNotesInbox))}
    </div>`;
  }

  function sideNotesProgramCardHtml(halSideNotes, halSideNoteMonitor, halSideNotesInbox, hubPath) {
    const online = isSideNotesInboxLive(halSideNotesInbox);
    const stationCount = (halSideNotesInbox && halSideNotesInbox.monitor && halSideNotesInbox.monitor.stationCount) || 0;
    const unread = ((halSideNotesInbox && halSideNotesInbox.items) || []).filter((m) => m && m.unread).length;
    const statusChip = online
      ? `<span class="hp-sn-badge hp-sn-badge--ok">${stationCount > 1 ? stationCount + " STATIONS" : "LIVE"}</span>`
      : '<span class="hp-sn-badge hp-sn-badge--off">WATCHERS OFFLINE</span>';
    return `<section class="hp-card hp-card--sidenotes" data-panel="sidenotes" style="grid-area:sidenotes;">
      ${cardHead(
        `SIDENOTES PROGRAM <span class="hp-muted">(SIDENOTESIM · EXTERNAL)</span>`,
        "sidenotes",
        "Open SideNotes program setup and station detail",
        cardIconRaw("nav", "sidenotes"),
      )}
      <div class="hp-sn-head__tools hp-sn-head__tools--card">${statusChip}${unread ? `<span class="hp-sn-badge hp-sn-badge--change">${unread} UNREAD</span>` : ""}</div>
      <div class="hp-sidenotes-program">${sideNotesMonitorHtml(halSideNotes, halSideNoteMonitor, halSideNotesInbox, hubPath)}</div>
    </section>`;
  }

  function widgetMetricsText(widget) {
    if (typeof HalSkills !== "undefined" && HalSkills.formatWidgetMetrics) {
      return HalSkills.formatWidgetMetrics(widget);
    }
    const metrics = (widget && widget.metrics) || {};
    const pairs = Object.entries(metrics)
      .filter(([, v]) => v !== null && v !== undefined && v !== "")
      .map(([k, v]) => `${k}: ${v}`);
    return pairs.length ? pairs.join(" · ") : "No verified metrics in this snapshot.";
  }

  function widgetStatusClass(status) {
    const s = String(status || "").toUpperCase();
    if (s === "SUCCESS") return "hp-wg-badge--ok";
    if (s === "DEGRADED") return "hp-wg-badge--warn";
    return "hp-wg-badge--off";
  }

  function widgetsMonitorHtml(halWidgetFeed) {
    if (!halWidgetFeed || !halWidgetFeed.widgets) {
      return `<div class="hp-widgets" data-panel="widgets">
        <div class="hp-sn-head"><h4>MANAGER DASHBOARD WIDGETS</h4><span class="hp-sn-badge hp-sn-badge--off">NO FEED</span></div>
        <p class="hp-sn-empty">Widget feed not loaded yet. <button type="button" class="hp-action" data-hal-cmd="Show manager dashboard widgets">Load widgets</button></p>
      </div>`;
    }
    const order =
      typeof HalSkills !== "undefined" && HalSkills.WIDGET_ORDER
        ? HalSkills.WIDGET_ORDER
        : Object.keys(halWidgetFeed.widgets);
    const cards = order
      .map((key) => {
        const w = halWidgetFeed.widgets[key];
        if (!w) return "";
        const nav = w.navTarget || "";
        const widgetCmd = `Explain why the ${w.title} widget shows its current status and what data is missing`;
        return `<article class="hp-wg-card hp-wg-card--active" data-hal-widget-key="${esc(key)}" data-hal-cmd="${esc(widgetCmd)}" title="${esc(widgetCmd)}">
          <div class="hp-wg-head">
            <span class="hp-wg-ico">${widgetIcon(key)}</span>
            <strong>${esc(w.title)}</strong>
            <span class="hp-wg-badge ${widgetStatusClass(w.status)}">${esc(w.status)}</span>
          </div>
          <p class="hp-wg-metrics">${esc(widgetMetricsText(w))}</p>
          <p class="hp-wg-summary">${esc(w.summary)}</p>
          <button type="button" class="hp-wg-open" data-hal-widget-nav="${esc(nav)}">${uiIcon("externalLink")} OPEN PAGE</button>
        </article>`;
      })
      .join("");
    const publish = (halWidgetFeed.jobs && halWidgetFeed.jobs.widgetPublish && halWidgetFeed.jobs.widgetPublish.status) || "—";
    const widgetCount = typeof HalSkills !== "undefined" && HalSkills.WIDGET_ORDER ? HalSkills.WIDGET_ORDER.length : Object.keys(halWidgetFeed.widgets || {}).length;
    return `<div class="hp-widgets" data-panel="widgets">
      <div class="hp-sn-head"><h4>MANAGER DASHBOARD WIDGETS</h4><span class="hp-sn-stat">${widgetCount} widgets · import cache · publish ${esc(publish)}</span></div>
      <div class="hp-wg-grid">${cards}</div>
      <p class="hp-sn-foot">HAL-managed widgets · local only · A/R from verified sources only</p>
    </div>`;
  }

  function aiStatRow(label, value, ok) {
    return `<div><dt>${esc(label)}</dt><dd${ok ? ' class="hp-ok"' : ""}>${esc(value)}</dd></div>`;
  }

  function aiReadinessHtml(halModels) {
    const rd = halModels && halModels.readinessDisplay;
    if (!rd) return emptyNote("Local AI readiness not configured.");

    const cfg = (halModels && halModels.config) || {};
    const svc = rd.localAiService || {};
    const api = rd.api || {};
    const cm = rd.configuredModels || {};
    const localModel = cm.local || {};
    const reasoningModel = cm.reasoning || {};
    const escalationModel = cm.escalation || {};
    const inventory = rd.availableModels || [];
    const inventoryPreview = inventory.slice(0, 4).join(" · ");
    const inventoryMore = inventory.length > 4 ? ` +${inventory.length - 4} more` : "";
    const runtimes = [cfg.localModel, cfg.reasoningModel, cfg.escalationModel];
    const webResearchOn = cfg.webResearch && cfg.webResearch.enabled === true;
    const lanesLive =
      cfg.mode === "online" &&
      cfg.externalCallsEnabled === false &&
      runtimes.every((runtime) => runtime && runtime.enabled && String(runtime.endpoint || "").includes("127.0.0.1"));
    const displayLabel = lanesLive ? (webResearchOn ? "(local models + web research)" : "(local only)") : "(display only)";

    return `
      <div class="hp-ai-ready">
        <p class="hp-ai-ready__title">LOCAL AI READINESS <span class="hp-muted">${displayLabel}</span></p>
        <dl class="hp-stats hp-stats--ai">
          ${aiStatRow("LOCAL AI SERVICE", `${svc.status || "Unknown"} · ${svc.name || "—"}`, svc.status === "Detected")}
          ${aiStatRow("OLLAMA API", `${api.status || "Unknown"} · ${api.version || "—"}`, api.status === "Reachable")}
          ${aiStatRow("ACTIVE LANE", rd.activeLane || cfg.activeLane || "—")}
          ${aiStatRow("LOCAL MODEL", `${localModel.model || cfg.localModel?.model || "—"} · ${localModel.available ? "available" : "missing"}`, !!localModel.available)}
          ${aiStatRow("REASONING MODEL", `${reasoningModel.model || "—"} · ${reasoningModel.available ? "available" : "missing"}`, !!reasoningModel.available)}
          ${aiStatRow("ESCALATION MODEL", `${escalationModel.model || "—"} · ${escalationModel.available ? "available" : "missing"}`, !!escalationModel.available)}
          ${aiStatRow("RUNNING MODEL", rd.runningModel || "none")}
          ${aiStatRow("GPU STATUS", rd.gpuStatus || "not verified", rd.gpu && rd.gpu.verified === true)}
          ${aiStatRow("BINDING", rd.bindingStatus || "not verified")}
          ${aiStatRow("LANE EXECUTION", lanesLive ? rd.laneExecution || "Enabled · local loopback only" : "Disabled")}
        </dl>
        <p class="hp-ai-ready__inventory"><b>Available inventory:</b> ${esc(inventoryPreview)}${esc(inventoryMore)} <em class="hp-muted">${lanesLive ? "(routed locally on query)" : "(not routed)"}</em></p>
        <p class="hp-card__foot hp-card__foot--ai">${esc(rd.dataPolicy || "No sensitive raw data sent to any model.")}</p>
      </div>`;
  }

  function stressTestHtml(st) {
    const s = st || {};
    const total = Number(s.total) || 2000000;
    const processed = Number(s.processed) || 0;
    const pct = total > 0 ? Math.min(100, Math.round((processed / total) * 100)) : 0;
    const running = !!s.running;
    const status = s.status || (running ? "Running" : processed > 0 && !s.failureTotal ? "Pass" : processed > 0 ? "Fail" : "Idle");
    const statusClass = status === "Pass" ? "hp-stress__status--ok" : status === "Fail" ? "hp-stress__status--fail" : running ? "hp-stress__status--run" : "";
    const failures = Array.isArray(s.topFailures) ? s.topFailures : [];
    const failRows = failures.length
      ? failures
          .slice(0, 12)
          .map(
            (f) =>
              `<li><span class="hp-stress__fail-count">${esc(f.count)}×</span> <code>${esc(f.stage)}</code> — ${esc(f.error)}<br><em class="hp-muted">${esc(String(f.example || "").slice(0, 120))}</em></li>`,
          )
          .join("")
      : '<li class="hp-stress__empty">No failures yet.</li>';

    return `<div class="hp-stress" id="hpStressPanel">
      <div class="hp-stress__head">
        <h4>ASK HAL STRESS TEST</h4>
        <span class="hp-stress__status ${statusClass}" id="hpStressStatus">${esc(status)}</span>
      </div>
      <p class="hp-stress__note">Routes, handlers, agent planner, and self-check — no live model calls. Generates questions on the fly so 2M+ runs stay in memory.</p>
      <div class="hp-stress__row">
        <label class="hp-stress__label" for="hpStressCount">Questions</label>
        <input class="hp-stress__input" id="hpStressCount" type="number" min="100" step="1000" value="${esc(total)}" ${running ? "disabled" : ""} />
        <button type="button" class="hp-stress__run" id="hpStressRun" data-hal-stress-run ${running ? "disabled" : ""}>${uiIcon("check")} Run</button>
        <button type="button" class="hp-stress__stop" id="hpStressStop" data-hal-stress-stop ${running ? "" : "disabled"}>${uiIcon("close")} Stop</button>
      </div>
      <div class="hp-stress__bar" aria-hidden="true"><span class="hp-stress__bar-fill" id="hpStressBar" style="width:${pct}%"></span></div>
      <dl class="hp-stress__stats">
        <div><dt>Processed</dt><dd id="hpStressProcessed">${esc(processed.toLocaleString())}</dd></div>
        <div><dt>Total</dt><dd id="hpStressTotal">${esc(total.toLocaleString())}</dd></div>
        <div><dt>Rate</dt><dd id="hpStressRate">${esc(s.rate ? s.rate.toLocaleString() + " q/s" : "—")}</dd></div>
        <div><dt>Failures</dt><dd id="hpStressFailures" class="${s.failureTotal ? "hp-stress__fail-num" : ""}">${esc(String(s.failureTotal || 0))}</dd></div>
        <div><dt>Distinct</dt><dd id="hpStressDistinct">${esc(String(s.distinctFailures || 0))}</dd></div>
        <div><dt>Intents</dt><dd id="hpStressIntents">${esc(String(s.intentCount || "—"))}</dd></div>
      </dl>
      <ul class="hp-stress__failures" id="hpStressFailList">${failRows}</ul>
    </div>`;
  }

  function agentHealthHtml(health, models, inbox) {
    const h = health || {};
    const rd = (models && models.readinessDisplay) || {};
    const inboxLive = inbox && inbox.monitor ? "Live" : "Offline";
    const selfCheckClass = String(h.lastSelfCheck || "").startsWith("pass") || h.lastSelfCheck === "none" ? "hp-ok" : "hp-stress__fail-num";
    return `<div class="hp-agent-health">
      <div class="hp-stress__head">
        <h4>HAL RUNTIME HEALTH</h4>
        <span class="hp-stress__status hp-stress__status--ok">${esc(h.architectureVersion || "hal-agent")}</span>
      </div>
      <dl class="hp-stress__stats">
        <div><dt>Model</dt><dd>${esc((rd.configuredModels && rd.configuredModels.local && rd.configuredModels.local.model) || rd.runningModel || "—")}</dd></div>
        <div><dt>GPU</dt><dd>${esc(rd.gpuStatus || "—")}</dd></div>
        <div><dt>Budget</dt><dd>${esc(h.budget ? `${h.budget.maxTools} tools · ${h.budget.maxRecentTurns} turns` : "—")}</dd></div>
        <div><dt>Last Intent</dt><dd>${esc(h.lastIntent || "—")}</dd></div>
        <div><dt>Self-Check</dt><dd class="${selfCheckClass}">${esc(h.lastSelfCheck || "none")}</dd></div>
        <div><dt>Repairs</dt><dd class="${h.repairCount ? "hp-stress__fail-num" : ""}">${esc(String(h.repairCount || 0))}</dd></div>
        <div><dt>Latency</dt><dd>${esc(h.lastLatencyMs ? h.lastLatencyMs + " ms" : "—")}</dd></div>
        <div><dt>SideNotes</dt><dd>${esc(inboxLive)}</dd></div>
      </dl>
      <p class="hp-card__foot hp-muted">Agent uses cached snapshots, bounded tools, local memory, and self-check before final answers.</p>
    </div>`;
  }

  function render(ctx) {
    const root = ctx.root;
    if (!root) return;
    const { halData, halModels, halAudit, halChatHistory, halAskDraft, halAskLoading, halInlineFirewallResult, halSideNotes, halSideNoteMonitor, halSideNotesInbox, halWidgetFeed, halProactiveBriefing, halStressTest, halAgentHealth, sidenotesHubPath } = ctx;
    const suggestions = (halData.askHal?.suggestions || []).slice(0, 12);
    // One message at a time: only the most recent turn is shown (no scrolling).
    const messages = (halChatHistory || []).slice(-1);
    const chatHtml = messages.length
      ? messages
          .map(
            (m) =>
              `<div class="hp-chat-row hp-chat-row--${m.role === "user" ? "user" : "hal"}">
                <div class="hp-chat-row__head">
                  <span>${m.role === "user" ? "You" : "HAL"}${m.lane ? ` · ${esc(m.lane)}` : ""}</span>
                  ${m.role === "hal" ? `<button type="button" class="hp-chat-copy" data-hal-copy-response title="Copy response (Ctrl+C also works)">${uiIcon("copy")} Copy</button>` : ""}
                </div>
                <p>${esc(m.text)}</p>
              </div>`,
          )
          .join("")
      : emptyNote("No HAL responses yet. Ask a question to begin.");

    const liveSources = (halWidgetFeed && halWidgetFeed.sourceHealth) || {};
    const sourceRows = ((halData.sources && halData.sources.items) || [])
      .map((item) => {
        const live = liveSources[item.target];
        // Prefer live import freshness/status; fall back to static config only
        // when no import data is present for this source.
        const useLive = live && live.hasData;
        const freshness = useLive ? live.freshness : item.freshness || "Not available";
        const statusKey = useLive ? mapLiveSourceStatus(live) : mapSourceStatus(item);
        const sourceCmd = `Review read-only source health for ${item.label}`;
        return `<tr class="hp-table__row--active" data-hal-source-nav="${esc(item.target)}" data-hal-cmd="${esc(sourceCmd)}" role="button" tabindex="0" title="${esc(sourceCmd)} · click arrow to open page">
          <td><span class="hp-table__label">${navIcon(item.target)}<span>${esc(item.label)}</span></span></td>
          <td>${esc(item.status || "unknown")}</td>
          <td>${esc(freshness || "Not available")}</td>
          <td>${esc(formatStatus(statusKey))}</td>
          <td class="hp-table__go"><button type="button" class="hp-table__open" data-hal-source-open="${esc(item.target)}" title="Open ${esc(item.label)}" aria-label="Open ${esc(item.label)}">${uiIcon("chevronRight")}</button></td>
        </tr>`;
      })
      .join("");

    const liveSurfaces = (halWidgetFeed && halWidgetFeed.surfaceCounts) || {};
    const surfaces = ((halData.workSurfaces && halData.workSurfaces.items) || [])
      .map((item) => {
        const reg = (halData.registry || []).find((e) => e.id === item.target);
        const live = liveSurfaces[item.target];
        const state = live ? mapSurfaceState(live.status) : reg ? reg.state : "unknown";
        const updated = live && live.updated ? live.updated : "Not available";
        const items =
          live && live.items != null
            ? `${live.items}${live.itemsLabel ? " " + live.itemsLabel : ""}`
            : "—";
        const surfCmd = `Explain the ${item.label} work surface and what staff should do next`;
        const surfOpen = surfNavTarget(item);
        return `<li class="hp-surf__row" data-hal-surf-nav="${esc(surfOpen)}" data-hal-cmd="${esc(surfCmd)}" role="button" tabindex="0" title="${esc(surfCmd)}">
          <span class="hp-surf__ico" aria-hidden="true">${surfNavIcon(item)}</span>
          <div class="hp-surf__main"><strong>${esc(item.label)}</strong><span>${esc(item.detail || "")}</span></div>
          <div class="hp-surf__meta">
            <span>State<br><b>${esc(state)}</b></span>
            <span>Updated<br><b>${esc(updated)}</b></span>
            <span>Items<br><b>${esc(items)}</b></span>
          </div>
          <button type="button" class="hp-surf__chev" data-hal-surf-open="${esc(surfOpen)}" title="Open ${esc(item.label)}" aria-label="Open ${esc(item.label)}">${uiIcon("chevronRight")}</button>
        </li>`;
      })
      .join("");

    const activity = (halAudit || []).slice(-5).reverse();
    const activityHtml = activity.length
      ? activity
          .map(
            (row) =>
              `<li class="hp-log__row--active" data-hal-activity-cmd="${esc(row.query || row.label || "")}" role="button" tabindex="0" title="Ask HAL again"><i class="hp-log__dot hp-log__dot--gold" aria-hidden="true"></i><span>${esc(row.query || row.label || "")}</span><time>${esc(row.time || "")}</time></li>`,
          )
          .join("")
      : emptyNote("No HAL activity in this session yet.");

    const insights = (halData.registry || [])
      .filter((e) => e.nextAction)
      .slice(0, 4)
      .map((e) => {
        const conf =
          String(e.state).toLowerCase() === "blocked"
            ? "high"
            : String(e.state).toLowerCase().includes("review")
              ? "medium"
              : "low";
        const insightCmd = `Open ${e.name} and ${e.nextAction}`;
        return `<li class="hp-insight__row--active" data-hal-insight-nav="${esc(e.id)}" data-hal-cmd="${esc(insightCmd)}" role="button" tabindex="0" title="${esc(insightCmd)}"><i class="hp-log__dot hp-log__dot--gold" aria-hidden="true"></i><span>${esc(e.name)}: ${esc(e.nextAction)}</span><b class="hp-conf hp-conf--${conf === "high" ? "high" : conf === "medium" ? "med" : "low"}">${esc(conf)} confidence</b><button type="button" class="hp-insight__open" data-hal-insight-open="${esc(e.id)}" title="Open ${esc(e.name)}" aria-label="Open ${esc(e.name)}">${uiIcon("chevronRight")}</button></li>`;
      })
      .join("");

    const blocked = (halData.firewall?.blocked || []).slice(0, 5);
    const fwList = blocked
      .map((item) => {
        const fwCmd = `Explain why "${item}" is blocked by the firewall`;
        return `<li class="hp-fw__row--active" data-hal-cmd="${esc(fwCmd)}" role="button" tabindex="0" title="${esc(fwCmd)}"><span>${esc(item)}</span><b>BLOCKED</b></li>`;
      })
      .join("");

    const now = new Date();
    const registry = halData.registry || [];
    const tally = (pred) => registry.filter((e) => pred(String(e.state || "").toLowerCase())).length;
    const readyCount = tally((s) => s === "ready");
    const blockedCount = tally((s) => s === "blocked");
    // HAL is a local read-only manager: it is online/healthy whenever its
    // program registry has loaded. Individual lane states are surfaced
    // separately as READY / BLOCKED counts below, not as HAL's own health.
    const halLoaded = registry.length > 0;
    const halStatusLabel = halLoaded ? "ONLINE" : "OFFLINE";
    const coreStatusLabel = halLoaded ? "HEALTHY" : "CHECK";
    const modeLabel = halModels?.config?.mode === "online" ? "Auto" : "Registry-only";

    // Manager signals derived from data already in ctx (no backend):
    // priorities/registry for next step + active work, firewall for allowed,
    // and the local audit log for the last local receipt/status.
    const needsReviewCount = tally((s) => s.includes("review"));
    const priorities = (halData.priorities && halData.priorities.items) || [];
    const topPriority =
      (halData.topPriority && halData.topPriority.summary) ||
      "Monitor the program, place correct data, and recommend the next safe staff action.";
    const nextSafeStep =
      (halProactiveBriefing && halProactiveBriefing.topAction && halProactiveBriefing.topAction.title) ||
      priorities[0] ||
      (registry.find((e) => e.nextAction) || {}).nextAction ||
      "Review the Needs Review lane before any external step.";
    const proactiveInsight =
      halProactiveBriefing && halProactiveBriefing.recommendations && halProactiveBriefing.recommendations.length
        ? halProactiveBriefing.recommendations
            .slice(0, 3)
            .map(
              (item) =>
                `<li class="hp-insight__lead hp-insight__row--active" data-hal-cmd="Explain ${esc(item.title)}" role="button" tabindex="0" title="Ask HAL about this recommendation"><i class="hp-log__dot hp-log__dot--gold" aria-hidden="true"></i><span><b>${esc(item.severity.toUpperCase())}</b> — ${esc(item.title)}</span></li>`,
            )
            .join("")
        : "";
    const programAccessLabel =
      halData.programAccess?.mode === "full-read"
        ? "Full read · all pages and services (local)"
        : "Registry only";
    const allowedActions = (halData.firewall && halData.firewall.allowed) || [];
    const auditList = halAudit || [];
    const lastReceipt = auditList.length ? auditList[auditList.length - 1] : null;
    const lastReceiptText = lastReceipt
      ? `${lastReceipt.time || ""} · ${lastReceipt.intent || lastReceipt.query || "local action"}`.trim()
      : "No local receipt this session";

    // HAL orb state: color/tempo variants while thinking or on warning.
    // Derived from data already in ctx (no backend, no polling).
    const liveUnread = !!(
      halSideNotesInbox &&
      Array.isArray(halSideNotesInbox.items) &&
      halSideNotesInbox.items.some((m) => m && m.unread)
    );
    const hasWarning =
      blockedCount > 0 ||
      liveUnread ||
      !!(halSideNoteMonitor && (halSideNoteMonitor.hasChanges || halSideNoteMonitor.highPriorityCount > 0)) ||
      !!(halInlineFirewallResult && /block/i.test(halInlineFirewallResult.text || ""));
    const ringState = !halLoaded
      ? "offline"
      : halAskLoading
        ? "thinking"
        : hasWarning
          ? "warning"
          : "ready";
    const ringStateLabel =
      ringState === "thinking"
        ? "THINKING"
        : ringState === "warning"
          ? "ATTENTION"
          : ringState === "offline"
            ? "OFFLINE"
            : "READY";
    const activeLaneModel =
      (halModels?.lanes || []).find((l) => l.id === halModels?.config?.activeLane)?.model ||
      halModels?.config?.localModel?.model ||
      "local";
    const ringTitle = `HAL ${ringStateLabel} · ${readyCount} ready · ${blockedCount} blocked · active lane ${activeLaneModel} · click for reasoning detail`;

    // HUD gauge: ready/blocked arcs around the rim, scaled to the registry.
    const gaugeR = 46;
    const gaugeC = 2 * Math.PI * gaugeR;
    const totalTracked = Math.max(registry.length, 1);
    const readyLen = (readyCount / totalTracked) * gaugeC;
    const blockedLen = (blockedCount / totalTracked) * gaugeC;
    const gaugeSvg = `
      <svg class="hp-ring__gauge" viewBox="0 0 100 100" aria-hidden="true">
        <circle class="hp-ring__gauge-track" cx="50" cy="50" r="${gaugeR}"></circle>
        <circle class="hp-ring__gauge-arc hp-ring__gauge-ready" cx="50" cy="50" r="${gaugeR}" stroke-dasharray="${readyLen.toFixed(2)} ${(gaugeC - readyLen).toFixed(2)}"></circle>
        <circle class="hp-ring__gauge-arc hp-ring__gauge-blocked" cx="50" cy="50" r="${gaugeR}" stroke-dasharray="${blockedLen.toFixed(2)} ${(gaugeC - blockedLen).toFixed(2)}" stroke-dashoffset="${(-readyLen).toFixed(2)}"></circle>
      </svg>`;

    const toothMark = `
      <svg class="hp-top__tooth" viewBox="0 0 64 64" aria-hidden="true">
        <path d="M20.9 7.8c4.4 0 7.1 2.4 11.1 2.4s6.7-2.4 11.1-2.4c7.8 0 13.2 6.3 13.2 15.1 0 5.4-2.4 10.4-4.7 15.2-2.2 4.6-3.4 9.7-4.4 14.7-.6 3.1-2.5 5.2-5.1 5.2-3.1 0-4.5-2.9-5.6-6.4l-2.1-6.7c-.7-2.3-1.4-3.8-2.4-3.8s-1.7 1.5-2.4 3.8l-2.1 6.7c-1.1 3.5-2.5 6.4-5.6 6.4-2.6 0-4.5-2.1-5.1-5.2-1-5-2.2-10.1-4.4-14.7-2.3-4.8-4.7-9.8-4.7-15.2C7.7 14.1 13.1 7.8 20.9 7.8Z"
          fill="none" stroke="currentColor" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" />
      </svg>`;

    root.innerHTML = `
      <div class="hp-body">
        <header class="hp-top">
          <div class="hp-top__brand">
            <button type="button" class="hp-top__mark hp-top__mark--btn" data-hal-cmd="What can you do" title="Ask HAL what it can do" aria-label="Ask HAL what it can do">${toothMark}</button>
            <div class="hp-top__copy"><strong>HAL COMMAND CENTER</strong><span>Direct. Orchestrate. Protect.</span></div>
          </div>
          <div class="hp-top__status">
            <button type="button" class="hp-status hp-status--btn" data-hal-cmd="What can you do" title="Ask HAL what it can do"><i class="hp-status__dot hp-status__dot--ok" aria-hidden="true"></i>HAL STATUS <b>${esc(halStatusLabel)}</b></button>
            <button type="button" class="hp-status hp-status--btn" data-hal-cmd="Run readiness check" title="Run local readiness check"><i class="hp-status__dot hp-status__dot--ok" aria-hidden="true"></i>LOCAL CORE <b>${esc(coreStatusLabel)}</b></button>
            <button type="button" class="hp-status hp-status--btn hp-status--red" data-hal-cmd="Explain the external action firewall" title="Explain the external action firewall"><i class="hp-status__dot hp-status__dot--red" aria-hidden="true"></i>FIREWALL <b>ACTIVE</b></button>
            <span class="hp-clock"><strong>${esc(now.toISOString().slice(11, 19))} UTC</strong><span>${esc(now.toISOString().slice(0, 10))}</span></span>
          </div>
        </header>
        <div class="hp-grid">
          <section class="hp-card hp-card--ask" data-panel="askHal" style="grid-area:ask;">
            ${cardHead("ASK HAL", "askHal", "Open Ask HAL detail and command examples", cardIconRaw("hal"))}
            <form class="hp-ask__box hp-live-form" id="hpAskForm">
              <textarea class="hp-live-input hp-live-textarea" id="hpAskInput" rows="3" enterkeyhint="send" placeholder="Ask HAL anything. Be direct.  (Enter to send · Shift+Enter for a new line)" aria-label="Ask HAL">${esc(halAskDraft || "")}</textarea>
              <div class="hp-ask__bar">
                <span class="hp-ask__mode">MODE</span>
                <span class="hp-ask__sel">${esc(halModels?.config?.mode === "online" ? "Auto" : "Registry only")}</span>
                <span class="hp-ask__hint" aria-hidden="true">↵ Enter to send</span>
                <button class="hp-ask__send hp-live-send" type="submit" ${halAskLoading ? "disabled" : ""}>${halAskLoading ? "…" : `${uiIcon("send")} SEND`}</button>
              </div>
            </form>
            <div class="hp-inline-chat">${chatHtml}</div>
            <div class="hp-chips hp-live-actions">${suggestions.map((s) => actionChip(s, `data-hal-suggest="${esc(s)}"`)).join("")}</div>
          </section>
          <section class="hp-card hp-card--reason" data-panel="reasoning" style="grid-area:reason;">
            ${cardHead("LOCAL REASONING CORE", "reasoning", "Open reasoning detail: active work session, plan, and evidence packet", cardIconRaw("widget", "officeManagerBoundaries"))}
            <div class="hp-reason">
              <div class="hp-ring hp-ring--${ringState}" data-hal-drawer="reasoning" data-hal-ring-cmd="Make a plan for today" role="button" tabindex="0" title="${esc(ringTitle)} · double-click for today's plan" aria-label="${esc(ringTitle)}">
                ${gaugeSvg}
                <span class="hp-ring__bezel" aria-hidden="true"></span>
                <span class="hp-ring__radar" aria-hidden="true"></span>
                <div class="hp-ring__lens" aria-hidden="true">
                  <span class="hp-ring__iris"></span>
                  <span class="hp-ring__lens-glow"></span>
                  <span class="hp-ring__lens-hot"></span>
                  <span class="hp-ring__iris-core"></span>
                  <span class="hp-ring__lens-glint"></span>
                  <div class="hp-ring__lens-data">
                    <span class="hp-ring__state">${esc(ringStateLabel)}</span>
                  </div>
                </div>
              </div>
              <dl class="hp-stats">
                <div><dt>STATUS</dt><dd class="${halLoaded ? "hp-ok" : ""}">${esc(halLoaded ? "Active" : "Idle")}</dd></div>
                <div><dt>MODE</dt><dd>${esc(modeLabel)}</dd></div>
                <div><dt>READY</dt><dd class="hp-ok">${esc(readyCount)}</dd></div>
                <div><dt>BLOCKED</dt><dd>${esc(blockedCount)}</dd></div>
              </dl>
            </div>
            ${aiReadinessHtml(halModels)}
            <p class="hp-card__foot">All reasoning stays local. No data leaves this environment.</p>
            <div class="hp-chips">${(halData.reasoning?.actions || []).map((a) => actionChip(a.label, `data-hal-cmd="${esc(a.command)}"`)).join("") || emptyNote("No reasoning actions configured.")}</div>
          </section>
          <section class="hp-card" data-panel="sources" style="grid-area:source;">
            ${cardHead('SOURCE INTAKE <span class="hp-muted">(READ-ONLY)</span>', "sources", "Open source intake detail", cardIconRaw("widget", "dataFreshnessQuality"))}
            <table class="hp-table"><thead><tr><th>SOURCE</th><th>TYPE</th><th>FRESHNESS</th><th>STATUS</th><th aria-label="Open"></th></tr></thead><tbody>${sourceRows || `<tr><td colspan="5">No sources configured</td></tr>`}</tbody></table>
            <p class="hp-card__foot hp-muted">Freshness reflects local SoftDent and QuickBooks import files only.</p>
          </section>
          ${sideNotesProgramCardHtml(halSideNotes, halSideNoteMonitor, halSideNotesInbox, sidenotesHubPath)}
          <section class="hp-card" data-panel="workSurfaces" style="grid-area:staff;">
            ${cardHead("STAFF WORK SURFACES", "workSurfaces", "Open staff work surfaces detail", cardIconRaw("ui", "surface"))}
            <ul class="hp-surf">${surfaces || emptyNote("No work surfaces configured.")}</ul>
          </section>
          <section class="hp-card hp-card--fw" data-panel="firewall" style="grid-area:firewall;">
            ${cardHead("EXTERNAL ACTION FIREWALL", "firewall", "Open firewall detail: allowed actions, blocked actions, and simulator", cardIconRaw("ui", "shield"))}
            <button type="button" class="hp-fw__active hp-fw__active--btn" data-hal-cmd="Explain the external action firewall" title="Explain the external action firewall">${uiIcon("check")} ENFORCED (read-only program)</button>
            <ul class="hp-fw__list">${fwList}</ul>
            <p class="hp-fw__allowed"><b>Allowed (local):</b> ${allowedActions.length ? allowedActions.slice(0, 6).map(esc).join(" · ") : "Open pages · Explain status · Prepare notes"}</p>
            ${halInlineFirewallResult ? `<p class="hp-live-note">${esc(halInlineFirewallResult.text || "")}</p>` : ""}
          </section>
          <section class="hp-card" data-panel="status" style="grid-area:recent;">
            ${cardHead("RECENT HAL ACTIVITY", "status", "Open recent activity and local audit log", cardIconRaw("ui", "activity"))}
            <ul class="hp-log">${activityHtml}</ul>
          </section>
          <section class="hp-card" data-panel="priorities" style="grid-area:insights;">
            ${cardHead("HAL INSIGHTS", "priorities", "Open priorities, recommendations, and next steps", cardIconRaw("ui", "insights"))}
            <ul class="hp-insight">
              <li class="hp-insight__lead hp-insight__row--active" data-hal-cmd="Show full program snapshot" role="button" tabindex="0" title="Show full program snapshot"><i class="hp-log__dot hp-log__dot--gold" aria-hidden="true"></i><span><b>TOP PRIORITY</b> — ${esc(topPriority)}</span></li>
              <li class="hp-insight__lead hp-insight__row--active" data-hal-cmd="Explain the external action firewall" role="button" tabindex="0" title="Explain program access rules"><i class="hp-log__dot hp-log__dot--gold" aria-hidden="true"></i><span><b>PROGRAM ACCESS</b> — ${esc(programAccessLabel)} <em class="hp-muted">(writes blocked)</em></span></li>
              <li class="hp-insight__lead hp-insight__row--active" data-hal-cmd="What needs review" role="button" tabindex="0" title="What needs review"><i class="hp-log__dot hp-log__dot--gold" aria-hidden="true"></i><span><b>NEXT SAFE STEP</b> — ${esc(nextSafeStep)}</span></li>
              ${proactiveInsight}
              <li class="hp-insight__lead hp-insight__row--active" data-hal-cmd="What needs review" role="button" tabindex="0" title="What needs review"><i class="hp-log__dot hp-log__dot--gold" aria-hidden="true"></i><span><b>ACTIVE WORK</b> — ${esc(needsReviewCount)} in review · ${esc(blockedCount)} blocked <em class="hp-muted">(local registry)</em></span></li>
              ${insights || emptyNote("No registry insights available.")}
            </ul>
            ${widgetsMonitorHtml(halWidgetFeed)}
          </section>
          <section class="hp-card" data-panel="controls" style="grid-area:controls;">
            ${cardHead("SYSTEM CONTROLS", "controls", "Open system controls: readiness, smoke test, and local receipts", cardIconRaw("ui", "check"))}
            <div class="hp-ctrl">
              <button type="button" class="hp-ctrl__btn" data-hal-cmd="Run readiness check"><span class="hp-ctrl__ico">${uiIcon("check")}</span><strong>Readiness</strong><span class="hp-ctrl__detail">Local check</span></button>
              <button type="button" class="hp-ctrl__btn" data-hal-cmd="Run operator smoke test"><span class="hp-ctrl__ico">${uiIcon("smoke")}</span><strong>Smoke test</strong><span class="hp-ctrl__detail">Local only</span></button>
              <button type="button" class="hp-ctrl__btn" data-hal-cmd="Staff handoff summary"><span class="hp-ctrl__ico">${uiIcon("handoff")}</span><strong>Handoff</strong><span class="hp-ctrl__detail">Build summary</span></button>
              <button type="button" class="hp-ctrl__btn" data-hal-cmd="Monitor sidenotes"><span class="hp-ctrl__ico">${navIcon("sidenotes")}</span><strong>SideNotes</strong><span class="hp-ctrl__detail">Live monitor</span></button>
              <button type="button" class="hp-ctrl__btn" data-hal-drawer="status"><span class="hp-ctrl__ico">${uiIcon("audit")}</span><strong>Audit log</strong><span class="hp-ctrl__detail">${auditList.length ? esc("Last " + (lastReceipt.time || "—")) : "0 actions"}</span></button>
            </div>
            <p class="hp-card__foot">Last local receipt: ${esc(lastReceiptText)} · receipts stay on this device.</p>
            ${agentHealthHtml(halAgentHealth, halModels, halSideNotesInbox)}
            ${stressTestHtml(halStressTest)}
          </section>
        </div>
      </div>`;

    const input = root.querySelector("#hpAskInput");
    if (input && halAskDraft) input.value = halAskDraft;
  }

  return { render, sideNotesMonitorHtml, sideNotesProgramCardHtml, widgetsMonitorHtml, isSideNotesInboxLive, surfNavTarget };
})();

if (typeof module !== "undefined" && module.exports) {
  module.exports = HalPage;
}
if (typeof window !== "undefined") {
  window.HalPage = HalPage;
}
