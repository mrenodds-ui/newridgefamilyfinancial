/* Office Manager — readiness + SoftDent ops · Force Close · Mon–Thu list · no fake board actions */
(function () {
  const W = window.NR2OpticalWire;
  if (!W) return;

  function countApptSlots(data) {
    if (!data || !Array.isArray(data.operatories)) return null;
    let n = 0;
    data.operatories.forEach(function (op) {
      if (op && Array.isArray(op.slots)) n += op.slots.length;
    });
    return n;
  }

  function todayIsoLocal() {
    const d = new Date();
    const y = d.getFullYear();
    const m = String(d.getMonth() + 1).padStart(2, "0");
    const day = String(d.getDate()).padStart(2, "0");
    return y + "-" + m + "-" + day;
  }

  function shortHash(h) {
    const s = String(h || "").replace(/^#/, "").trim();
    if (!s) return "—";
    return "#" + s.slice(0, 4);
  }

  function renderWeeklySchedule(data) {
    const grid = document.getElementById("wk-days-grid");
    const rangeEl = document.getElementById("wk-range-label");
    if (!grid) return;
    grid.textContent = "";
    const days = data && Array.isArray(data.days) ? data.days : [];
    if (rangeEl) {
      rangeEl.textContent = data && data.dateRange ? String(data.dateRange) : "—";
    }
    if (!days.length) {
      const p = document.createElement("p");
      p.className = "wk-empty";
      p.textContent =
        (data && data.emptyMessage) ||
        "No Mon–Thu SoftDent appointments — sync SoftDent or empty week.";
      grid.appendChild(p);
      return;
    }
    const today = todayIsoLocal();
    days.forEach(function (day) {
      if (!day || typeof day !== "object") return;
      const col = document.createElement("article");
      const dateIso = String(day.date || "").slice(0, 10);
      col.className = "wk-day" + (dateIso === today ? " is-today" : "");

      const head = document.createElement("div");
      head.className = "wk-day-head";
      const title = document.createElement("span");
      title.textContent =
        String(day.dayName || "").slice(0, 3) +
        (dateIso ? " · " + dateIso.slice(5) : "");
      const count = document.createElement("span");
      count.className = "wk-count";
      const n = typeof day.count === "number" ? day.count : (day.slots || []).length;
      count.textContent = String(n) + " appt" + (n === 1 ? "" : "s");
      head.appendChild(title);
      head.appendChild(count);
      col.appendChild(head);

      const slots = Array.isArray(day.slots) ? day.slots : [];
      if (!slots.length) {
        const empty = document.createElement("p");
        empty.className = "wk-empty";
        empty.textContent =
          String(day.emptyMessage || "").trim() || "No SoftDent appointments.";
        col.appendChild(empty);
      } else {
        const ul = document.createElement("ul");
        ul.className = "wk-slots";
        slots.forEach(function (slot) {
          if (!slot || typeof slot !== "object") return;
          const li = document.createElement("li");
          li.className = "wk-slot";
          const phi = document.createElement("span");
          phi.className = "phi";
          const initials = String(slot.initials || "P—").trim() || "P—";
          phi.textContent = initials + " · " + shortHash(slot.patientHash);
          const prov = document.createElement("span");
          prov.className = "prov";
          prov.textContent = String(slot.provider || "—");
          prov.title = String(slot.provider || "");
          const st = document.createElement("span");
          st.className = "st";
          st.textContent = String(slot.status || "scheduled");
          const tm = document.createElement("span");
          tm.className = "tm";
          tm.textContent = "time " + (String(slot.time || "—").trim() || "—");
          li.appendChild(phi);
          li.appendChild(prov);
          li.appendChild(st);
          li.appendChild(tm);
          ul.appendChild(li);
        });
        col.appendChild(ul);
      }
      grid.appendChild(col);
    });
  }

  async function loadWeeklySchedule() {
    const grid = document.getElementById("wk-days-grid");
    if (grid) {
      grid.textContent = "";
      const p = document.createElement("p");
      p.className = "wk-loading";
      p.id = "wk-loading";
      p.textContent = "Loading Mon–Thu schedule…";
      grid.appendChild(p);
    }
    // Server defaults start=monday_of_week_iso when omitted
    const res = await W.getJson("/api/softdent/appointments-range?days=4", 15000);
    if (!res.ok || !res.data) {
      if (grid) {
        grid.textContent = "";
        const p = document.createElement("p");
        p.className = "wk-fault";
        p.textContent =
          "Mon–Thu schedule NO SIGNAL · " +
          String((res.data && res.data.error) || res.status || "fetch failed");
        grid.appendChild(p);
      }
      const rangeEl = document.getElementById("wk-range-label");
      if (rangeEl) rangeEl.textContent = "NO SIGNAL";
      return false;
    }
    renderWeeklySchedule(res.data);
    return !!(res.data.hasData || (res.data.days && res.data.days.length));
  }

  function wireWeeklyRefresh() {
    const btn = document.getElementById("btn-wk-refresh");
    if (!btn || btn._nr2WkBound) return;
    btn._nr2WkBound = true;
    btn.addEventListener("click", function () {
      loadWeeklySchedule().catch(function (err) {
        const grid = document.getElementById("wk-days-grid");
        if (!grid) return;
        grid.textContent = "";
        const p = document.createElement("p");
        p.className = "wk-fault";
        p.textContent = "Mon–Thu refresh fault · " + String(err && err.message ? err.message : err);
        grid.appendChild(p);
      });
    });
  }

  function gapKeys(ready) {
    const keys = [];
    const seen = {};
    function add(list) {
      (list || []).forEach(function (g) {
        if (!g || typeof g !== "object") return;
        const k = String(g.datasetKey || g.key || "").trim();
        if (!k || seen[k]) return;
        seen[k] = true;
        keys.push(k);
      });
    }
    add(ready.blocking);
    const gaps = (ready.datasetGaps || []).concat(
      (ready.completeness && ready.completeness.softGaps) || []
    );
    add(
      gaps.filter(function (g) {
        return g && /stale|missing|partial/i.test(String(g.status || ""));
      })
    );
    return keys;
  }

  function wireForceClose(readyData, readyOk) {
    const btn = document.getElementById("btn-force-close");
    if (!btn || btn._nr2ForceBound) return;
    btn._nr2ForceBound = true;
    btn.addEventListener("click", async function () {
      if (btn.disabled || btn.classList.contains("busy")) return;
      btn.classList.add("busy");
      btn.disabled = true;
      btn.textContent = "CLOSING…";
      W.setBanner("partial", "OM FORCE CLOSE · SoftDent pull if lasers red / stalled · empty ≠ $0");
      try {
        await W.ensureSession();
        const res = await W.forcePeriodClose({ actor: "optical-om" });
        const data = res && res.data ? res.data : {};
        const ok = !!(res && res.ok && data.ok);
        const status = String(data.status || (ok ? "completed" : "failed")).toUpperCase();
        const pull =
          data.pullSoftdentDecided === true
            ? " · SoftDent pull"
            : data.pullSoftdentDecided === false
              ? " · attest-only"
              : "";
        const hash = data.beamHash ? " · hash " + String(data.beamHash).slice(0, 8) : "";
        const fallback = data.fallback ? " · " + String(data.fallback) : "";
        W.setBanner(
          ok ? "live" : "partial",
          "OM FORCE CLOSE · " +
            status +
            pull +
            fallback +
            hash +
            (ok ? "" : " · " + String(data.error || "failed")) +
            " · empty ≠ $0"
        );
        if (ok) {
          W.setText("val-close", status);
          const el = document.getElementById("val-close");
          if (el) el.classList.remove("stale");
        } else if (String(data.status || "").toLowerCase() === "blocked") {
          W.setText("val-close", "BLOCKED");
          const el = document.getElementById("val-close");
          if (el) el.classList.add("stale");
        }
      } catch (err) {
        W.setBanner(
          "partial",
          "OM FORCE CLOSE fault · " + String(err && err.message ? err.message : err)
        );
      } finally {
        btn.classList.remove("busy");
        btn.textContent = "FORCE CLOSE";
        setTimeout(function () {
          boot();
        }, 400);
      }
    });
  }

  async function boot() {
    W.setBanner("partial", "OM wiring readiness + SoftDent day pulse · empty ≠ $0");
    W.setText("val-close", null, "—");
    W.setText("val-ready", null, "—");
    W.setText("val-ops", null, "—");
    W.setText("val-gaps", null, "—");
    W.setText("val-health", null, "—");

    wireWeeklyRefresh();
    const [ready, health, np, appt, weeklyOk] = await Promise.all([
      W.getJson("/api/import-readiness", 12000),
      W.getJson("/api/health", 12000),
      W.getJson("/api/softdent/new-patients-mtd", 12000),
      W.getJson("/api/softdent/appointments-today", 12000),
      loadWeeklySchedule().catch(function () {
        return false;
      }),
    ]);

    let live = !!weeklyOk;
    let blocked = false;
    let closeTrouble = false;
    let readyData = null;
    let pc = null;

    if (ready.ok && ready.data) {
      readyData = ready.data;
      const blocking = Array.isArray(readyData.blocking) ? readyData.blocking.length : 0;
      blocked = W.lasersRed ? W.lasersRed(readyData) : blocking > 0;
      closeTrouble = W.periodCloseIsTrouble ? W.periodCloseIsTrouble(readyData) : false;
      pc = W.periodCloseStatus ? W.periodCloseStatus(readyData) : null;
      const closeBit = W.periodCloseBannerBit
        ? W.periodCloseBannerBit(readyData)
        : "CLOSE · UNKNOWN";
      if (pc) {
        W.setText("val-close", String(pc.status || "unknown").toUpperCase());
        const ch = document.getElementById("hint-close");
        if (ch) {
          ch.textContent =
            closeBit + " · FORCE CLOSE pulls SoftDent when lasers red / stalled · empty ≠ $0";
        }
        if (closeTrouble) {
          const el = document.getElementById("val-close");
          if (el) el.classList.add("stale");
        }
      } else {
        W.setText("val-close", "NO SIGNAL");
      }
      const level = String(readyData.level || "unknown").toUpperCase();
      const sum = readyData.summary || {};
      const laserKeys = W.laserKeys ? W.laserKeys(readyData) : [];
      W.setText(
        "val-ready",
        level +
          (blocked ? " · lasers red" : " · lasers clear") +
          (blocking ? " · block " + blocking : "") +
          (sum.stale != null ? " · stale " + sum.stale : "")
      );
      const keys = laserKeys.length ? laserKeys : gapKeys(readyData);
      if (keys.length) {
        W.setText("val-gaps", keys.slice(0, 3).join(" · ") + (keys.length > 3 ? " +" + (keys.length - 3) : ""));
        const gh = document.getElementById("hint-gaps");
        if (gh) {
          gh.textContent =
            keys.length +
            " key(s)" +
            (blocked ? " · lasers RED" : " · soft gaps") +
            " · empty ≠ $0";
        }
      } else {
        W.setText("val-gaps", "NONE");
      }
      const hint = document.getElementById("hint-ready");
      if (hint) {
        hint.textContent = blocked
          ? "Blocking / lasers red · money reads STALE on main"
          : closeTrouble
            ? "Lasers clear but period-close " + String((pc && pc.status) || "trouble") + " — not LIVE OPS"
            : "No laser block · brief soft stale under TTL stays green";
      }
      live = true;
    } else {
      W.setText("val-close", "NO SIGNAL");
      W.setText("val-ready", "NO SIGNAL");
      W.setText("val-gaps", "NO SIGNAL");
    }

    wireForceClose(readyData, ready.ok);
    if (W.bindVerifyBeamButton) {
      W.bindVerifyBeamButton("btn-verify-beam", {
        hintId: "hint-beam-proof",
        valId: "val-beam-proof",
      });
    }
    if (W.bindDeskSmokeButton) {
      W.bindDeskSmokeButton("btn-desk-smoke", {
        hintId: "hint-desk-smoke",
        valId: "val-desk-smoke",
      });
    }
    W.getJson("/api/health/desk-smoke?run=0", 8000).then(function (res) {
      if (!res || !res.ok || !res.data) return;
      const st = String(res.data.status || "NO SIGNAL").toUpperCase();
      W.setText("val-desk-smoke", st);
      const el = document.getElementById("val-desk-smoke");
      if (el) {
        el.classList.remove("stale", "hal");
        el.classList.add(st === "GREEN" ? "hal" : "stale");
      }
    });
    const btn = document.getElementById("btn-force-close");
    if (btn && !btn.classList.contains("busy")) {
      const available = W.forceCloseAvailable
        ? W.forceCloseAvailable(readyData)
        : false;
      btn.disabled = !ready.ok || !available;
    }

    const opsBits = [];
    if (np.ok && np.data && np.data.hasData && np.data.count != null) {
      opsBits.push(String(np.data.count) + " NP");
      const oh = document.getElementById("hint-ops");
      if (oh) {
        oh.textContent =
          "new patients" + (np.data.period ? " · " + np.data.period : "") + " · appointments today";
      }
      live = true;
    }
    if (appt.ok && appt.data && appt.data.hasData) {
      const slots = countApptSlots(appt.data);
      if (slots != null) {
        opsBits.push(String(slots) + " appts");
        live = true;
      }
    }
    if (opsBits.length) {
      W.setText("val-ops", opsBits.join(" · "));
    } else {
      W.setText("val-ops", null, np.ok || appt.ok ? "∅" : "NO SIGNAL");
    }

    if (health.ok && health.data) {
      const bits = [];
      bits.push(health.data.db ? "DB" : "DB↓");
      bits.push(health.data.ollama ? "OLLAMA" : "OLLAMA↓");
      if (health.data.readinessLevel) bits.push(String(health.data.readinessLevel).toUpperCase());
      W.setText("val-health", bits.join(" · "));
      live = true;
    } else {
      W.setText("val-health", "NO SIGNAL");
    }

    const closeBit = readyData && W.periodCloseBannerBit ? W.periodCloseBannerBit(readyData) : "";
    W.setBanner(
      blocked || closeTrouble ? "partial" : live ? "live" : "partial",
      blocked
        ? "OM · lasers STALE · FORCE CLOSE pulls SoftDent aging · empty ≠ $0"
        : closeTrouble
          ? "OM · " + closeBit + " · FORCE CLOSE available · empty ≠ $0"
          : "OM · SoftDent Mon–Thu list + day pulse · " +
            (closeBit || "CLOSE · idle") +
            " · FORCE CLOSE · empty ≠ $0"
    );
  }

  boot().catch((err) => {
    W.setBanner("partial", "OM wire fault · " + String(err && err.message ? err.message : err));
  });
})();

