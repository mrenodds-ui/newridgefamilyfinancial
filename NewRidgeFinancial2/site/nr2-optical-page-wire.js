/* Shared optical subpage wire helpers — empty ≠ $0 (CSP script-src 'self') */
(function (global) {
  function money(n) {
    if (n == null || !Number.isFinite(Number(n))) return null;
    return Number(n);
  }
  function fmtMoney(n) {
    const v = money(n);
    if (v == null) return null;
    return "$" + v.toLocaleString("en-US", { maximumFractionDigits: 0 });
  }
  function clearLoadingFace(el) {
    if (!el) return;
    el.classList.remove("is-loading");
    el.removeAttribute("aria-busy");
    const sk = el.querySelector(".nr2-skeleton");
    if (sk) sk.remove();
  }
  /** Gray bar only — never show placeholder dollars while loading. */
  function setLoading(idOrEl) {
    const el = typeof idOrEl === "string" ? document.getElementById(idOrEl) : idOrEl;
    if (!el) return null;
    el.classList.remove("empty", "zero", "nosignal");
    el.classList.add("is-loading");
    el.setAttribute("aria-busy", "true");
    el.textContent = "";
    const sk = document.createElement("span");
    sk.className = "nr2-skeleton";
    sk.setAttribute("aria-hidden", "true");
    el.appendChild(sk);
    return el;
  }
  function markFacesLoading(ids) {
    const list = Array.isArray(ids) ? ids : [];
    list.forEach(function (id) {
      setLoading(id);
    });
    return list.length;
  }
  function isBrowserOffline() {
    try {
      return navigator.onLine === false;
    } catch (_) {
      return false;
    }
  }
  function clearErrorFace(el) {
    if (!el) return;
    el.classList.remove("nr2-error-face", "nr2-soft-fail", "nr2-hard-fail", "nr2-error-beam");
    const chip = el.querySelector(".nr2-retry-chip");
    if (chip) chip.remove();
  }
  /**
   * Package 8: soft fail (retry chip) vs hard fail (stuck NO SIGNAL).
   * opts: { label, detail, hard, onRetry, countdownSec, announce }
   */
  function setErrorState(idOrEl, opts) {
    const o = opts || {};
    const el = typeof idOrEl === "string" ? document.getElementById(idOrEl) : idOrEl;
    if (!el) return null;
    clearLoadingFace(el);
    clearErrorFace(el);
    el.classList.remove("empty", "zero");
    el.classList.add("nosignal", "nr2-error-face");
    if (o.hard) el.classList.add("nr2-hard-fail");
    else el.classList.add("nr2-soft-fail", "nr2-error-beam");
    const offline = isBrowserOffline();
    const label =
      o.label ||
      (offline ? "OFFLINE" : o.hard ? "NO SIGNAL" : "NO SIGNAL · retry");
    el.textContent = "";
    const text = document.createElement("span");
    text.className = "nr2-error-label";
    text.textContent = label;
    el.appendChild(text);
    if (o.detail) {
      const d = document.createElement("span");
      d.className = "nr2-error-detail";
      d.textContent = " · " + String(o.detail);
      el.appendChild(d);
    }
    if (!o.hard && typeof o.onRetry === "function") {
      mountRetryChip(el, {
        onRetry: o.onRetry,
        countdownSec: o.countdownSec,
        label: o.retryLabel,
      });
    }
    if (o.announce !== false) {
      announce(label + (o.detail ? " · " + o.detail : "") + " · empty ≠ $0");
    }
    return el;
  }
  const retryTimers = new WeakMap();
  function mountRetryChip(host, opts) {
    const o = opts || {};
    if (!host || typeof o.onRetry !== "function") return null;
    const prev = retryTimers.get(host);
    if (prev) {
      clearInterval(prev.interval);
      clearTimeout(prev.timeout);
      retryTimers.delete(host);
    }
    let chip = host.querySelector(".nr2-retry-chip");
    if (!chip) {
      chip = document.createElement("button");
      chip.type = "button";
      chip.className = "nr2-retry-chip";
      host.appendChild(chip);
    }
    let left = Math.max(0, Number(o.countdownSec) || 0);
    const base = o.label || "Retry";
    function paint() {
      chip.textContent = left > 0 ? base + " · " + left + "s" : base + " now";
      chip.disabled = false;
    }
    function run() {
      const st = retryTimers.get(host);
      if (st) {
        clearInterval(st.interval);
        clearTimeout(st.timeout);
        retryTimers.delete(host);
      }
      chip.disabled = true;
      chip.textContent = "Retrying…";
      Promise.resolve()
        .then(function () {
          return o.onRetry();
        })
        .catch(function () {
          /* caller paints fault */
        })
        .then(function () {
          chip.disabled = false;
          paint();
        });
    }
    paint();
    chip.onclick = function (e) {
      e.preventDefault();
      e.stopPropagation();
      run();
    };
    if (left > 0) {
      const interval = setInterval(function () {
        left -= 1;
        if (left <= 0) {
          clearInterval(interval);
          run();
          return;
        }
        paint();
      }, 1000);
      retryTimers.set(host, { interval: interval, timeout: null });
    }
    return chip;
  }
  function ensureErrorRail() {
    let rail = document.getElementById("nr2-error-rail");
    if (rail) return rail;
    rail = document.createElement("div");
    rail.id = "nr2-error-rail";
    rail.className = "nr2-error-rail";
    rail.hidden = true;
    rail.setAttribute("role", "status");
    rail.setAttribute("aria-live", "polite");
    const banner = document.querySelector(".banner");
    if (banner && banner.parentNode) {
      banner.insertAdjacentElement("afterend", rail);
    } else {
      const main = document.querySelector(".main") || document.body;
      main.insertBefore(rail, main.firstChild);
    }
    return rail;
  }
  function hideErrorRail() {
    const rail = document.getElementById("nr2-error-rail");
    if (!rail) return;
    rail.hidden = true;
    rail.textContent = "";
    rail.className = "nr2-error-rail";
  }
  /**
   * Soft fail rail (retry) or hard fail panel.
   * opts: { hard, message, detail, onRetry, countdownSec }
   */
  function showPageError(opts) {
    const o = opts || {};
    const rail = ensureErrorRail();
    const offline = isBrowserOffline();
    rail.hidden = false;
    rail.className =
      "nr2-error-rail " +
      (o.hard ? "nr2-hard-fail" : "nr2-soft-fail") +
      (offline ? " is-offline" : "") +
      (o.hard ? "" : " nr2-error-beam");
    rail.textContent = "";
    const msg = document.createElement("span");
    msg.className = "nr2-error-rail-msg";
    msg.textContent =
      o.message ||
      (offline
        ? "OFFLINE · SoftDent beams unreachable · empty ≠ $0"
        : o.hard
          ? "HARD FAIL · no live signal · empty ≠ $0"
          : "SOFT FAIL · fetch interrupted · empty ≠ $0");
    rail.appendChild(msg);
    if (o.detail) {
      const d = document.createElement("span");
      d.className = "nr2-error-rail-detail";
      d.textContent = " · " + String(o.detail);
      rail.appendChild(d);
    }
    if (!o.hard && typeof o.onRetry === "function") {
      mountRetryChip(rail, {
        onRetry: o.onRetry,
        countdownSec: o.countdownSec != null ? o.countdownSec : 8,
        label: o.retryLabel || "Retry",
      });
    }
    announce(msg.textContent);
    return rail;
  }
  function bindOfflineRail(onRetry) {
    if (document._nr2OfflineBound) return;
    document._nr2OfflineBound = true;
    window.addEventListener("offline", function () {
      showPageError({
        message: "OFFLINE · SoftDent / Trellis beams paused · empty ≠ $0",
        onRetry: onRetry,
        countdownSec: 12,
      });
      setBanner("unavailable", "browser offline · empty ≠ $0");
    });
    window.addEventListener("online", function () {
      hideErrorRail();
      if (typeof onRetry === "function") {
        showPageError({
          message: "BACK ONLINE · refreshing beams…",
          onRetry: onRetry,
          countdownSec: 2,
        });
      }
    });
  }
  function setText(id, value, emptyLabel) {
    const el = document.getElementById(id);
    if (!el) return;
    const wasLoading = el.classList.contains("is-loading");
    clearLoadingFace(el);
    clearErrorFace(el);
    el.classList.remove("empty", "zero", "nosignal");
    if (value == null || value === "") {
      const label = emptyLabel || "—";
      el.textContent = label;
      el.classList.add("empty");
      if (/no signal/i.test(label)) el.classList.add("nosignal");
      if (/^\$?\s*0(\.0+)?$/i.test(String(label).trim())) {
        el.textContent = "Empty ≠ $0";
      }
      if (wasLoading) pulseFaceSettle(el);
      maybeAnnounceEmpty(el.textContent);
      return;
    }
    const raw = String(value).trim();
    // Never paint attested-looking $0.00 — empty ≠ $0.
    if (/^\$?\s*0(\.0+)?$/.test(raw)) {
      el.textContent = "Empty ≠ $0";
      el.classList.add("empty");
      if (wasLoading) pulseFaceSettle(el);
      maybeAnnounceEmpty(el.textContent);
      return;
    }
    el.textContent = value;
    if (wasLoading) pulseFaceSettle(el);
  }
  function prefersReducedMotion() {
    try {
      return !!(
        window.matchMedia &&
        window.matchMedia("(prefers-reduced-motion: reduce)").matches
      );
    } catch (_) {
      return false;
    }
  }
  function pulseFaceSettle(elOrId) {
    const el = typeof elOrId === "string" ? document.getElementById(elOrId) : elOrId;
    if (!el || prefersReducedMotion()) return;
    el.classList.remove("nr2-face-settle");
    void el.offsetWidth;
    el.classList.add("nr2-face-settle");
    // Moonshot P5: physical lift on parent glass face during data refresh
    const face =
      (el.closest && el.closest(".metric-face, .beam-face")) ||
      (el.classList && (el.classList.contains("metric-face") || el.classList.contains("beam-face"))
        ? el
        : null);
    if (face) {
      face.classList.add("nr2-face-lift");
      window.setTimeout(function () {
        face.classList.remove("nr2-face-lift");
      }, 420);
    }
    window.setTimeout(function () {
      el.classList.remove("nr2-face-settle");
    }, 400);
  }
  /** Moonshot P1: grain atmosphere on every optical shell */
  function bootAtmosphere() {
    document.querySelectorAll(".shell").forEach(function (el) {
      el.classList.add("atmosphere");
    });
    return true;
  }
  function markRowsEnter(nodes, staggerMs) {
    if (prefersReducedMotion()) return 0;
    const list = nodes && nodes.length != null ? Array.prototype.slice.call(nodes) : [];
    const step = typeof staggerMs === "number" ? staggerMs : 18;
    list.forEach(function (el, i) {
      if (!el || !el.classList) return;
      el.classList.add("nr2-row-enter");
      el.style.setProperty("--nr2-stagger", Math.min(i, 16) * step + "ms");
    });
    return list.length;
  }
  function bootMotionGrammar() {
    if (document.documentElement.getAttribute("data-nr2-motion") === "off") return false;
    if (prefersReducedMotion()) {
      document.documentElement.classList.add("nr2-reduced-motion");
      document.documentElement.classList.remove("nr2-motion");
      return false;
    }
    document.documentElement.classList.add("nr2-motion");
    document.documentElement.classList.remove("nr2-reduced-motion");
    const main = document.querySelector(".shell > .main, main.main");
    if (main) main.classList.add("nr2-motion-enter");
    const faces = document.querySelectorAll(
      ".money-strip .metric-face, .align-bench .beam-face, .metric-face"
    );
    faces.forEach(function (el, i) {
      el.classList.add("nr2-face-enter");
      el.style.setProperty("--nr2-stagger", Math.min(i, 8) * 40 + "ms");
    });
    return true;
  }
  function ensureLiveRegion() {
    let el = document.getElementById("nr2-a11y-live");
    if (el) return el;
    el = document.createElement("div");
    el.id = "nr2-a11y-live";
    el.className = "nr2-sr-only";
    el.setAttribute("role", "status");
    el.setAttribute("aria-live", "polite");
    el.setAttribute("aria-atomic", "true");
    document.body.appendChild(el);
    return el;
  }
  let announceTimer = null;
  function announce(msg, opts) {
    const text = String(msg || "").trim();
    if (!text) return;
    const el = ensureLiveRegion();
    const delay = opts && opts.immediate ? 0 : 40;
    if (announceTimer) clearTimeout(announceTimer);
    el.textContent = "";
    announceTimer = setTimeout(function () {
      el.textContent = text;
    }, delay);
  }
  let lastEmptyAnnounce = "";
  function maybeAnnounceEmpty(label) {
    const t = String(label || "").trim();
    if (!t) return;
    if (!/empty|∅|no signal|Empty/i.test(t) && t !== "—") return;
    if (t === "—" || t === "∅") return; // too noisy for every face
    if (t === lastEmptyAnnounce) return;
    lastEmptyAnnounce = t;
    announce(t);
  }
  function focusMainHeading(opts) {
    const o = opts || {};
    const h1 =
      document.querySelector(".main h1") ||
      document.querySelector("main h1") ||
      document.querySelector("h1");
    if (!h1) return null;
    if (!h1.hasAttribute("tabindex")) h1.setAttribute("tabindex", "-1");
    try {
      h1.focus({ preventScroll: !!o.preventScroll });
    } catch (_) {
      try {
        h1.focus();
      } catch (_) {
        /* ignore */
      }
    }
    if (o.announce !== false) {
      const label = String(h1.textContent || "").trim() || "Page";
      announce(label + " · empty ≠ $0");
    }
    return h1;
  }
  function getFocusable(root) {
    if (!root) return [];
    const sel =
      'a[href], button:not([disabled]), textarea:not([disabled]), input:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])';
    return Array.prototype.slice.call(root.querySelectorAll(sel)).filter(function (el) {
      if (el.hasAttribute("disabled") || el.getAttribute("aria-hidden") === "true") return false;
      const style = window.getComputedStyle ? window.getComputedStyle(el) : null;
      if (style && (style.visibility === "hidden" || style.display === "none")) return false;
      return true;
    });
  }
  let focusTrapState = null;
  function releaseFocusTrap() {
    if (!focusTrapState) return null;
    document.removeEventListener("keydown", focusTrapState.onKey, true);
    const prev = focusTrapState.prev;
    const container = focusTrapState.container;
    if (container) {
      container.removeAttribute("aria-modal");
    }
    focusTrapState = null;
    if (prev && typeof prev.focus === "function") {
      try {
        prev.focus({ preventScroll: true });
      } catch (_) {
        try {
          prev.focus();
        } catch (_) {
          /* ignore */
        }
      }
    }
    return prev;
  }
  function trapFocus(container, opts) {
    const o = opts || {};
    if (!container) return null;
    releaseFocusTrap();
    const prev = document.activeElement;
    const onKey = function (e) {
      if (e.key === "Escape" && typeof o.onEscape === "function") {
        e.preventDefault();
        o.onEscape();
        return;
      }
      if (e.key !== "Tab") return;
      const list = getFocusable(container);
      if (!list.length) {
        e.preventDefault();
        return;
      }
      const first = list[0];
      const last = list[list.length - 1];
      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault();
        last.focus();
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault();
        first.focus();
      }
    };
    document.addEventListener("keydown", onKey, true);
    container.setAttribute("aria-modal", "true");
    focusTrapState = { container: container, onKey: onKey, prev: prev };
    const heading = container.querySelector("h1, h2, h3, [data-nr2-focus]");
    if (heading) {
      if (!heading.hasAttribute("tabindex")) heading.setAttribute("tabindex", "-1");
      try {
        heading.focus({ preventScroll: true });
      } catch (_) {
        heading.focus();
      }
    } else {
      const list = getFocusable(container);
      if (list[0]) list[0].focus();
    }
    if (o.announce) announce(o.announce);
    return focusTrapState;
  }
  function openFocusPanel(panel, opts) {
    if (!panel) return null;
    panel.hidden = false;
    return trapFocus(panel, opts);
  }
  function closeFocusPanel(panel) {
    if (panel) panel.hidden = true;
    return releaseFocusTrap();
  }
  /**
   * Money face honesty: null → empty label · 0 → "Empty ≠ $0" · else fmtMoney.
   * Never invent $0.00 for missing data.
   */
  function setMoneyText(id, amount, opts) {
    const o = opts || {};
    const v = money(amount);
    if (v == null) {
      setText(id, null, o.emptyLabel || "—");
      return { empty: true, live: false };
    }
    if (v === 0) {
      setText(id, null, o.zeroLabel || "Empty ≠ $0");
      const el = document.getElementById(id);
      if (el) el.classList.add("zero");
      return { empty: true, live: false, zeroish: true };
    }
    const shown = fmtMoney(v);
    setText(id, shown);
    return { empty: false, live: true, text: shown };
  }
  /** Surface SoftDent Excel Output Options probe (never fake Excel-ready). */
  async function applyExcelProbeHint(hintId, timeoutMs) {
    const el = hintId ? document.getElementById(hintId) : null;
    const r = await getJson("/api/softdent/excel-probe", timeoutMs || 8000);
    const data = r.ok ? r.data : null;
    const available = !!(data && data.excelAvailable === true);
    const bit = available
      ? "Excel Output Options available"
      : data && data.hasProbe
        ? "Excel Output Options blocked · morning bundle stays attest_only"
        : "Excel probe missing · do not invent export paths";
    if (el) {
      const prev = String(el.textContent || "").trim();
      el.textContent = (prev ? prev + " · " : "") + bit;
      el.classList.toggle("excel-blocked", !available);
    }
    let chip = document.getElementById("nr2-excel-probe-chip");
    if (!chip) {
      // Package 1: honesty is body LED — park chip after beam/compact header, not under fixed footer.
      const anchor =
        document.querySelector("main.main > .beam") ||
        document.querySelector("main.main > .exec-compact-header") ||
        document.querySelector("main.main .honesty, main.main .honesty-strip") ||
        document.querySelector(".honesty, .honesty-strip");
      if (anchor && anchor.parentNode) {
        chip = document.createElement("p");
        chip.id = "nr2-excel-probe-chip";
        chip.className = "excel-probe-chip";
        anchor.insertAdjacentElement("afterend", chip);
      }
    }
    if (chip) {
      chip.className = "excel-probe-chip " + (available ? "ok" : "blocked");
      chip.textContent =
        (available ? "EXCEL · READY" : "EXCEL · BLOCKED") + " · empty ≠ $0 · never Printer/File";
    }
    return { ok: !!r.ok, excelAvailable: available, data: data };
  }
  /** Board-safe hash chip · "#a7f3" (never invent). */
  function shortHash(h, len) {
    const s = String(h || "")
      .replace(/^#/, "")
      .trim();
    if (!s) return "—";
    const n = typeof len === "number" && len > 0 ? len : 4;
    return "#" + s.slice(0, n);
  }
  /** "Jane Doe" → "J.D." · empty → "P—". */
  function initialsFromName(name) {
    const parts = String(name || "")
      .trim()
      .split(/\s+/)
      .filter(Boolean);
    if (!parts.length) return "P—";
    const letters = parts
      .slice(0, 2)
      .map(function (p) {
        return p.charAt(0).toUpperCase();
      })
      .filter(Boolean);
    if (!letters.length) return "P—";
    if (letters.length === 1) return letters[0] + ".";
    return letters[0] + "." + letters[1] + ".";
  }
  /** Prefer API initials; normalize "JD—" → "J.D."; never invent from hash. */
  function formatPhiInitials(obj) {
    const raw = String((obj && obj.initials) || "").trim();
    if (raw) {
      const compact = raw
        .replace(/[—\-\s_.]/g, "")
        .toUpperCase();
      if (/^[A-Z]{1,3}$/.test(compact)) {
        if (compact.length === 1) return compact + ".";
        return compact[0] + "." + compact[1] + ".";
      }
      return raw;
    }
    const name = String((obj && (obj.patientName || obj.name)) || "").trim();
    if (name) return initialsFromName(name);
    return "P—";
  }
  /**
   * Default board label: "J.D. #a7f3". Never returns a full First Last string.
   * Pass { reveal: true } only after an explicit staff reveal action.
   */
  function formatPhiLabel(obj, opts) {
    const o = opts || {};
    if (o.reveal) {
      const full = String((obj && (obj.patientName || obj.name)) || "").trim();
      if (full) return full;
    }
    const ini = formatPhiInitials(obj);
    const hash = shortHash(
      (obj && (obj.patientHash || obj.nameHash || obj.hash)) || ""
    );
    if (hash === "—") return ini;
    return ini + " " + hash;
  }
  /** Frosted PHI chip into el (initials + hash spans). */
  function fillPhiCard(el, obj, opts) {
    if (!el) return null;
    const o = opts || {};
    el.classList.add("phi-card");
    el.textContent = "";
    const label = document.createElement("span");
    label.className = "phi-label";
    const ini = document.createElement("span");
    ini.className = "phi-initials";
    ini.textContent = formatPhiInitials(obj);
    const hash = document.createElement("span");
    hash.className = "phi-hash";
    hash.textContent = shortHash(
      (obj && (obj.patientHash || obj.nameHash || obj.hash)) || ""
    );
    label.appendChild(ini);
    label.appendChild(document.createTextNode(" "));
    label.appendChild(hash);
    el.appendChild(label);
    if (o.title !== false) {
      el.title = formatPhiLabel(obj) + " · PHI glass · empty ≠ $0";
    }
    return el;
  }
  /** Compact sample list of PHI cards (SoftDent / AR faces). */
  function fillPhiSampleList(el, claims, limit) {
    if (!el) return 0;
    el.textContent = "";
    el.classList.add("phi-sample");
    const eyebrow = document.createElement("p");
    eyebrow.className = "mode-eyebrow";
    eyebrow.textContent = "PHI glass · open claims sample";
    el.appendChild(eyebrow);
    const list = Array.isArray(claims) ? claims : [];
    const n = typeof limit === "number" && limit > 0 ? limit : 6;
    const slice = list.slice(0, n);
    if (!slice.length) {
      const empty = document.createElement("p");
      empty.className = "phi-sample-empty";
      empty.textContent = "No open claim sample · empty ≠ $0 · initials+hash only";
      el.appendChild(empty);
      return 0;
    }
    const ul = document.createElement("ul");
    ul.className = "phi-sample-list";
    slice.forEach(function (c) {
      const li = document.createElement("li");
      li.className = "phi-sample-row";
      fillPhiCard(li, c);
      const meta = document.createElement("span");
      meta.className = "phi-sample-meta";
      const amt =
        c && c.amount != null && Number.isFinite(Number(c.amount))
          ? fmtMoney(Number(c.amount))
          : null;
      meta.textContent =
        String((c && c.payer) || "—").slice(0, 18) +
        (amt ? " · " + amt : " · ∅");
      li.appendChild(meta);
      ul.appendChild(li);
    });
    el.appendChild(ul);
    const note = document.createElement("p");
    note.className = "phi-sample-note";
    note.textContent =
      "PHI glass · " +
      slice.length +
      " of " +
      list.length +
      " · initials+hash only · no SoftDent write-back";
    el.appendChild(note);
    return slice.length;
  }
  async function getJson(path, timeoutMs) {
    const ctrl = typeof AbortController !== "undefined" ? new AbortController() : null;
    const timer = ctrl && timeoutMs ? setTimeout(() => ctrl.abort(), timeoutMs) : null;
    try {
      const res = await fetch(path, {
        cache: "no-store",
        headers: { Accept: "application/json" },
        signal: ctrl ? ctrl.signal : undefined,
      });
      let data = null;
      try {
        data = await res.json();
      } catch (_) {
        data = null;
      }
      return { ok: res.ok, status: res.status, data: data };
    } catch (err) {
      return { ok: false, status: 0, data: { error: String(err && err.message ? err.message : err) } };
    } finally {
      if (timer) clearTimeout(timer);
    }
  }
  let sessionToken = "";
  async function ensureSession() {
    const r = await getJson("/api/browser-session", 8000);
    if (r.ok && r.data && r.data.sessionToken) {
      sessionToken = String(r.data.sessionToken);
      return true;
    }
    return false;
  }
  async function postJson(path, body, timeoutMs) {
    if (!sessionToken) await ensureSession();
    const ctrl = typeof AbortController !== "undefined" ? new AbortController() : null;
    const timer = ctrl && timeoutMs ? setTimeout(() => ctrl.abort(), timeoutMs) : null;
    try {
      const res = await fetch(path, {
        method: "POST",
        cache: "no-store",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
          ...(sessionToken ? { "X-NR2-Session-Token": sessionToken } : {}),
        },
        body: JSON.stringify(body || {}),
        signal: ctrl ? ctrl.signal : undefined,
      });
      let data = null;
      try {
        data = await res.json();
      } catch (_) {
        data = null;
      }
      return { ok: res.ok, status: res.status, data: data };
    } catch (err) {
      return { ok: false, status: 0, data: { error: String(err && err.message ? err.message : err) } };
    } finally {
      if (timer) clearTimeout(timer);
    }
  }
  let cachedBuildId = "";
  async function resolveBuildId() {
    if (cachedBuildId) return cachedBuildId;
    const r = await getJson("/api/app-info", 6000);
    const id =
      r.ok && r.data
        ? String(r.data.buildId || r.data.BUILD_ID || r.data.assetVersion || "").trim()
        : "";
    cachedBuildId = id || "nr2-optical";
    return cachedBuildId;
  }
  function setBanner(mode, detail) {
    const banner = document.querySelector(".banner");
    if (!banner) return;
    const label =
      mode === "live" ? "LIVE" : mode === "partial" ? "PARTIAL" : mode === "unavailable" ? "UNAVAILABLE" : "WIRE";
    const stamp = cachedBuildId || "nr2-optical";
    banner.classList.remove("live", "partial", "unavailable");
    if (mode === "live" || mode === "partial" || mode === "unavailable") {
      banner.classList.add(mode);
    }
    banner.childNodes[0] && banner.childNodes[0].nodeType === 3
      ? (banner.childNodes[0].textContent =
          label + " · optical · " + stamp + " · empty ≠ $0 · no SoftDent write-back ")
      : null;
    const bind = banner.querySelector(".bind");
    if (bind && detail) bind.textContent = detail;
    if (!cachedBuildId) {
      resolveBuildId().then(function (id) {
        if (!banner.childNodes[0] || banner.childNodes[0].nodeType !== 3) return;
        banner.childNodes[0].textContent =
          label + " · optical · " + id + " · empty ≠ $0 · no SoftDent write-back ";
      });
    }
  }
  function lasersRed(ready) {
    if (!ready || typeof ready !== "object") return false;
    const lasers = ready.alignmentLasers || {};
    const blocking = Array.isArray(ready.blocking) ? ready.blocking : [];
    if (lasers.red === true) return true;
    if (lasers.red === false) return false;
    return blocking.length > 0 || ready.ok === false;
  }
  function laserKeys(ready) {
    const lasers = ready && ready.alignmentLasers;
    if (lasers && Array.isArray(lasers.datasetKeys) && lasers.datasetKeys.length) {
      return lasers.datasetKeys.map(String);
    }
    return (ready && Array.isArray(ready.blocking) ? ready.blocking : [])
      .map(function (b) {
        return b && b.datasetKey ? String(b.datasetKey) : "";
      })
      .filter(Boolean);
  }
  function keysHit(keys, prefixes) {
    return (keys || []).some(function (k) {
      return prefixes.some(function (p) {
        return k === p || k.indexOf(p) === 0;
      });
    });
  }
  function bannerModeFromReady(ready, hasLiveSignal) {
    if (lasersRed(ready)) return "partial";
    return hasLiveSignal ? "live" : "partial";
  }
  /** HAL-shaped SoftDent/QB money honesty — never treat $0 as live data. */
  function honestyMoney(hasData, display) {
    if (!hasData) return { text: "NO SIGNAL", empty: true };
    const d = String(display || "").trim();
    if (!d || /^[∅⊘]|no signal|unavailable/i.test(d)) {
      return { text: "NO SIGNAL", empty: true };
    }
    if (/^\$?\s*0(\.0+)?$/.test(d)) {
      return { text: "empty (not zero)", empty: true };
    }
    return { text: d, empty: false };
  }
  async function getMoneyBeams(timeoutMs) {
    return getJson("/api/hal/tools/money-beams", timeoutMs || 12000);
  }
  /**
   * Apply SoftDent or QB attested headline from money-beams.
   * When lasers red / importStale: suppress dollars (empty ≠ $0).
   */
  function applyBeamHeadline(opts) {
    const id = opts && opts.id;
    const hintId = opts && opts.hintId;
    const beams = opts && opts.beams;
    const ready = opts && opts.ready;
    const side = opts && opts.side; // "softdent" | "quickbooks"
    const el = id ? document.getElementById(id) : null;
    if (!el) return { applied: false, live: false };

    const lasers = lasersRed(ready);
    const staleBeam = !!(beams && beams.importStale);
    const block = lasers || staleBeam;
    const sideObj =
      beams && side === "quickbooks"
        ? beams.quickbooks
        : beams && beams.softdent
          ? beams.softdent
          : null;

    if (block) {
      setText(id, null, lasers ? "STALE / ∅" : "NO SIGNAL");
      el.classList.add("stale");
      if (hintId) {
        const hint = document.getElementById(hintId);
        if (hint) {
          hint.textContent =
            "Lasers/import STALE · empty ≠ $0 · hash " +
            String((beams && beams.beamHash) || "n/a").slice(0, 16);
        }
      }
      return { applied: true, live: false, blocked: true };
    }

    if (!beams || !sideObj) {
      return { applied: false, live: false };
    }

    const h = honestyMoney(!!sideObj.hasData, sideObj.display);
    if (h.empty) {
      setText(id, null, h.text);
      return { applied: true, live: false };
    }
    setText(id, h.text);
    el.classList.remove("stale");
    if (hintId) {
      const hint = document.getElementById(hintId);
      if (hint) {
        const ts = String(beams.beamTimestamp || beams.at || "").slice(0, 19);
        const sideLabel = side === "quickbooks" ? "QuickBooks" : "SoftDent";
        hint.textContent =
          sideLabel +
          (ts ? " · " + ts : "") +
          " · hash " +
          String(beams.beamHash || "n/a").slice(0, 16) +
          " · empty ≠ $0";
      }
    }
    return { applied: true, live: true, beamHash: beams.beamHash };
  }
  function beamProvenanceLine(beams, ready) {
    if (!beams) return "money-beams · NO SIGNAL";
    const close = ready && ready.periodClose;
    const parts = [
      "dataHash " + formatBeamHash(beams.dataBeamHash || beams.beamHash, 16),
      "beamHash " + formatBeamHash(beams.beamHash, 16),
      beams.beamTimestamp ? "at " + String(beams.beamTimestamp).slice(0, 19) : "",
      close && close.completedAt ? "close " + String(close.completedAt).slice(0, 19) : "",
    ].filter(Boolean);
    return parts.join(" · ");
  }
  function formatBeamHash(h, len) {
    const s = String(h || "").trim();
    if (!s) return "n/a";
    const n = typeof len === "number" && len > 0 ? len : 16;
    return s.slice(0, n);
  }
  function hashesMatch(a, b) {
    const x = String(a || "").trim().toLowerCase();
    const y = String(b || "").trim().toLowerCase();
    if (!x || !y || x === "n/a" || y === "n/a") return false;
    const n = Math.min(x.length, y.length, 16);
    return x.slice(0, n) === y.slice(0, n);
  }
  async function fetchBeamVerify(timeoutMs) {
    return getJson("/api/hal/tools/beam-verify", timeoutMs || 12000);
  }
  async function patientForceAttest(patientId, opts) {
    const o = opts || {};
    await ensureSession();
    return postJson(
      "/api/apex/patient-force-attest",
      {
        patientId: String(patientId || "").trim(),
        actor: o.actor || "optical-om",
        sessionId: o.sessionId || undefined,
      },
      o.timeoutMs || 20000
    );
  }
  async function patientForceAttestStatus(patientId, timeoutMs) {
    const pid = encodeURIComponent(String(patientId || "").trim());
    return getJson("/api/apex/patient-force-attest/" + pid, timeoutMs || 12000);
  }
  async function patientForceAttestEligible(timeoutMs) {
    return getJson("/api/apex/patient-force-attest/eligible", timeoutMs || 12000);
  }
  function bindVerifyBeamButton(btnId, opts) {
    const btn = document.getElementById(btnId || "btn-verify-beam");
    if (!btn || btn._nr2VerifyBound) return btn;
    btn._nr2VerifyBound = true;
    const o = opts || {};
    btn.disabled = false;
    btn.addEventListener("click", function () {
      if (btn.classList.contains("busy")) return;
      btn.classList.add("busy");
      btn.disabled = true;
      const label = btn.textContent;
      btn.textContent = "VERIFYING…";
      fetchBeamVerify(12000)
        .then(function (res) {
          const data = (res && res.data) || {};
          const live = data.live || {};
          const close = data.periodClose || {};
          const proof = String(data.deskProof || "NO SIGNAL");
          const liveData = formatBeamHash(live.dataBeamHash, 16);
          const closeData = formatBeamHash(close.dataBeamHash, 16);
          let driftBit = "";
          const drift = data.drift;
          if (drift && typeof drift === "object") {
            const parts = [];
            if (drift.softdentDisplay) {
              parts.push(
                "SD " + String(drift.softdentDisplay.close || "—") + "→" + String(drift.softdentDisplay.live || "—")
              );
            }
            if (drift.qbDisplay) {
              parts.push(
                "QB " + String(drift.qbDisplay.close || "—") + "→" + String(drift.qbDisplay.live || "—")
              );
            }
            if (parts.length) driftBit = " · drift " + parts.join(" · ");
          }
          const bit =
            "VERIFY BEAM · " +
            proof +
            " · live " +
            liveData +
            " · close " +
            closeData +
            driftBit +
            (data.refreshCloseSuggested ? " · re-close suggested" : "") +
            " · empty ≠ $0";
          if (typeof o.onDone === "function") {
            o.onDone({ ok: !!(res && res.ok && data.ok), res: res, bit: bit, data: data });
          } else if (typeof setBanner === "function") {
            setBanner(proof === "MATCH" ? "live" : "partial", bit);
          }
          if (o.hintId) {
            const hint = document.getElementById(o.hintId);
            if (hint) hint.textContent = bit;
          }
          if (o.valId) {
            const el = document.getElementById(o.valId);
            if (el) {
              el.textContent = proof;
              el.classList.remove("stale", "hal", "sd");
              el.classList.add(proof === "MATCH" ? "hal" : "stale");
            }
          }
        })
        .catch(function (err) {
          if (typeof setBanner === "function") {
            setBanner(
              "partial",
              "VERIFY BEAM · fault · " + String(err && err.message ? err.message : err)
            );
          }
        })
        .finally(function () {
          btn.classList.remove("busy");
          btn.textContent = label || "VERIFY BEAM";
          btn.disabled = false;
          if (typeof o.onFinally === "function") o.onFinally();
        });
    });
    return btn;
  }
  async function runDeskSmoke(opts) {
    const o = opts || {};
    const q = o.run === false || o.run === 0 ? "?run=0" : "?run=1";
    const probe = o.probeHttp === false ? "&probeHttp=0" : "&probeHttp=1";
    return getJson("/api/health/desk-smoke" + q + probe, o.timeoutMs || 60000);
  }
  function deskSmokeDriftBit(data) {
    const checks = (data && Array.isArray(data.checks) ? data.checks : []) || [];
    const proof = checks.find(function (c) {
      return c && c.id === "beam_desk_proof";
    });
    const drift = proof && proof.drift && typeof proof.drift === "object" ? proof.drift : null;
    if (!drift) return "";
    const sd = drift.softdentDisplay || drift.softdentTotal;
    if (!sd || typeof sd !== "object") return "";
    const close = sd.close != null ? String(sd.close) : "";
    const live = sd.live != null ? String(sd.live) : "";
    if (!close && !live) return "";
    return " · SoftDent close " + (close || "—") + " vs live " + (live || "—");
  }
  function formatDeskSmokeBit(data) {
    const d = data || {};
    const status = String(d.status || (d.ok ? "GREEN" : "RED")).toUpperCase();
    const fails = Array.isArray(d.failures) ? d.failures.join(",") : "";
    const thisPatient =
      d.thisPatientShortcutCovered === true
        ? " · this-patient OK"
        : d.thisPatientShortcutCovered === false
          ? " · this-patient gap"
          : "";
    return (
      "DESK SMOKE · " +
      status +
      (d.deskProof ? " · proof " + d.deskProof : "") +
      deskSmokeDriftBit(d) +
      (d.dataBeamHash ? " · data " + formatBeamHash(d.dataBeamHash, 8) : "") +
      thisPatient +
      (fails ? " · fail " + fails : "") +
      " · empty ≠ $0 · no SoftDent write-back"
    );
  }
  function paintDeskSmokeFace(data, opts) {
    const o = opts || {};
    const d = data || {};
    const status = String(d.status || (d.ok ? "GREEN" : "RED")).toUpperCase();
    const bit = formatDeskSmokeBit(d);
    if (o.valId) {
      const el = document.getElementById(o.valId);
      if (el) {
        el.textContent = status === "NO SIGNAL" ? "NO SIGNAL" : status;
        el.classList.remove("stale", "hal", "sd");
        el.classList.add(status === "GREEN" ? "hal" : "stale");
      }
    }
    if (o.hintId) {
      const hint = document.getElementById(o.hintId);
      if (hint) hint.textContent = bit;
    }
    return { status: status, bit: bit };
  }
  function bindDeskSmokeButton(btnId, opts) {
    const btn = document.getElementById(btnId || "btn-desk-smoke");
    if (!btn || btn._nr2SmokeBound) return btn;
    btn._nr2SmokeBound = true;
    const o = opts || {};
    btn.disabled = false;
    btn.addEventListener("click", function () {
      if (btn.classList.contains("busy")) return;
      btn.classList.add("busy");
      btn.disabled = true;
      const label = btn.textContent;
      btn.textContent = "SMOKING…";
      runDeskSmoke({ probeHttp: o.probeHttp !== false })
        .then(function (res) {
          const data = (res && res.data) || {};
          // Transport may be 200 with ok:false (honest RED / MISMATCH).
          const painted = paintDeskSmokeFace(data, { valId: o.valId, hintId: o.hintId });
          if (typeof setBanner === "function") {
            setBanner(painted.status === "GREEN" ? "live" : "partial", painted.bit);
          }
          if (typeof o.onDone === "function") o.onDone({ res: res, data: data, painted: painted });
        })
        .catch(function (err) {
          if (typeof setBanner === "function") {
            setBanner(
              "partial",
              "DESK SMOKE · fault · " + String(err && err.message ? err.message : err)
            );
          }
        })
        .finally(function () {
          btn.classList.remove("busy");
          btn.textContent = label || "RUN SMOKE";
          btn.disabled = false;
          if (typeof o.onFinally === "function") o.onFinally();
        });
    });
    return btn;
  }
  function periodCloseStatus(ready) {
    const close = ready && ready.periodClose;
    if (!close || typeof close !== "object") {
      const op = ready && ready.operationContext;
      if (op && op.activeOperation) {
        return { status: String(op.activeOperation), completedAt: null, lastBeamHash: null };
      }
      return null;
    }
    return {
      status: String(close.status || "unknown").toLowerCase(),
      completedAt: close.completedAt || null,
      lastBeamHash: close.lastBeamHash || null,
    };
  }
  function periodCloseIsTrouble(ready) {
    const pc = periodCloseStatus(ready);
    if (!pc) return false;
    return /^(stalled|blocked|running|daily_close)$/i.test(pc.status);
  }
  function periodCloseBannerBit(ready) {
    const pc = periodCloseStatus(ready);
    if (!pc) return "CLOSE · NO SIGNAL";
    const stamp = pc.completedAt ? String(pc.completedAt).slice(0, 16).replace("T", " ") : "";
    const hash = pc.lastBeamHash ? " · hash " + String(pc.lastBeamHash).slice(0, 8) : "";
    return (
      "CLOSE · " +
      String(pc.status || "unknown").toUpperCase() +
      (stamp ? " · " + stamp : "") +
      hash
    );
  }
  function forceCloseAvailable(ready) {
    const pc = periodCloseStatus(ready);
    const status = pc ? String(pc.status || "").toLowerCase() : "";
    if (status === "running" || status === "daily_close") return false;
    if (status === "stalled" || status === "blocked") return true;
    return lasersRed(ready);
  }
  async function forcePeriodClose(opts) {
    const o = opts || {};
    const body = {
      actor: o.actor || "optical-force-close",
    };
    if (typeof o.pullSoftdent === "boolean") body.pullSoftdent = o.pullSoftdent;
    return postJson("/api/period-close/force", body, o.timeoutMs || 180000);
  }
  function bindForceCloseButton(btnId, opts) {
    const btn = document.getElementById(btnId || "btn-force-close");
    if (!btn) return null;
    const o = opts || {};
    const ready = o.ready || null;
    const available = forceCloseAvailable(ready);
    btn.disabled = !available;
    btn.title = available
      ? "FORCE CLOSE · SoftDent pull when lasers red or close stalled; else attest-only · empty ≠ $0"
      : "FORCE CLOSE · available when lasers red or period-close stalled/blocked";
    if (btn._nr2ForceBound) return btn;
    btn._nr2ForceBound = true;
    btn.addEventListener("click", function () {
      if (btn.disabled || btn.classList.contains("busy")) return;
      btn.classList.add("busy");
      btn.disabled = true;
      const label = btn.textContent;
      btn.textContent = "CLOSING…";
      forcePeriodClose({ actor: o.actor || "optical-force-close" })
        .then(function (res) {
          const data = (res && res.data) || {};
          const hash = data.beamHash ? String(data.beamHash).slice(0, 12) : "n/a";
          const ok = !!(res && res.ok && data.ok);
          const bit =
            (ok ? "FORCE CLOSE · OK · hash " : "FORCE CLOSE · FAIL · ") +
            hash +
            (data.laserOverride ? " · laserOverride" : "") +
            " · empty ≠ $0";
          if (typeof o.onDone === "function") {
            o.onDone({ ok: ok, res: res, bit: bit, data: data });
          } else if (typeof setBanner === "function") {
            setBanner(ok ? "live" : "partial", bit);
          }
          if (o.hintId) {
            const hint = document.getElementById(o.hintId);
            if (hint) hint.textContent = bit;
          }
        })
        .catch(function (err) {
          if (typeof setBanner === "function") {
            setBanner("partial", "FORCE CLOSE · fault · " + String(err && err.message ? err.message : err));
          }
        })
        .finally(function () {
          btn.classList.remove("busy");
          btn.textContent = label || "FORCE CLOSE";
          // Re-enable only if still available after refresh callers handle re-boot.
          if (typeof o.onFinally === "function") o.onFinally();
          else btn.disabled = !forceCloseAvailable(o.ready);
        });
    });
    return btn;
  }
  function morningBundleGate(ready) {
    const bundle = ready && ready.periodClose && ready.periodClose.morningBundle;
    if (!bundle || typeof bundle !== "object") {
      return {
        id: "morning_bundle",
        label: "BUNDLE",
        status: "RED",
        detail: "No morning bundle signal · empty ≠ $0",
        value: "RED",
      };
    }
    if (bundle.ok) {
      return {
        id: "morning_bundle",
        label: "BUNDLE",
        status: "GREEN",
        detail:
          "Morning bundle ok" +
          (bundle.okCount != null ? " · " + bundle.okCount + " reports" : "") +
          " · empty ≠ $0",
        value: "GREEN",
      };
    }
    const err = String(bundle.error || bundle.detail || bundle.fallback || "not ok").slice(0, 72);
    return {
      id: "morning_bundle",
      label: "BUNDLE",
      status: "RED",
      detail: (bundle.fallback ? "FALLBACK · " : "") + err + " · empty ≠ $0",
      value: "RED",
    };
  }
  function trellisGate(proof) {
    if (!proof || typeof proof !== "object") {
      return {
        id: "trellis",
        label: "TRELLIS",
        status: "YELLOW",
        detail: "No Trellis AM proof signal",
        value: "—",
      };
    }
    if (proof.passed) {
      return {
        id: "trellis",
        label: "TRELLIS",
        status: "GREEN",
        detail: String(proof.chipLabel || "withBenefits > 0") + " · counts only",
        value: "GREEN",
      };
    }
    const chip = String(proof.chipStatus || "awaiting").toLowerCase();
    if (chip === "fault") {
      return {
        id: "trellis",
        label: "TRELLIS",
        status: "RED",
        detail: String(proof.chipLabel || "Trellis AM proof fault"),
        value: "RED",
      };
    }
    return {
      id: "trellis",
      label: "TRELLIS",
      status: "YELLOW",
      detail: String(proof.chipLabel || "awaiting nightly ClearCoverage scrape"),
      value: "YELLOW",
    };
  }
  function shadowGate(pilot) {
    if (!pilot || typeof pilot !== "object") {
      return {
        id: "shadow",
        label: "SHADOW",
        status: "YELLOW",
        detail: "No pilot shadow signal · systemOfRecord stays false",
        value: "—/30",
      };
    }
    const minDays = Number(pilot.minShadowDays);
    const min = Number.isFinite(minDays) && minDays > 0 ? minDays : 30;
    const elapsedRaw = pilot.shadowDaysElapsed;
    const elapsed = typeof elapsedRaw === "number" && Number.isFinite(elapsedRaw) ? elapsedRaw : null;
    const clock = (elapsed != null ? String(elapsed) : "—") + "/" + String(min);
    if (pilot.systemOfRecord) {
      return {
        id: "shadow",
        label: "SHADOW",
        status: "GREEN",
        detail: "systemOfRecord=true · phase " + String(pilot.phase || "cutover"),
        value: clock,
      };
    }
    const detail =
      "phase " +
      String(pilot.phase || "shadow") +
      " · " +
      clock +
      " days · systemOfRecord=false";
    return {
      id: "shadow",
      label: "SHADOW",
      status: "YELLOW",
      detail: detail,
      value: clock,
    };
  }
  function deriveOpsGates(ready, trellisProof, pilot) {
    return [morningBundleGate(ready), trellisGate(trellisProof), shadowGate(pilot)];
  }
  async function fetchOpsGates(timeoutMs) {
    const ms = timeoutMs || 12000;
    const [readyRes, trellisRes, appRes] = await Promise.all([
      getJson("/api/import-readiness", ms),
      getJson("/api/trellis/am-proof", ms),
      getJson("/api/app-info", ms),
    ]);
    const ready = readyRes.ok ? readyRes.data : null;
    const trellisProof = trellisRes.ok ? trellisRes.data : null;
    const pilot =
      appRes.ok && appRes.data && appRes.data.pilot && typeof appRes.data.pilot === "object"
        ? appRes.data.pilot
        : null;
    return {
      gates: deriveOpsGates(ready, trellisProof, pilot),
      ready: ready,
      trellisProof: trellisProof,
      pilot: pilot,
    };
  }
  function renderOpsGates(el, gates) {
    if (!el) return;
    const list = Array.isArray(gates) ? gates : [];
    el.innerHTML = list
      .map(function (g) {
        const status = String(g.status || "YELLOW").toUpperCase();
        const tone =
          status === "GREEN" ? "green" : status === "RED" ? "red" : status === "FAULT" ? "red" : "yellow";
        const pulse = status === "RED" ? " pulse" : "";
        return (
          '<span class="nr2-ops-gate tone-' +
          tone +
          pulse +
          '" data-gate="' +
          String(g.id || "") +
          '" title="' +
          String(g.detail || "").replace(/"/g, "&quot;") +
          '">' +
          '<span class="lbl">' +
          String(g.label || g.id || "GATE") +
          "</span>" +
          '<span class="val">' +
          String(g.value || status) +
          "</span>" +
          "</span>"
        );
      })
      .join("");
  }
  let opsGatesTimer = null;
  function mountOpsGates(opts) {
    const o = opts || {};
    if (document.documentElement.getAttribute("data-nr2-ops-gates") === "off") return null;
    let bar = document.getElementById("nr2-ops-gates");
    if (!bar) {
      bar = document.createElement("div");
      bar.id = "nr2-ops-gates";
      bar.className = "nr2-ops-gates";
      bar.setAttribute("role", "status");
      bar.setAttribute("aria-live", "polite");
      bar.setAttribute("aria-label", "Ops gates · morning bundle · Trellis · shadow clock");
      bar.innerHTML =
        '<span class="nr2-ops-gate tone-yellow"><span class="lbl">OPS</span><span class="val">…</span></span>';
      const banner = document.querySelector(".banner");
      if (banner && banner.parentNode) {
        banner.insertAdjacentElement("afterend", bar);
      } else if (document.body.firstChild) {
        document.body.insertBefore(bar, document.body.firstChild);
      } else {
        document.body.appendChild(bar);
      }
    }
    document.body.classList.add("has-ops-gates");
    const refresh = function () {
      return fetchOpsGates(o.timeoutMs || 12000).then(function (pack) {
        renderOpsGates(bar, pack.gates);
        if (typeof o.onDone === "function") o.onDone(pack);
        return pack;
      });
    };
    refresh();
    const ms = o.refreshMs == null ? 60000 : Number(o.refreshMs);
    if (opsGatesTimer) {
      clearInterval(opsGatesTimer);
      opsGatesTimer = null;
    }
    if (ms > 0) {
      opsGatesTimer = setInterval(refresh, ms);
    }
    return bar;
  }
  /** Package 9: print header + PHI scrub (initials+hash → REDACTED) + optional row breaks. */
  function ensurePrintHeader() {
    let el = document.getElementById("nr2-print-header");
    if (el) return el;
    el = document.createElement("div");
    el.id = "nr2-print-header";
    el.className = "nr2-print-header";
    el.setAttribute("aria-hidden", "true");
    el.textContent =
      "NewRidge Financial — Confidential · SoftDent READ-ONLY · empty ≠ $0 · no write-back";
    document.body.insertBefore(el, document.body.firstChild);
    return el;
  }
  function redactPhiForPrint() {
    const sel =
      ".phi-hash, .phi-name, td.phi-name, .wk-slot .phi, .phi-card .phi-label, .phi-sample-row .phi-label";
    document.querySelectorAll(sel).forEach(function (el) {
      if (!el || el.getAttribute("data-nr2-print-orig") != null) return;
      const hashChild = el.querySelector && el.querySelector(".phi-hash");
      if (hashChild && !hashChild.getAttribute("data-nr2-print-orig")) {
        hashChild.setAttribute("data-nr2-print-orig", hashChild.textContent || "");
        hashChild.textContent = "REDACTED";
        hashChild.classList.add("nr2-print-redacted");
        if (el.getAttribute("title")) {
          el.setAttribute("data-nr2-print-title", el.getAttribute("title"));
          el.removeAttribute("title");
        }
        return;
      }
      el.setAttribute("data-nr2-print-orig", el.textContent || "");
      if (el.getAttribute("title")) {
        el.setAttribute("data-nr2-print-title", el.getAttribute("title"));
        el.removeAttribute("title");
      }
      el.textContent = "REDACTED";
      el.classList.add("nr2-print-redacted");
    });
  }
  function restorePhiAfterPrint() {
    document.querySelectorAll("[data-nr2-print-orig]").forEach(function (el) {
      el.textContent = el.getAttribute("data-nr2-print-orig") || "";
      el.removeAttribute("data-nr2-print-orig");
      el.classList.remove("nr2-print-redacted");
      if (el.hasAttribute("data-nr2-print-title")) {
        el.setAttribute("title", el.getAttribute("data-nr2-print-title"));
        el.removeAttribute("data-nr2-print-title");
      }
    });
  }
  function markPrintPageBreaks(selector, everyN) {
    document.querySelectorAll(".nr2-print-break").forEach(function (el) {
      el.classList.remove("nr2-print-break");
    });
    if (!selector) return 0;
    const n = typeof everyN === "number" && everyN > 0 ? everyN : 25;
    const rows = document.querySelectorAll(selector);
    let marked = 0;
    rows.forEach(function (el, i) {
      if (i > 0 && i % n === 0) {
        el.classList.add("nr2-print-break");
        marked += 1;
      }
    });
    return marked;
  }
  function ensurePrintExecutiveChrome() {
    ensurePrintHeader();
    if (!document.getElementById("nr2-exec-print-watermark")) {
      const w = document.createElement("div");
      w.id = "nr2-exec-print-watermark";
      w.className = "exec-print-watermark";
      w.setAttribute("aria-hidden", "true");
      w.textContent = "CONFIDENTIAL";
      document.body.appendChild(w);
    }
    if (!document.getElementById("nr2-exec-print-fold")) {
      const f = document.createElement("div");
      f.id = "nr2-exec-print-fold";
      f.className = "exec-print-fold";
      f.setAttribute("aria-hidden", "true");
      document.body.appendChild(f);
    }
    if (!document.getElementById("nr2-exec-print-signline")) {
      const s = document.createElement("div");
      s.id = "nr2-exec-print-signline";
      s.className = "exec-print-signline";
      s.setAttribute("aria-hidden", "true");
      s.textContent =
        "Authorized signature ____________________________ · NewRidge Financial — Confidential · empty ≠ $0";
      const main = document.querySelector(".main") || document.body;
      main.appendChild(s);
    }
    return true;
  }
  function bindPrintHygiene(opts) {
    document._nr2PrintOpts = opts || {};
    ensurePrintHeader();
    ensurePrintExecutiveChrome();
    if (document._nr2PrintBound) return true;
    document._nr2PrintBound = true;
    window.addEventListener("beforeprint", function () {
      const cfg = document._nr2PrintOpts || {};
      redactPhiForPrint();
      ensurePrintExecutiveChrome();
      if (cfg.breakSelector) {
        markPrintPageBreaks(cfg.breakSelector, cfg.breakEvery);
      }
    });
    window.addEventListener("afterprint", function () {
      restorePhiAfterPrint();
      document.querySelectorAll(".nr2-print-break").forEach(function (el) {
        el.classList.remove("nr2-print-break");
      });
    });
    return true;
  }
  /** Moonshot E1–E4: letterhead, seals, currency emboss, desk surface on every optical page. */
  function bootExecutiveChrome() {
    document.body.classList.add("exec-desk-surface");
    const banner = document.querySelector(".banner");
    if (banner && !document.getElementById("nr2-exec-letterhead")) {
      const lh = document.createElement("header");
      lh.id = "nr2-exec-letterhead";
      lh.className = "exec-letterhead exec-practice-header";
      lh.setAttribute("aria-label", "Executive letterhead");
      lh.innerHTML =
        '<div><span class="exec-practice-name">NewRidge Family Financial</span>' +
        '<div class="type-laser" style="margin-top:2px;font-size:11px;color:var(--muted)">Optical desk · SoftDent READ-ONLY</div></div>' +
        '<div>CFO / Controller · <span class="cfo-initials" id="nr2-cfo-initials">NR</span></div>' +
        '<div class="exec-period-seal period-seal" id="nr2-period-seal">Period close · —</div>';
      banner.insertAdjacentElement("afterend", lh);
    }
    document
      .querySelectorAll(
        ".metric-face .val, .metric-face .face-val, .beam-face .face-val, .hal-beam-val"
      )
      .forEach(function (el) {
        el.classList.add("exec-currency");
      });
    document.querySelectorAll(".ledge").forEach(function (ledge) {
      if (ledge.querySelector(".exec-signature-block")) return;
      const sig = document.createElement("div");
      sig.className = "exec-signature-block";
      sig.textContent = "Sign / attest · empty ≠ $0 · no SoftDent write-back";
      ledge.appendChild(sig);
    });
    document.querySelectorAll(".money-strip").forEach(function (strip) {
      if (strip.closest(".ledge")) return;
      if (strip.parentNode && strip.parentNode.querySelector(".exec-signature-block")) return;
      const sig = document.createElement("div");
      sig.className = "exec-signature-block";
      sig.textContent = "Sign / attest · empty ≠ $0 · no SoftDent write-back";
      strip.insertAdjacentElement("afterend", sig);
    });
    // Refresh period seal from readiness when available (non-blocking).
    getJson("/api/import-readiness", 6000).then(function (r) {
      const seal = document.getElementById("nr2-period-seal");
      if (!seal) return;
      const pc = periodCloseStatus(r.ok ? r.data : null);
      const bit = periodCloseBannerBit(r.ok ? r.data : null);
      seal.textContent = bit || (pc && pc.status ? "Period close · " + String(pc.status) : "Period close · —");
      if (periodCloseIsTrouble(r.ok ? r.data : null)) {
        seal.classList.add("exec-brass-accent");
      }
    });
    return true;
  }
  function bootOpsGates() {
    try {
      mountOpsGates({ refreshMs: 60000 });
    } catch (_) {
      /* ignore mount faults — page faces still load */
    }
    try {
      bootAtmosphere();
    } catch (_) {
      /* atmosphere optional */
    }
    try {
      bootExecutiveChrome();
    } catch (_) {
      /* executive chrome optional */
    }
    try {
      bootMotionGrammar();
    } catch (_) {
      /* motion optional */
    }
    try {
      bindPrintHygiene();
    } catch (_) {
      /* print hygiene optional */
    }
  }
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", bootOpsGates);
  } else {
    bootOpsGates();
  }
  global.NR2OpticalWire = {
    money: money,
    fmtMoney: fmtMoney,
    setText: setText,
    setLoading: setLoading,
    markFacesLoading: markFacesLoading,
    clearLoadingFace: clearLoadingFace,
    clearErrorFace: clearErrorFace,
    isBrowserOffline: isBrowserOffline,
    setErrorState: setErrorState,
    mountRetryChip: mountRetryChip,
    showPageError: showPageError,
    hideErrorRail: hideErrorRail,
    bindOfflineRail: bindOfflineRail,
    setMoneyText: setMoneyText,
    applyExcelProbeHint: applyExcelProbeHint,
    prefersReducedMotion: prefersReducedMotion,
    pulseFaceSettle: pulseFaceSettle,
    markRowsEnter: markRowsEnter,
    bootMotionGrammar: bootMotionGrammar,
    bootAtmosphere: bootAtmosphere,
    announce: announce,
    focusMainHeading: focusMainHeading,
    getFocusable: getFocusable,
    trapFocus: trapFocus,
    releaseFocusTrap: releaseFocusTrap,
    openFocusPanel: openFocusPanel,
    closeFocusPanel: closeFocusPanel,
    shortHash: shortHash,
    initialsFromName: initialsFromName,
    formatPhiInitials: formatPhiInitials,
    formatPhiLabel: formatPhiLabel,
    fillPhiCard: fillPhiCard,
    fillPhiSampleList: fillPhiSampleList,
    getJson: getJson,
    postJson: postJson,
    ensureSession: ensureSession,
    setBanner: setBanner,
    resolveBuildId: resolveBuildId,
    lasersRed: lasersRed,
    laserKeys: laserKeys,
    keysHit: keysHit,
    bannerModeFromReady: bannerModeFromReady,
    honestyMoney: honestyMoney,
    getMoneyBeams: getMoneyBeams,
    applyBeamHeadline: applyBeamHeadline,
    beamProvenanceLine: beamProvenanceLine,
    periodCloseStatus: periodCloseStatus,
    periodCloseIsTrouble: periodCloseIsTrouble,
    periodCloseBannerBit: periodCloseBannerBit,
    forceCloseAvailable: forceCloseAvailable,
    forcePeriodClose: forcePeriodClose,
    bindForceCloseButton: bindForceCloseButton,
    formatBeamHash: formatBeamHash,
    hashesMatch: hashesMatch,
    fetchBeamVerify: fetchBeamVerify,
    patientForceAttest: patientForceAttest,
    patientForceAttestStatus: patientForceAttestStatus,
    patientForceAttestEligible: patientForceAttestEligible,
    bindVerifyBeamButton: bindVerifyBeamButton,
    runDeskSmoke: runDeskSmoke,
    bindDeskSmokeButton: bindDeskSmokeButton,
    paintDeskSmokeFace: paintDeskSmokeFace,
    formatDeskSmokeBit: formatDeskSmokeBit,
    morningBundleGate: morningBundleGate,
    trellisGate: trellisGate,
    shadowGate: shadowGate,
    deriveOpsGates: deriveOpsGates,
    fetchOpsGates: fetchOpsGates,
    renderOpsGates: renderOpsGates,
    mountOpsGates: mountOpsGates,
    ensurePrintHeader: ensurePrintHeader,
    redactPhiForPrint: redactPhiForPrint,
    restorePhiAfterPrint: restorePhiAfterPrint,
    markPrintPageBreaks: markPrintPageBreaks,
    bindPrintHygiene: bindPrintHygiene,
    bootExecutiveChrome: bootExecutiveChrome,
    ensurePrintExecutiveChrome: ensurePrintExecutiveChrome,
  };
})(window);
