/* nr2 optical landing — money fusion bench (CSP script-src 'self') */
(function () {
  const toast = (msg) => {
    const el = document.getElementById("toast");
    if (!el) return;
    el.textContent = msg;
    el.classList.add("show");
    setTimeout(() => el.classList.remove("show"), 2800);
  };

  let sessionToken = "";
  let role = "om";
  let syncBusy = false;
  let selectedPeriod = "60";
  let lastReady = null;
  let lastSessionOk = false;
  let coreSyncMode = null;

  function lasersRed(ready) {
    if (!ready || typeof ready !== "object") return true;
    const lasers = ready.alignmentLasers || {};
    const blocking = Array.isArray(ready.blocking) ? ready.blocking : [];
    if (lasers.red === true) return true;
    if (lasers.red === false) return false;
    return ready.ok === false || blocking.length > 0;
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

  function periodCloseTrouble(ready) {
    const W = window.NR2OpticalWire;
    if (W && typeof W.periodCloseIsTrouble === "function") {
      return !!W.periodCloseIsTrouble(ready);
    }
    const close = ready && ready.periodClose;
    const status = close && close.status ? String(close.status) : "";
    return /^(stalled|blocked|running|daily_close)$/i.test(status);
  }

  function periodCloseBit(ready) {
    const W = window.NR2OpticalWire;
    if (W && typeof W.periodCloseBannerBit === "function") {
      return W.periodCloseBannerBit(ready);
    }
    if (!ready || !ready.periodClose) return "CLOSE · NO SIGNAL";
    return "CLOSE · " + String(ready.periodClose.status || "unknown").toUpperCase();
  }

  function applyWireHonesty(ready, sessionOk) {
    lastReady = ready || null;
    if (sessionOk != null) lastSessionOk = !!sessionOk;
    if (!ready) {
      setWireMark(false, "PARTIAL WIRE · CHECK IMPORT-READINESS");
      return;
    }
    if (lasersRed(ready)) {
      const keys = laserKeys(ready).slice(0, 3).join(",") || "blocking";
      setWireMark(false, "STALE · lasers red · " + keys + " · empty ≠ $0");
      return;
    }
    if (periodCloseTrouble(ready)) {
      setWireMark(false, periodCloseBit(ready) + " · empty ≠ $0 · no SoftDent write-back");
      return;
    }
    if (!lastSessionOk) {
      setWireMark(false, "READINESS OK · SESSION WEAK — mutations may 403");
      return;
    }
    setWireMark(true, "LIVE SIGNAL · empty ≠ $0 · no SoftDent write-back");
  }

  function morningBundleBit(ready) {
    const close = ready && ready.periodClose;
    const bundle = close && close.morningBundle;
    if (!bundle || typeof bundle !== "object") return "";
    if (bundle.ok) {
      return (
        " · morning OK" + (bundle.okCount != null ? " " + bundle.okCount : "")
      );
    }
    if (bundle.fallback) return " · morning FALLBACK";
    const err = bundle.error || bundle.detail || "";
    return " · morning FAIL" + (err ? " · " + String(err).slice(0, 28) : "");
  }

  function halMorningBrief(ready, sdText, qbText) {
    const sd = String(sdText || "—");
    const qb = String(qbText || "—");
    const mb = morningBundleBit(ready);
    if (!ready) {
      return "No import-readiness signal yet — SoftDent and QuickBooks faces stay empty ≠ $0.";
    }
    if (lasersRed(ready)) {
      const keys = laserKeys(ready).slice(0, 2).join(", ") || "critical imports";
      return (
        "Lasers red on " +
        keys +
        " — money faces gated until imports refresh. empty ≠ $0."
      );
    }
    if (periodCloseTrouble(ready)) {
      return (
        periodCloseBit(ready) +
        mb +
        " — close path blocked; click Ask HAL for next move. empty ≠ $0."
      );
    }
    if (/STALE|∅|NO SIGNAL|—/.test(sd) || /STALE|∅|NO SIGNAL|—/.test(qb)) {
      return (
        "Green-path lasers, but money fusion still incomplete (SD " +
        sd +
        " · QB " +
        qb +
        "). empty ≠ $0."
      );
    }
    return (
      "Live fusion: SoftDent claims " +
      sd +
      ", QuickBooks " +
      qb +
      "." +
      (mb ? mb.replace(/^ · /, " ") + "." : "") +
      " Click Ask HAL for today's brief."
    );
  }

  function setRayHealth(id, tone) {
    const el = document.getElementById(id);
    if (!el) return;
    el.classList.toggle("is-dim", tone === "dim");
    el.classList.toggle("is-cut", tone === "cut");
  }

  function laneBeamTone(statusText, metricText) {
    const s = String(statusText || "");
    const m = String(metricText || "").trim();
    if (/NO SIGNAL|UNAVAILABLE/i.test(s) || m === "—" || m === "∅" || m === "") return "cut";
    if (/STALE|CLOSE STALL|STALE \/ ∅|NO SIGNAL/i.test(s) || /STALE|∅|STALE \/ ∅/.test(m)) {
      return "dim";
    }
    if (/LIVE|CLAIMS · LIVE|COHERENT|GREEN/i.test(s)) return "live";
    if (/\$/.test(m) || /\d/.test(m)) return "live";
    return "dim";
  }

  function updateBeamHealth() {
    const sdStatus = (document.getElementById("sd-status") || {}).textContent || "";
    const qbStatus = (document.getElementById("qb-status") || {}).textContent || "";
    const sdMetric = (document.getElementById("metric-sd") || {}).textContent || "";
    const qbMetric = (document.getElementById("metric-qb") || {}).textContent || "";
    const taxMetric = (document.getElementById("metric-tax") || {}).textContent || "";
    const globalFault = !!(lasersRed(lastReady) || periodCloseTrouble(lastReady));
    setRayHealth("ray-sd", laneBeamTone(sdStatus, sdMetric));
    setRayHealth("ray-qb", laneBeamTone(qbStatus, qbMetric));
    setRayHealth(
      "ray-tax",
      /ERR|FAIL/i.test(taxMetric) ? "cut" : /PLANS|PLAN|%|\$/.test(taxMetric) ? "live" : "dim"
    );
    setRayHealth(
      "ray-ctrl",
      !lastSessionOk ? "dim" : globalFault ? "dim" : "live"
    );

    const rays = ["ray-sd", "ray-qb", "ray-tax", "ray-ctrl"].map(function (id) {
      return document.getElementById(id);
    });
    const allClear =
      !globalFault &&
      rays.every(function (el) {
        return el && !el.classList.contains("is-dim") && !el.classList.contains("is-cut");
      });

    rays.forEach(function (el) {
      if (!el) return;
      const bad = el.classList.contains("is-dim") || el.classList.contains("is-cut");
      el.classList.toggle("is-quiet", allClear || (!bad && !globalFault));
      el.classList.toggle("is-loud", bad || (globalFault && el.id === "ray-ctrl"));
    });

    const hits = document.querySelectorAll(".core-hit");
    hits.forEach(function (hit) {
      const beam = hit.getAttribute("data-beam");
      const ray = document.getElementById(beam === "ctrl" ? "ray-ctrl" : "ray-" + beam);
      const cut = ray && ray.classList.contains("is-cut");
      const dim = ray && ray.classList.contains("is-dim");
      hit.style.opacity = cut ? "0.05" : dim ? "0.4" : allClear ? "0.22" : "";
    });
  }

  function setCoreSyncPulse(mode) {
    coreSyncMode = mode || null;
    const core = document.getElementById("core");
    const state = document.getElementById("hal-state");
    if (!core) return;
    core.classList.toggle("core--syncing", mode === "running");
    if (mode === "running") {
      if (state) {
        state.textContent = "SYNC · RUNNING";
        state.style.color = "#ffaa00";
      }
      return;
    }
    if (mode === "ok") {
      fireCoreBurst("ok");
      if (state) {
        state.textContent = "SYNC · OK";
        state.style.color = "";
      }
      setTimeout(function () {
        coreSyncMode = null;
        core.classList.remove("core--syncing");
        updateHalCore(lastReady);
      }, 1100);
      return;
    }
    if (mode === "fail") {
      fireCoreBurst("fail");
      if (state) {
        state.textContent = "SYNC · FAIL";
        state.style.color = "var(--fringe)";
      }
      setTimeout(function () {
        coreSyncMode = null;
        core.classList.remove("core--syncing");
        updateHalCore(lastReady);
      }, 1300);
      return;
    }
    core.classList.remove("core--syncing");
    updateHalCore(lastReady);
  }

  function updateHalCore(ready, moneyBits) {
    const core = document.getElementById("core");
    const state = document.getElementById("hal-state");
    const fusion = document.getElementById("hal-fusion");
    const hint = document.getElementById("hal-hint");
    const brief = document.getElementById("hal-brief");
    if (!core || !state) return;

    const sdText =
      moneyBits && moneyBits.sd
        ? String(moneyBits.sd)
        : (document.getElementById("metric-sd") || {}).textContent || "—";
    const qbText =
      moneyBits && moneyBits.qb
        ? String(moneyBits.qb)
        : (document.getElementById("metric-qb") || {}).textContent || "—";
    if (fusion) fusion.textContent = "SD " + sdText + " · QB " + qbText;
    if (brief) brief.textContent = halMorningBrief(ready, sdText, qbText);
    updateBeamHealth();

    if (coreSyncMode === "running" || coreSyncMode === "ok" || coreSyncMode === "fail") {
      return;
    }

    let mode = "fault";
    let label = "NO SIGNAL";
    let hintText = "empty ≠ $0 · no SoftDent write-back";
    const mb = morningBundleBit(ready);

    if (!ready) {
      label = "READINESS · NO SIGNAL";
      mode = "fault";
    } else if (lasersRed(ready)) {
      const keys = laserKeys(ready).slice(0, 2).join(",") || "blocking";
      label = "LASERS · RED";
      hintText = "Blocking · " + keys + mb + " · empty ≠ $0";
      mode = "fault";
    } else if (periodCloseTrouble(ready)) {
      label = periodCloseBit(ready);
      hintText = label + mb + " · money gated · empty ≠ $0";
      mode = "warn";
    } else if (!lastSessionOk) {
      label = "READY · SESSION WEAK";
      hintText = "Session may 403 mutations" + mb + " · empty ≠ $0";
      mode = "warn";
    } else {
      label = "LIVE · GREEN-PATH";
      hintText = periodCloseBit(ready) + mb + " · empty ≠ $0";
      mode = "live";
    }

    state.textContent = label;
    state.style.color = "";
    if (hint) hint.textContent = hintText;
    core.classList.toggle("core--live", mode === "live");
    core.classList.toggle("core--warn", mode === "warn");
    core.classList.toggle("core--fault", mode === "fault");
    core.title = "HAL core · " + label;
  }

  function halCoreAskPrompt(ready) {
    if (!ready) {
      return "What's the import readiness status on the optical bench? empty ≠ $0.";
    }
    if (lasersRed(ready)) {
      const keys = laserKeys(ready).slice(0, 3).join(", ") || "blocking imports";
      return (
        "Lasers are red (" +
        keys +
        "). What is blocking money-beams and what should I do next? empty ≠ $0."
      );
    }
    if (periodCloseTrouble(ready)) {
      return (
        periodCloseBit(ready) +
        morningBundleBit(ready) +
        " — what is blocking period close / morning bundle, and what should I do next? empty ≠ $0."
      );
    }
    const sd = (document.getElementById("metric-sd") || {}).textContent || "—";
    const qb = (document.getElementById("metric-qb") || {}).textContent || "—";
    return (
      "Give me today's money fusion brief: SoftDent claims " +
      sd +
      ", QuickBooks " +
      qb +
      ". empty ≠ $0."
    );
  }

  function openAlignmentBench() {
    fireCoreBurst(lasersRed(lastReady) || periodCloseTrouble(lastReady) ? "fail" : "ok");
    toast("HAL → Alignment Bench · honesty lasers + period-close");
    window.location.href = "/nr2-optical-pages-hub.html";
  }

  function openAskHal() {
    fireCoreBurst(lasersRed(lastReady) || periodCloseTrouble(lastReady) ? "fail" : "ok");
    const q = encodeURIComponent(halCoreAskPrompt(lastReady));
    toast("HAL → Ask HAL · contextual bench prompt");
    window.location.href = "/nr2-optical-page-hal.html?q=" + q + "&autoAsk=1";
  }

  function money(n) {
    if (n == null || !Number.isFinite(Number(n))) return null;
    return Number(n);
  }
  function fmtMoney(n) {
    const v = money(n);
    if (v == null) return null;
    return "$" + v.toLocaleString("en-US", { maximumFractionDigits: 0 });
  }
  function setMetric(id, value, opts) {
    const el = document.getElementById(id);
    if (!el) return;
    if (value == null || value === "") {
      el.textContent = opts && opts.emptyLabel ? opts.emptyLabel : "—";
      el.classList.add("empty");
      return;
    }
    el.textContent = value;
    el.classList.remove("empty");
  }
  function setWireMark(live, text) {
    const el = document.getElementById("wire-mark");
    if (!el) return;
    el.textContent = text;
    el.classList.toggle("live", !!live);
  }

  async function api(path, init) {
    const headers = Object.assign({ Accept: "application/json" }, (init && init.headers) || {});
    if (init && init.method && init.method.toUpperCase() !== "GET" && sessionToken) {
      headers["X-NR2-Session-Token"] = sessionToken;
      headers["Content-Type"] = headers["Content-Type"] || "application/json";
    }
    let res;
    try {
      res = await fetch(path, Object.assign({ cache: "no-store" }, init || {}, { headers }));
    } catch (err) {
      const aborted = err && (err.name === "AbortError" || err.code === 20);
      return {
        ok: false,
        status: aborted ? 408 : 0,
        data: { error: aborted ? "request_aborted" : String(err && err.message ? err.message : err) },
        aborted: !!aborted,
      };
    }
    let data = null;
    try {
      data = await res.json();
    } catch (_) {
      data = null;
    }
    return { ok: res.ok, status: res.status, data: data };
  }

  function tick() {
    const clock = document.getElementById("clock");
    if (clock) clock.textContent = new Date().toISOString().slice(11, 19) + " UTC";
  }
  tick();
  setInterval(tick, 1000);

  function applyRole() {
    const locked = role === "fd";
    document.querySelectorAll(".inst, .ctrl").forEach((n) => n.classList.toggle("locked", locked));
    document.querySelectorAll("[data-act], #wheel button").forEach((n) => {
      if (n.getAttribute("data-act") === "ask-hal" || n.getAttribute("data-act") === "align") {
        n.disabled = false;
        return;
      }
      n.disabled = locked;
    });
    const om = document.getElementById("role-om");
    const fd = document.getElementById("role-fd");
    if (om) om.classList.toggle("on", role === "om");
    if (fd) fd.classList.toggle("on", role === "fd");
  }
  const roleOm = document.getElementById("role-om");
  const roleFd = document.getElementById("role-fd");
  if (roleOm) roleOm.onclick = () => {
    role = "om";
    applyRole();
    toast("RBAC: office_manager keys inserted");
  };
  if (roleFd) roleFd.onclick = () => {
    role = "fd";
    applyRole();
    toast("RBAC shutters closed — Front Desk view-only");
  };
  applyRole();

  /* —— beams —— */
  function localPoint(bench, clientX, clientY) {
    const br = bench.getBoundingClientRect();
    return { x: clientX - br.left, y: clientY - br.top };
  }
  function rimPoint(center, from, r) {
    const dx = from.x - center.x;
    const dy = from.y - center.y;
    const len = Math.hypot(dx, dy) || 1;
    return { x: center.x + (dx / len) * r, y: center.y + (dy / len) * r };
  }
  function placeRay(id, a, b) {
    const el = document.getElementById(id);
    if (!el) return;
    const dx = b.x - a.x;
    const dy = b.y - a.y;
    const len = Math.hypot(dx, dy);
    const deg = (Math.atan2(dy, dx) * 180) / Math.PI;
    const height = parseFloat(getComputedStyle(el).height) || 5;
    el.style.transformOrigin = "0 50%";
    el.style.width = Math.max(len, 0) + "px";
    el.style.left = a.x + "px";
    el.style.top = a.y - height / 2 + "px";
    el.style.transform = "rotate(" + deg + "deg)";
  }
  function placeCoreHit(beam, rim, center, radius) {
    const el = document.querySelector('.core-hit[data-beam="' + beam + '"]');
    if (!el || !radius) return;
    const pctX = 50 + ((rim.x - center.x) / radius) * 50;
    const pctY = 50 + ((rim.y - center.y) / radius) * 50;
    el.style.left = pctX + "%";
    el.style.top = pctY + "%";
  }
  function fireCoreBurst(kind) {
    const core = document.getElementById("core");
    if (!core) return;
    const cls = kind === "fail" ? "core--fire-fail" : "core--fire";
    core.classList.remove("core--fire", "core--fire-fail");
    void core.offsetWidth;
    core.classList.add(cls);
    const burst = core.querySelector(".core-burst");
    const clear = () => {
      core.classList.remove("core--fire", "core--fire-fail");
      if (burst) burst.removeEventListener("animationend", clear);
    };
    if (burst) {
      burst.addEventListener("animationend", clear);
    } else {
      setTimeout(clear, 800);
    }
  }
  function aperturePoint(bench, rect, side) {
    /* Match CSS ::after LEDs: 14px at right/left -7px → center sits on the widget edge */
    const y = rect.top + rect.height * 0.48;
    const x = side === "right" ? rect.right : rect.left;
    return localPoint(bench, x, y);
  }
  function snapBeams() {
    const bench = document.getElementById("bench");
    const core = document.getElementById("core");
    const sd = document.getElementById("emitter-sd");
    const qb = document.getElementById("emitter-qb");
    const tax = document.getElementById("tax");
    const ctrl = document.getElementById("ctrl");
    if (!bench || !core || !sd || !qb || !tax || !ctrl) return;
    const cr = core.getBoundingClientRect();
    if (cr.width < 4) return;
    const center = localPoint(bench, cr.left + cr.width / 2, cr.top + cr.height / 2);
    /* Touch the visible core border (not outer halo) */
    const radius = cr.width / 2;
    const sdStart = aperturePoint(bench, sd.getBoundingClientRect(), "right");
    const qbStart = aperturePoint(bench, qb.getBoundingClientRect(), "left");
    const taxStart = aperturePoint(bench, tax.getBoundingClientRect(), "left");
    const ctrlStart = aperturePoint(bench, ctrl.getBoundingClientRect(), "right");
    const sdRim = rimPoint(center, sdStart, radius);
    const qbRim = rimPoint(center, qbStart, radius);
    const taxRim = rimPoint(center, taxStart, radius);
    const ctrlRim = rimPoint(center, ctrlStart, radius);
    placeRay("ray-sd", sdStart, sdRim);
    placeRay("ray-qb", qbStart, qbRim);
    placeRay("ray-tax", taxStart, taxRim);
    placeRay("ray-ctrl", ctrlStart, ctrlRim);
    placeCoreHit("sd", sdRim, center, radius);
    placeCoreHit("qb", qbRim, center, radius);
    placeCoreHit("tax", taxRim, center, radius);
    placeCoreHit("ctrl", ctrlRim, center, radius);
  }
  window.snapBeams = snapBeams;
  snapBeams();
  requestAnimationFrame(function () {
    requestAnimationFrame(snapBeams);
  });
  setTimeout(snapBeams, 50);
  setTimeout(snapBeams, 250);
  window.addEventListener("resize", snapBeams);
  if (typeof ResizeObserver !== "undefined") {
    const bench = document.getElementById("bench");
    if (bench) new ResizeObserver(snapBeams).observe(bench);
  }

  /* —— live wires —— */
  async function ensureSession() {
    const r = await api("/api/browser-session");
    if (r.data && r.data.sessionToken) {
      sessionToken = String(r.data.sessionToken);
      return true;
    }
    return false;
  }

  async function refreshLasers() {
    const align = document.getElementById("align");
    const r = await api("/api/import-readiness");
    if (!r.ok || !r.data) {
      if (align) {
        align.classList.add("bad");
        align.title = "Import readiness unavailable";
      }
      applyWireHonesty(null);
      updateHalCore(null);
      updateClosePath(null);
      return null;
    }
    const ready = r.data;
    const blocking = Array.isArray(ready.blocking) ? ready.blocking : [];
    const lasers = ready.alignmentLasers || {};
    const red = lasersRed(ready);
    // Canonical server lasers — do not re-compute softGaps client-side (brief soft stale must stay soft).
    if (align) {
      align.classList.toggle("bad", !!red);
      align.title = red
        ? "Import gaps / stale · lasers red (blocking=" +
          blocking.length +
          (lasers.datasetKeys && lasers.datasetKeys.length
            ? " · " + lasers.datasetKeys.slice(0, 4).join(",")
            : "") +
          ")"
        : "Import readiness coherent · lasers green-path";
    }
    applyWireHonesty(ready);
    applyMetricLaserHonesty(ready);
    updateHalCore(ready);
    updateClosePath(ready);
    return ready;
  }

  function applyMetricLaserHonesty(ready) {
    const keys = laserKeys(ready);
    const closeTrouble = periodCloseTrouble(ready);
    const sdStatus = document.getElementById("sd-status");
    const qbStatus = document.getElementById("qb-status");
    if (sdStatus && /LIVE/.test(sdStatus.textContent || "")) {
      if (keysHit(keys, ["softdent."]) || closeTrouble) {
        sdStatus.textContent = closeTrouble ? "CLAIMS · CLOSE STALL" : "CLAIMS · STALE";
      }
    }
    if (qbStatus && (qbStatus.textContent || "") === "LIVE") {
      if (keysHit(keys, ["quickbooks."]) || closeTrouble) {
        qbStatus.textContent = closeTrouble ? "CLOSE STALL" : "STALE";
      }
    }
    const bind = document.getElementById("banner-bind");
    if (bind && ready) {
      bind.textContent =
        periodCloseBit(ready) +
        " · lasers " +
        (lasersRed(ready) ? "RED" : "green-path") +
        " · money-beams · empty ≠ $0";
    }
  }

  async function refreshMetrics(readyHint) {
    const ready = readyHint || lastReady;
    const keys = laserKeys(ready);
    const closeTrouble = periodCloseTrouble(ready);
    const lasersBlock = lasersRed(ready);
    const sdStale = keysHit(keys, ["softdent."]) || closeTrouble || lasersBlock;
    const qbStale = keysHit(keys, ["quickbooks."]) || closeTrouble || lasersBlock;
    const sdStatus = document.getElementById("sd-status");
    const qbStatus = document.getElementById("qb-status");
    const sdSub = document.getElementById("sd-sub");
    const qbSub = document.getElementById("qb-sub");

    const beamsRes = await api("/api/hal/tools/money-beams");
    const beams = beamsRes.ok ? beamsRes.data : null;
    const beamHash = beams && beams.beamHash ? String(beams.beamHash).slice(0, 8) : "";
    const importStale = !!(beams && beams.importStale);
    const gateMoney = lasersBlock || importStale || closeTrouble;

    let sdFilled = false;
    const sdBeam = beams && beams.softdent;
    if (gateMoney) {
      setMetric("metric-sd", null, { emptyLabel: "STALE / ∅" });
      if (sdStatus) {
        sdStatus.textContent = closeTrouble
          ? "CLAIMS · CLOSE STALL"
          : lasersBlock
            ? "CLAIMS · STALE"
            : "CLAIMS · NO SIGNAL";
      }
      if (sdSub) {
        sdSub.textContent =
          "money-beams gated · " +
          periodCloseBit(ready) +
          (beamHash ? " · hash " + beamHash : "") +
          " · empty ≠ $0 · no write-back";
      }
      sdFilled = true;
    } else if (sdBeam && sdBeam.hasData && (sdBeam.display || sdBeam.totalOutstanding != null)) {
      const shown =
        sdBeam.display ||
        (sdBeam.totalOutstanding != null ? fmtMoney(sdBeam.totalOutstanding) : null);
      if (shown) {
        setMetric("metric-sd", shown);
        if (sdStatus) sdStatus.textContent = sdStale ? "CLAIMS · STALE" : "CLAIMS · LIVE";
        if (sdSub) {
          sdSub.textContent =
            "money-beams SoftDent" +
            (beamHash ? " · hash " + beamHash : "") +
            (sdStale ? " · lasers red" : "") +
            " · empty ≠ $0 · no write-back";
        }
        sdFilled = true;
      }
    }

    if (!sdFilled) {
      const claims = await api("/api/softdent/claims-outstanding?limit=25");
      if (claims.ok && claims.data && claims.data.hasData) {
        const list = Array.isArray(claims.data.claims) ? claims.data.claims : [];
        const count = claims.data.count != null ? Number(claims.data.count) : list.length;
        const total = money(claims.data.totalOutstanding);
        const shown = total != null ? fmtMoney(total) : null;
        if (shown) {
          setMetric("metric-sd", shown);
          if (sdStatus) sdStatus.textContent = sdStale ? "CLAIMS · STALE" : "CLAIMS · LIVE";
          if (sdSub) {
            sdSub.textContent =
              "claims outstanding" +
              (count ? " · " + count + " open" : "") +
              (sdStale ? " · lasers red" : "") +
              " · empty ≠ $0 · no write-back";
          }
        } else {
          setMetric("metric-sd", null);
          if (sdStatus) sdStatus.textContent = "∅ EMPTY";
        }
        await refreshFilm(claims.data);
      } else {
        setMetric("metric-sd", null, { emptyLabel: "∅" });
        if (sdStatus) sdStatus.textContent = "NO SIGNAL";
        if (sdSub) sdSub.textContent = "no claims signal · empty ≠ $0 · no SoftDent write-back";
        await refreshFilm(null);
      }
    } else {
      const claims = await api("/api/softdent/claims-outstanding?limit=25");
      await refreshFilm(claims.ok && claims.data ? claims.data : null);
    }

    let qbFilled = false;
    const qbBeam = beams && beams.quickbooks;
    if (gateMoney) {
      setMetric("metric-qb", null, { emptyLabel: "STALE / ∅" });
      if (qbStatus) {
        qbStatus.textContent = closeTrouble
          ? "CLOSE STALL"
          : lasersBlock
            ? "STALE"
            : "NO SIGNAL";
      }
      if (qbSub) {
        qbSub.textContent =
          "money-beams gated · " +
          periodCloseBit(ready) +
          (beamHash ? " · hash " + beamHash : "") +
          " · empty ≠ $0";
      }
      qbFilled = true;
    } else if (qbBeam && qbBeam.hasData && (qbBeam.display || qbBeam.monthlyRevenue != null)) {
      const shown =
        qbBeam.display ||
        (qbBeam.monthlyRevenue != null ? fmtMoney(qbBeam.monthlyRevenue) : null);
      if (shown) {
        setMetric("metric-qb", shown);
        if (qbStatus) qbStatus.textContent = qbStale ? "STALE" : "LIVE";
        if (qbSub) {
          qbSub.textContent =
            "money-beams QuickBooks" +
            (beamHash ? " · hash " + beamHash : "") +
            (qbStale ? " · lasers red" : "") +
            " · empty ≠ $0";
        }
        qbFilled = true;
      }
    }

    if (!qbFilled) {
      const qb = await api("/api/qb/monthly-revenue");
      if (qb.ok && qb.data && qb.data.hasData && Array.isArray(qb.data.values) && qb.data.values.length) {
        const last = qb.data.values[qb.data.values.length - 1];
        const shown = fmtMoney(last);
        if (shown) {
          setMetric("metric-qb", shown);
          if (qbStatus) qbStatus.textContent = qbStale ? "STALE" : "LIVE";
          const lbl = Array.isArray(qb.data.labels) ? qb.data.labels[qb.data.labels.length - 1] : "";
          if (qbSub) {
            qbSub.textContent =
              "monthly revenue" +
              (lbl ? " · " + lbl : "") +
              (qbStale ? " · lasers red" : "") +
              " · empty ≠ $0";
          }
        } else {
          setMetric("metric-qb", null, { emptyLabel: "∅ EMPTY" });
          if (qbStatus) qbStatus.textContent = "∅ EMPTY";
        }
      } else {
        setMetric("metric-qb", null, { emptyLabel: "∅" });
        if (qbStatus) qbStatus.textContent = "NO SIGNAL";
      }
    }

    applyMetricLaserHonesty(ready);
    const sdEl = document.getElementById("metric-sd");
    const qbEl = document.getElementById("metric-qb");
    updateHalCore(ready, {
      sd: sdEl ? sdEl.textContent : "—",
      qb: qbEl ? qbEl.textContent : "—",
    });
    updateBeamHealth();
    updateClosePath(ready);
  }

  async function refreshFilm(claimsData) {
    const slots = document.querySelectorAll("#film .slot");
    if (!slots.length) return;
    const list =
      claimsData && claimsData.hasData && Array.isArray(claimsData.claims)
        ? claimsData.claims.slice(0, slots.length)
        : [];
    slots.forEach((slot, i) => {
      const c = list[i];
      slot.classList.remove("age-ok", "age-warn", "age-late", "age-critical", "age-unknown");
      if (!c) {
        slot.classList.add("empty");
        slot.innerHTML = "∅";
        slot.title = "No claim stub · empty ≠ $0";
        slot.removeAttribute("data-claim-id");
        slot.removeAttribute("data-patient-id");
        slot.tabIndex = -1;
        return;
      }
      slot.classList.remove("empty");
      const amt = money(c.amount);
      const claimId = String(c.claimId || "").trim();
      const patientId = String(c.patientId || "").trim();
      const age = claimAgeDays(c.serviceDate);
      const ageCls = claimAgeClass(age);
      slot.classList.add(ageCls);
      const label =
        String(c.claimId || c.patientName || "claim").slice(0, 14) +
        (amt != null ? " · $" + Math.round(amt) : "");
      slot.innerHTML = '<div class="mini"></div>' + label.replace(/</g, "");
      slot.title =
        String(c.payer || "") +
        " · " +
        String(c.serviceDate || "") +
        " · age " +
        (age == null ? "unknown" : String(age) + "d") +
        " · " +
        String(c.status || "") +
        " · open Claims · read-only";
      if (claimId) slot.setAttribute("data-claim-id", claimId);
      else slot.removeAttribute("data-claim-id");
      if (patientId) slot.setAttribute("data-patient-id", patientId);
      else slot.removeAttribute("data-patient-id");
      slot.tabIndex = 0;
    });
  }

  function claimAgeDays(serviceDate) {
    const sd = String(serviceDate || "").slice(0, 10);
    if (!/^\d{4}-\d{2}-\d{2}$/.test(sd)) return null;
    const d = new Date(sd + "T12:00:00");
    if (Number.isNaN(d.getTime())) return null;
    const today = new Date();
    today.setHours(12, 0, 0, 0);
    return Math.max(0, Math.floor((today.getTime() - d.getTime()) / 86400000));
  }

  /** ≤30 green · ≤60 yellow · ≤90 amber · >90 red · unknown muted */
  function claimAgeClass(ageDays) {
    if (ageDays == null || !Number.isFinite(ageDays)) return "age-unknown";
    if (ageDays <= 30) return "age-ok";
    if (ageDays <= 60) return "age-warn";
    if (ageDays <= 90) return "age-late";
    return "age-critical";
  }

  function openEmitter(go) {
    if (go === "claims") {
      toast("SoftDent → Claims");
      window.location.href = "/nr2-optical-page-claims.html";
      return;
    }
    if (go === "hub") {
      toast("QuickBooks → Alignment Bench");
      window.location.href = "/nr2-optical-pages-hub.html";
      return;
    }
    if (go === "tax") {
      toast("Tax Prism → Tax page");
      window.location.href = "/nr2-optical-page-taxes.html";
    }
  }

  function openClaimsFromFilm(slot) {
    if (!slot || slot.classList.contains("empty")) {
      window.location.href = "/nr2-optical-page-claims.html";
      return;
    }
    const claimId = slot.getAttribute("data-claim-id") || "";
    const patientId = slot.getAttribute("data-patient-id") || "";
    try {
      sessionStorage.setItem(
        "nr2.claims.focus",
        JSON.stringify({
          claimId: claimId,
          patientId: patientId,
          at: Date.now(),
          source: "landing-film",
        })
      );
    } catch (_) {}
    toast("FILM → Claims" + (claimId ? " · " + claimId.slice(0, 18) : ""));
    window.location.href = "/nr2-optical-page-claims.html";
  }

  function updateClosePath(ready) {
    const root = document.getElementById("close-steps");
    const hint = document.getElementById("close-hint");
    if (!root) return;
    const bundle = ready && ready.periodClose && ready.periodClose.morningBundle;
    const steps = {
      bundle: root.querySelector('[data-step="bundle"]'),
      lasers: root.querySelector('[data-step="lasers"]'),
      close: root.querySelector('[data-step="close"]'),
    };
    Object.keys(steps).forEach(function (k) {
      if (steps[k]) steps[k].classList.remove("on", "warn", "bad");
    });

    let bundleTone = "bad";
    let bundleLabel = "Bundle";
    if (bundle && typeof bundle === "object") {
      if (bundle.ok) {
        bundleTone = "on";
        bundleLabel = "Bundle OK";
      } else if (bundle.fallback) {
        bundleTone = "warn";
        bundleLabel = "Fallback";
      } else {
        bundleTone = "bad";
        bundleLabel = "Bundle";
      }
    } else if (ready && ready.periodClose) {
      bundleTone = "warn";
      bundleLabel = "Bundle ?";
    }
    if (steps.bundle) {
      steps.bundle.classList.add(bundleTone);
      steps.bundle.textContent = bundleLabel;
      steps.bundle.title =
        bundleTone === "on"
          ? "Morning bundle ok"
          : "Click → SoftDent REFRESH-PERIOD (morning bundle gate)";
    }

    const red = !ready || lasersRed(ready);
    if (steps.lasers) {
      steps.lasers.classList.add(red ? "bad" : "on");
      steps.lasers.textContent = red ? "Lasers" : "Green";
      steps.lasers.title = red ? "Click → Alignment Bench" : "Lasers green-path";
    }

    const closeTrouble = periodCloseTrouble(ready);
    const closeBit = periodCloseBit(ready);
    const W = window.NR2OpticalWire;
    const canForce = !!(W && typeof W.forceCloseAvailable === "function" && W.forceCloseAvailable(ready));
    if (steps.close) {
      if (!ready || !ready.periodClose) {
        steps.close.classList.add("bad");
        steps.close.textContent = "Close";
      } else if (closeTrouble) {
        steps.close.classList.add("warn");
        steps.close.textContent = String((ready.periodClose && ready.periodClose.status) || "stall")
          .slice(0, 8)
          .toUpperCase();
      } else {
        steps.close.classList.add("on");
        steps.close.textContent = "Close";
      }
      steps.close.title = canForce
        ? "Click → FORCE CLOSE (lasers red / stall)"
        : closeTrouble
          ? "Period-close trouble · force unavailable"
          : "Period-close idle";
      steps.close.setAttribute("data-can-force", canForce ? "1" : "0");
    }

    if (hint) {
      hint.textContent =
        closeBit +
        morningBundleBit(ready) +
        (red ? " · lasers red" : " · lasers green-path") +
        (canForce ? " · force ready" : "") +
        " · empty ≠ $0";
    }
  }

  async function runCloseStep(stepEl) {
    if (!stepEl || role === "fd") {
      if (role === "fd") toast("Shutter locked — Front Desk cannot mutate");
      return;
    }
    const step = stepEl.getAttribute("data-step");
    if (step === "bundle") {
      if (stepEl.classList.contains("on")) {
        toast("Morning bundle already OK · empty ≠ $0");
        return;
      }
      toast("Close Path · Bundle → SoftDent REFRESH-PERIOD");
      await doRefreshPeriod();
      return;
    }
    if (step === "lasers") {
      if (stepEl.classList.contains("on")) {
        toast("Lasers already green-path");
        return;
      }
      openAlignmentBench();
      return;
    }
    if (step === "close") {
      const W = window.NR2OpticalWire;
      if (!W || typeof W.forcePeriodClose !== "function") {
        toast("Force close wire unavailable");
        return;
      }
      if (stepEl.getAttribute("data-can-force") !== "1") {
        toast("FORCE CLOSE gated · needs lasers red or close stall/blocked");
        return;
      }
      toast("Close Path · FORCE CLOSE …");
      fireCoreBurst("ok");
      const r = await W.forcePeriodClose({ actor: "landing-close-path" });
      if (!r || !r.ok) {
        fireCoreBurst("fail");
        toast(
          "Force close failed · " +
            ((r && r.data && (r.data.error || r.data.detail || r.data.reason)) ||
              (r && r.status) ||
              "unknown")
        );
        return;
      }
      fireCoreBurst("ok");
      toast("Force close posted · refreshing lasers + metrics");
      await refreshLasers();
      await refreshMetrics();
    }
  }

  async function bootWire() {
    setWireMark(false, "CONNECTING · SESSION + READINESS");
    try {
      const okSession = await ensureSession();
      lastSessionOk = !!okSession;
      const ready = await refreshLasers();
      await refreshMetrics(ready);
      applyWireHonesty(ready, okSession);
      if (okSession && ready && !lasersRed(ready) && !periodCloseTrouble(ready)) {
        toast("Optical wires live · money-beams · lasers green-path · SoftDent + QB");
      } else if (ready && periodCloseTrouble(ready)) {
        toast(periodCloseBit(ready) + " · money faces gated · empty ≠ $0");
      } else if (ready && lasersRed(ready)) {
        toast("Lasers red · money reads STALE until critical imports refresh");
      }
    } catch (err) {
      setWireMark(false, "WIRE FAILED · " + String(err && err.message ? err.message : err));
    }
  }

  const wheel = document.getElementById("wheel");
  if (wheel) {
    wheel.onclick = async (e) => {
      const b = e.target.closest("button[data-period]");
      if (!b || role === "fd") return;
      document.querySelectorAll("#wheel button").forEach((x) => x.classList.remove("on"));
      b.classList.add("on");
      selectedPeriod = b.dataset.period || selectedPeriod;
      toast("Period " + selectedPeriod + "d selected · pressing REFRESH-PERIOD posts SoftDent refresh");
    };
  }

  async function doSync(btn) {
    if (syncBusy) return;
    syncBusy = true;
    if (btn) btn.classList.add("busy");
    const led = document.getElementById("pulse-led");
    if (led) {
      led.classList.remove("idle");
      led.classList.add("on");
    }
    setCoreSyncPulse("running");
    toast("SYNC → POST /api/apex/sync/trigger …");
    const r = await api("/api/apex/sync/trigger", {
      method: "POST",
      body: JSON.stringify({ page: "financial", fullSync: true, actor: "optical-bench" }),
    });
    syncBusy = false;
    if (btn) btn.classList.remove("busy");
    if (led) {
      led.classList.remove("on");
      led.classList.add("idle");
    }
    if (r.status === 423) {
      setCoreSyncPulse("fail");
      toast("Sync locked — already in progress (423)");
      return;
    }
    if (!r.ok) {
      setCoreSyncPulse("fail");
      toast("Sync failed · " + (r.data && (r.data.error || r.data.status) || r.status));
      return;
    }
    setCoreSyncPulse("ok");
    toast("Sync ok · refreshing lasers + metrics");
    await refreshLasers();
    await refreshMetrics();
  }

  async function doRefreshPeriod() {
    const btn = document.querySelector('[data-act="refresh"]');
    if (btn) {
      btn.disabled = true;
      btn.classList.add("busy");
    }
    toast("Period Wheel → POST /api/apex/softdent/refresh-period · " + selectedPeriod + "d …");
    const ctrl = typeof AbortController !== "undefined" ? new AbortController() : null;
    // Client aborts before server 22s hard cap so UI never waits forever.
    const timer = ctrl ? setTimeout(() => ctrl.abort(), 18000) : null;
    const r = await api("/api/apex/softdent/refresh-period", {
      method: "POST",
      body: JSON.stringify({ periodDays: Number(selectedPeriod) || 60 }),
      signal: ctrl ? ctrl.signal : undefined,
    });
    if (timer) clearTimeout(timer);
    if (btn) {
      btn.disabled = role === "fd";
      btn.classList.remove("busy");
    }
    if (r.aborted || r.status === 408 || r.status === 504) {
      toast(
        "Refresh stalled — check SoftDent Sign On (COMPUTE) / Excel path · " +
          ((r.data && (r.data.detail || r.data.error || r.data.reason)) || "timeout") +
          " · empty ≠ $0"
      );
      return;
    }
    if (!r.ok) {
      toast("Refresh-period failed · " + (r.data && r.data.error || r.status));
      return;
    }
    toast(r.data && r.data.ok ? "SoftDent period refresh ok" : "Refresh returned · check SoftDent sign-on");
    await refreshLasers();
    await refreshMetrics();
  }

  async function doTax() {
    toast("Tax Prism → POST /api/apex/tax/calculate-planning …");
    const r = await api("/api/apex/tax/calculate-planning", {
      method: "POST",
      body: JSON.stringify({}),
    });
    const metric = document.getElementById("metric-tax");
    if (!r.ok) {
      toast("Tax planning failed · " + (r.data && r.data.error || r.status));
      if (metric) metric.textContent = "ERR";
      return;
    }
    const plan = r.data || {};
    const label =
      plan.effective_rate != null
        ? (Number(plan.effective_rate) * 100).toFixed(1) + "% EFF"
        : plan.taxable_income != null
          ? fmtMoney(plan.taxable_income) || "PLAN"
          : "PLAN OK";
    if (metric) {
      metric.textContent = label;
      metric.classList.remove("empty");
    }
    updateBeamHealth();
    toast((plan.disclaimer || "PLANNING ONLY — CPA REVIEW") + "");
  }

  const benchEl = document.getElementById("bench");
  if (benchEl) {
    function runAct(btn) {
      if (!btn) return;
      if (role === "fd") {
        toast("Shutter locked — Front Desk cannot mutate");
        return;
      }
      const act = btn.dataset.act;
      if (act === "sync") return void doSync(btn);
      if (act === "refresh") return void doRefreshPeriod();
      if (act === "tax") return void doTax();
      if (act === "ask-hal") {
        openAskHal();
        return;
      }
      if (act === "align") {
        openAlignmentBench();
        return;
      }
    }
    benchEl.addEventListener("click", (e) => {
      const filmSlot = e.target.closest("#film .slot");
      if (filmSlot) {
        openClaimsFromFilm(filmSlot);
        return;
      }
      const closeStep = e.target.closest("#close-steps [data-step]");
      if (closeStep) {
        runCloseStep(closeStep);
        return;
      }
      const actBtn = e.target.closest("[data-act]");
      if (actBtn) {
        runAct(actBtn);
        return;
      }
      const emitter = e.target.closest(".emitter[data-go]");
      if (emitter) {
        openEmitter(emitter.getAttribute("data-go"));
      }
    });
    benchEl.addEventListener("keydown", (e) => {
      if (e.key !== "Enter" && e.key !== " ") return;
      const filmSlot = e.target.closest("#film .slot");
      if (filmSlot) {
        e.preventDefault();
        openClaimsFromFilm(filmSlot);
        return;
      }
      const closeStep = e.target.closest("#close-steps [data-step]");
      if (closeStep) {
        e.preventDefault();
        runCloseStep(closeStep);
        return;
      }
      const btn = e.target.closest("[data-act]");
      if (btn) {
        if (btn.tagName === "BUTTON") return;
        e.preventDefault();
        runAct(btn);
        return;
      }
      const emitter = e.target.closest(".emitter[data-go]");
      if (emitter && e.target === emitter) {
        e.preventDefault();
        openEmitter(emitter.getAttribute("data-go"));
      }
    });
  }

  bootWire();
  setInterval(refreshLasers, 60000);
})();
