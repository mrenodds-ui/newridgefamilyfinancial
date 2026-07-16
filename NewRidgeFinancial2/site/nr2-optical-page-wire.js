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
  function setText(id, value, emptyLabel) {
    const el = document.getElementById(id);
    if (!el) return;
    if (value == null || value === "") {
      el.textContent = emptyLabel || "—";
      el.classList.add("empty");
      return;
    }
    el.textContent = value;
    el.classList.remove("empty");
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
          const status = String(data.status || (data.ok ? "GREEN" : "RED")).toUpperCase();
          const fails = Array.isArray(data.failures) ? data.failures.join(",") : "";
          const bit =
            "DESK SMOKE · " +
            status +
            (data.deskProof ? " · proof " + data.deskProof : "") +
            (data.dataBeamHash ? " · data " + formatBeamHash(data.dataBeamHash, 8) : "") +
            (fails ? " · fail " + fails : "") +
            " · empty ≠ $0";
          if (typeof setBanner === "function") {
            setBanner(status === "GREEN" ? "live" : "partial", bit);
          }
          if (o.hintId) {
            const hint = document.getElementById(o.hintId);
            if (hint) hint.textContent = bit;
          }
          if (o.valId) {
            const el = document.getElementById(o.valId);
            if (el) {
              el.textContent = status;
              el.classList.remove("stale", "hal", "sd");
              el.classList.add(status === "GREEN" ? "hal" : "stale");
            }
          }
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
  function bootOpsGates() {
    try {
      mountOpsGates({ refreshMs: 60000 });
    } catch (_) {
      /* ignore mount faults — page faces still load */
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
    morningBundleGate: morningBundleGate,
    trellisGate: trellisGate,
    shadowGate: shadowGate,
    deriveOpsGates: deriveOpsGates,
    fetchOpsGates: fetchOpsGates,
    renderOpsGates: renderOpsGates,
    mountOpsGates: mountOpsGates,
  };
})(window);
