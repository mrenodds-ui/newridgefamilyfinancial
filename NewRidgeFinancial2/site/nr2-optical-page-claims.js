/* Claims optical bench — outstanding list + click dossier (schedule-style) */
(function () {
  const W = window.NR2OpticalWire;
  if (!W) return;

  let clActiveClaimId = "";
  let clActivePatientId = "";

  function shortHash(h) {
    const s = String(h || "").replace(/^#/, "").trim();
    if (!s) return "—";
    return "#" + s.slice(0, 4);
  }

  function displayPatientName(obj) {
    const name = String((obj && obj.patientName) || "").trim();
    if (name) return name;
    const initials = String((obj && obj.initials) || "").trim();
    if (initials) return initials;
    return "—";
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

  function fmtClaimAmount(amount) {
    if (amount == null || amount === "") return "—";
    const n = W.money ? W.money(amount) : Number(amount);
    if (n == null || !Number.isFinite(n)) return "—";
    if (n === 0) return "—";
    if (W.fmtMoney) {
      const shown = W.fmtMoney(n);
      return shown || "—";
    }
    return "$" + n.toLocaleString("en-US", { maximumFractionDigits: 2 });
  }

  function setDossierMessage(text, isFault) {
    const panel = document.getElementById("cl-dossier");
    const body = document.getElementById("cl-dossier-body");
    const wrap = document.getElementById("cl-body");
    if (!panel || !body) return;
    panel.hidden = false;
    if (wrap) wrap.classList.add("has-dossier");
    body.textContent = "";
    const p = document.createElement("p");
    p.className = isFault ? "d-fault" : "";
    p.style.margin = "0";
    p.textContent = text;
    body.appendChild(p);
  }

  function appendRows(body, rows) {
    rows.forEach(function (pair) {
      const row = document.createElement("div");
      row.className = "d-row";
      const k = document.createElement("span");
      k.textContent = pair[0];
      const v = document.createElement("span");
      v.textContent = pair[1];
      row.appendChild(k);
      row.appendChild(v);
      body.appendChild(row);
    });
  }

  function renderClaimDossier(claim, mini, review) {
    const panel = document.getElementById("cl-dossier");
    const body = document.getElementById("cl-dossier-body");
    const wrap = document.getElementById("cl-body");
    if (!panel || !body) return;
    panel.hidden = false;
    if (wrap) wrap.classList.add("has-dossier");
    body.textContent = "";

    const age = claimAgeDays(claim && claim.serviceDate);
    appendRows(body, [
      ["Patient", displayPatientName(claim)],
      ["Claim", String((claim && claim.claimId) || "—")],
      ["Payer", String((claim && claim.payer) || "—")],
      ["Service", String((claim && claim.serviceDate) || "—").slice(0, 10) || "—"],
      ["Amount", fmtClaimAmount(claim && claim.amount)],
      ["Status", String((claim && claim.status) || "—")],
      ["Age", age == null ? "—" : String(age) + " days"],
      ["Hash", shortHash((claim && claim.patientHash) || (mini && mini.patientHash))],
    ]);

    const rev = review && typeof review === "object" ? review : null;
    if (rev && rev.ok) {
      const nar = rev.narrative && typeof rev.narrative === "object" ? rev.narrative : null;
      if (nar && nar.text) {
        const nHead = document.createElement("h4");
        nHead.className = "wk-dossier-sub";
        nHead.textContent = "Review narrative";
        body.appendChild(nHead);
        const nP = document.createElement("p");
        nP.className = "wk-dossier-muted";
        nP.style.whiteSpace = "pre-wrap";
        nP.textContent = String(nar.text);
        body.appendChild(nP);
        if (nar.nextAction) {
          const act = document.createElement("p");
          act.style.margin = "0.35rem 0 0";
          act.innerHTML = "";
          const strong = document.createElement("strong");
          strong.textContent = "Next: ";
          act.appendChild(strong);
          act.appendChild(document.createTextNode(String(nar.nextAction)));
          body.appendChild(act);
        }
      }

      const check = rev.checklist && typeof rev.checklist === "object" ? rev.checklist : null;
      const items = check && Array.isArray(check.items) ? check.items : [];
      if (items.length) {
        const cHead = document.createElement("h4");
        cHead.className = "wk-dossier-sub";
        cHead.textContent =
          "Preflight" +
          (check.ready ? " · clear" : " · " + String(check.gapCount || items.filter(function (i) { return !i.ok; }).length) + " gap(s)");
        body.appendChild(cHead);
        const ul = document.createElement("ul");
        ul.className = "wk-claim-list";
        items.forEach(function (it) {
          if (!it || typeof it !== "object") return;
          const li = document.createElement("li");
          li.textContent =
            (it.ok ? "✓ " : "✗ ") +
            String(it.label || it.id || "check") +
            (it.detail ? " — " + String(it.detail) : "");
          if (!it.ok) li.style.color = "var(--nr2-warn, #a67c00)";
          ul.appendChild(li);
        });
        body.appendChild(ul);
      }

      const procs = Array.isArray(rev.procedures) ? rev.procedures : [];
      const pHead = document.createElement("h4");
      pHead.className = "wk-dossier-sub";
      pHead.textContent = "SoftDent procedures (DOS)";
      body.appendChild(pHead);
      if (!procs.length) {
        const empty = document.createElement("p");
        empty.className = "wk-dossier-muted";
        empty.textContent = "No SoftDent TXN lines for this DOS — empty ≠ $0";
        body.appendChild(empty);
      } else {
        const ul = document.createElement("ul");
        ul.className = "wk-claim-list";
        procs.slice(0, 12).forEach(function (p) {
          if (!p || typeof p !== "object") return;
          const li = document.createElement("li");
          const amt =
            p.production == null || p.production === ""
              ? ""
              : " · $" + Number(p.production).toLocaleString("en-US", { maximumFractionDigits: 2 });
          li.textContent =
            String(p.code || "—") +
            " · " +
            String(p.kind || "line") +
            amt +
            (p.providerId ? " · Dr " + String(p.providerId) : "");
          ul.appendChild(li);
        });
        body.appendChild(ul);
      }

      const revActions = document.createElement("div");
      revActions.className = "wk-dossier-actions";
      if (nar && nar.phoneCopy) {
        const copyBtn = document.createElement("button");
        copyBtn.type = "button";
        copyBtn.className = "btn-quiet";
        copyBtn.textContent = "Copy for phone";
        copyBtn.addEventListener("click", function () {
          const text = String(nar.phoneCopy || "");
          if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(text).catch(function () {});
          }
          copyBtn.textContent = "Copied";
          setTimeout(function () {
            copyBtn.textContent = "Copy for phone";
          }, 1200);
        });
        revActions.appendChild(copyBtn);
      }
      body.appendChild(revActions);
    } else if (rev && rev.error) {
      const p = document.createElement("p");
      p.className = "wk-dossier-muted";
      p.textContent =
        String(rev.emptyMessage || rev.error || "Review unavailable") +
        " · SoftDent READ-ONLY · empty ≠ $0";
      body.appendChild(p);
    }

    if (!mini) {
      const note = document.createElement("p");
      note.className = "wk-dossier-muted";
      note.textContent =
        "No SoftDent patient id for name join — claim detail only · empty ≠ $0";
      body.appendChild(note);
      return;
    }

    if (mini.ok === false) {
      const p = document.createElement("p");
      p.className = "d-fault";
      p.textContent =
        String(mini.error || "Mini dossier unavailable") + " · SoftDent READ-ONLY · empty ≠ $0";
      body.appendChild(p);
      return;
    }

    const head = document.createElement("h4");
    head.className = "wk-dossier-sub";
    head.textContent = "Patient (SoftDent)";
    body.appendChild(head);
    appendRows(body, [
      ["Carrier", mini.primaryCarrier != null ? String(mini.primaryCarrier) : "—"],
      ["Open claims", mini.openClaims != null ? String(mini.openClaims) : "—"],
      ["Last visit", mini.lastVisit != null ? String(mini.lastVisit) : "—"],
      ["Clinical notes", mini.hasClinicalNotes ? "yes" : "none / unknown"],
      [
        "Account $",
        mini.accountBalance != null ? String(mini.accountBalance) : "unavailable",
      ],
    ]);
    if (mini.schemaGap) {
      const gap = document.createElement("p");
      gap.className = "wk-dossier-muted";
      gap.textContent = String(mini.schemaGap);
      body.appendChild(gap);
    }

    const claims = mini.claims && typeof mini.claims === "object" ? mini.claims : null;
    const claimItems = claims && Array.isArray(claims.items) ? claims.items : [];
    const claimsHead = document.createElement("h4");
    claimsHead.className = "wk-dossier-sub";
    claimsHead.textContent = "Other claims (same patient)";
    body.appendChild(claimsHead);
    if (!claimItems.length) {
      const empty = document.createElement("p");
      empty.className = "wk-dossier-muted";
      empty.textContent =
        (claims && (claims.emptyMessage || claims.error)) ||
        "No additional SoftDent claims for this patient.";
      body.appendChild(empty);
    } else {
      const ul = document.createElement("ul");
      ul.className = "wk-claim-list";
      claimItems.slice(0, 5).forEach(function (c) {
        if (!c || typeof c !== "object") return;
        const li = document.createElement("li");
        const amt =
          c.amount == null || c.amount === ""
            ? "—"
            : typeof c.amount === "number"
              ? "$" + c.amount.toLocaleString("en-US", { maximumFractionDigits: 2 })
              : String(c.amount);
        li.textContent =
          shortHash(c.claimHash || c.claimId) +
          " · " +
          String(c.payer || "unknown") +
          " · " +
          String(c.serviceDate || "—") +
          " · " +
          amt +
          " · " +
          String(c.status || "—");
        ul.appendChild(li);
      });
      body.appendChild(ul);
    }

    const pid = String(
      (claim && claim.patientId) ||
        (rev && rev.claim && rev.claim.patientId) ||
        ""
    ).trim();
    const ph = shortHash(
      (claim && claim.patientHash) ||
        (mini && mini.patientHash) ||
        (rev && rev.claim && rev.claim.patientHash)
    ).replace(/^#/, "");
    if (pid) {
      const actions = document.createElement("div");
      actions.className = "wk-dossier-actions";
      const halBtn = document.createElement("button");
      halBtn.type = "button";
      halBtn.className = "btn-quiet";
      halBtn.textContent = "Ask HAL about this claim →";
      halBtn.addEventListener("click", function () {
        askHalAboutClaim(claim, pid, ph);
      });
      actions.appendChild(halBtn);
      body.appendChild(actions);
    }
  }

  function askHalAboutClaim(claim, patientId, patientHash) {
    const pid = String(patientId || "").trim();
    const ph = String(patientHash || "").replace(/^#/, "").trim();
    if (!pid) {
      setDossierMessage("Cannot hand off to HAL — SoftDent patient id missing.", true);
      return;
    }
    const ctx = {
      patientId: pid,
      patientHash: ph,
      initials: String((claim && claim.initials) || "P—"),
      claimId: String((claim && claim.claimId) || ""),
      payer: String((claim && claim.payer) || ""),
      serviceDate: String((claim && claim.serviceDate) || "").slice(0, 10),
      amount: claim && claim.amount,
      at: Date.now(),
      ttlMs: 30 * 60 * 1000,
    };
    try {
      sessionStorage.setItem("nr2.hal.patientContext", JSON.stringify(ctx));
      sessionStorage.setItem(
        "nr2.hal.seedPrompt",
        "Review unpaid SoftDent claim " +
          String(ctx.claimId || "") +
          " for " +
          displayPatientName(claim) +
          " · payer " +
          String(ctx.payer || "—") +
          " · DOS " +
          String(ctx.serviceDate || "—") +
          " · SoftDent READ-ONLY · empty ≠ $0. Give a short narrative and next staff action."
      );
    } catch (_) {}
    if (W.postJson && ph) {
      W.postJson(
        "/api/audit/hal-patient-context",
        {
          patientHash: ph,
          action: "context_set",
          toolsUsed: '["claims_ask_hal_claim"]',
        },
        8000
      ).catch(function () {});
    }
    window.location.href =
      "/nr2-optical-page-hal.html?patientId=" +
      encodeURIComponent(pid) +
      "&patientHash=" +
      encodeURIComponent(ph) +
      "&autoSummarize=1";
  }

  function askHalAboutPatient(patientId, patientHash, initials) {
    askHalAboutClaim(
      { patientId: patientId, patientHash: patientHash, initials: initials },
      patientId,
      patientHash
    );
  }

  async function openClaimContext(claim) {
    const cid = String((claim && claim.claimId) || "").trim();
    const pid = String((claim && claim.patientId) || "").trim();
    const ph = String((claim && claim.patientHash) || "").trim();
    clActiveClaimId = cid;
    clActivePatientId = pid;
    document.querySelectorAll("#cl-tbody tr.is-active").forEach(function (el) {
      el.classList.remove("is-active");
    });
    setDossierMessage("Loading claim review…");
    let review = null;
    let mini = null;
    try {
      if (W.ensureSession) await W.ensureSession();
      if (ph && W.postJson) {
        W.postJson(
          "/api/audit/hal-patient-context",
          { patientHash: ph, action: "set_context", toolsUsed: '["claims_row_click"]' },
          8000
        ).catch(function () {});
      }
      const reviewReq = W.postJson
        ? W.postJson("/api/softdent/claims-review", claim || {}, 15000)
        : W.getJson(
            "/api/softdent/claims-review?claimId=" + encodeURIComponent(cid),
            15000
          );
      const miniReq = pid
        ? W.getJson("/api/apex/patient-dossier-mini/" + encodeURIComponent(pid), 12000)
        : Promise.resolve({ ok: false, data: null });
      const settled = await Promise.all([reviewReq, miniReq]);
      if (clActiveClaimId !== cid) return;
      const revRes = settled[0];
      const miniRes = settled[1];
      if (revRes && revRes.ok && revRes.data) review = revRes.data;
      if (miniRes && miniRes.ok && miniRes.data) mini = miniRes.data;
      if (review && review.claim && review.claim.patientId && !claim.patientId) {
        claim.patientId = review.claim.patientId;
        claim.patientHash = review.claim.patientHash || claim.patientHash;
        clActivePatientId = String(claim.patientId || "");
      }
      renderClaimDossier(claim, mini, review);
    } catch (err) {
      if (clActiveClaimId !== cid) return;
      setDossierMessage(
        "Claim review fault · " + String(err && err.message ? err.message : err),
        true
      );
      renderClaimDossier(claim, null, null);
    }
  }

  function renderClaimsOutstanding(data) {
    const tbody = document.getElementById("cl-tbody");
    const summary = document.getElementById("cl-summary");
    const rangeEl = document.getElementById("cl-range-label");
    if (!tbody) return;
    tbody.textContent = "";
    let claims = data && Array.isArray(data.claims) ? data.claims.slice() : [];
    const count = data && data.count != null ? Number(data.count) : claims.length;
    const sampleLimit =
      data && data.sampleLimit != null ? Number(data.sampleLimit) : claims.length;
    const total =
      data && data.totalOutstanding != null ? W.money(data.totalOutstanding) : null;
    let totalBit = "total —";
    if (total != null && total !== 0) {
      const shown = W.fmtMoney ? W.fmtMoney(total) : "$" + String(total);
      if (shown) totalBit = "total " + shown;
    } else if (data && data.hasData && (total == null || total === 0)) {
      totalBit = "total empty (not zero)";
    }
    if (rangeEl) {
      rangeEl.textContent =
        String(Math.min(claims.length, sampleLimit || claims.length)) +
        " of " +
        String(count) +
        " open";
    }
    if (summary) {
      summary.textContent =
        String(count) +
        " open claim" +
        (count === 1 ? "" : "s") +
        " · " +
        totalBit +
        " · SoftDent READ-ONLY · empty ≠ $0";
    }
    if (!claims.length) {
      const tr = document.createElement("tr");
      const td = document.createElement("td");
      td.colSpan = 6;
      td.className = "cl-empty";
      td.textContent =
        (data && data.emptyMessage) ||
        "No outstanding SoftDent claims in sample — sync SoftDent or empty queue.";
      tr.appendChild(td);
      tbody.appendChild(tr);
      return;
    }
    // SoftDent unpaid only — never show paid/completed/denied/closed rows.
    claims = claims.filter(function (c) {
      const st = String((c && c.status) || "")
        .trim()
        .toLowerCase();
      if (!st) return true;
      if (
        st === "paid" ||
        st === "closed" ||
        st === "complete" ||
        st === "completed" ||
        st === "denied" ||
        st === "done" ||
        st === "settled" ||
        st.indexOf("paid") === 0 ||
        st.indexOf("complete") >= 0
      ) {
        return false;
      }
      return true;
    });
    if (!claims.length) {
      const tr = document.createElement("tr");
      const td = document.createElement("td");
      td.colSpan = 6;
      td.className = "cl-empty";
      td.textContent = "No unpaid SoftDent claims in sample — empty ≠ $0.";
      tr.appendChild(td);
      tbody.appendChild(tr);
      return;
    }
    claims.sort(function (a, b) {
      const aa = claimAgeDays(a && a.serviceDate);
      const bb = claimAgeDays(b && b.serviceDate);
      if (aa == null && bb == null) return 0;
      if (aa == null) return 1;
      if (bb == null) return -1;
      return bb - aa;
    });
    claims.forEach(function (c) {
      if (!c || typeof c !== "object") return;
      const tr = document.createElement("tr");
      const cid = String(c.claimId || "");
      const age = claimAgeDays(c.serviceDate);
      const ageCls = claimAgeClass(age);
      tr.classList.add(ageCls);
      if (cid) tr.setAttribute("data-claim-id", cid);
      if (clActiveClaimId && cid && cid === clActiveClaimId) {
        tr.classList.add("is-active");
      }
      const cells = [
        displayPatientName(c),
        String(c.payer || "—") || "—",
        String(c.serviceDate || "—").slice(0, 10) || "—",
        fmtClaimAmount(c.amount),
        String(c.status || "—") || "—",
        age == null ? "—" : String(age) + "d",
      ];
      cells.forEach(function (text, idx) {
        const td = document.createElement("td");
        if (idx === 0) td.className = "phi-name";
        if (idx === 3 || idx === 5) td.className = "num";
        if (idx === 5) td.classList.add("age-cell");
        td.textContent = text;
        tr.appendChild(td);
      });
      tr.title =
        "Open claim context · " +
        (cid || "—") +
        " · age " +
        (age == null ? "unknown" : String(age) + "d");
      tr.addEventListener("click", function () {
        tr.classList.add("is-active");
        openClaimContext(c);
      });
      tbody.appendChild(tr);
    });
  }

  async function loadClaimsOutstanding() {
    const summary = document.getElementById("cl-summary");
    const tbody = document.getElementById("cl-tbody");
    const rangeEl = document.getElementById("cl-range-label");
    if (summary) summary.textContent = "Loading outstanding claims…";
    if (tbody) tbody.textContent = "";
    const res = await W.getJson("/api/softdent/claims-outstanding?limit=200", 20000);
    if (!res.ok || !res.data) {
      if (summary) {
        summary.textContent =
          "Outstanding claims NO SIGNAL · " +
          String((res.data && res.data.error) || res.status || "fetch failed");
      }
      if (rangeEl) rangeEl.textContent = "NO SIGNAL";
      if (tbody) {
        const tr = document.createElement("tr");
        const td = document.createElement("td");
        td.colSpan = 6;
        td.className = "cl-fault";
        td.textContent = "Could not load SoftDent claims — empty ≠ $0";
        tr.appendChild(td);
        tbody.appendChild(tr);
      }
      return { ok: false, data: null };
    }
    renderClaimsOutstanding(res.data);
    try {
      const raw = sessionStorage.getItem("nr2.claims.focus");
      if (raw) {
        sessionStorage.removeItem("nr2.claims.focus");
        const focus = JSON.parse(raw);
        const claimId = String((focus && focus.claimId) || "").trim();
        if (claimId && res.data && Array.isArray(res.data.claims)) {
          const match = res.data.claims.find(function (c) {
            return String(c.claimId || "").trim() === claimId;
          });
          if (match) {
            openClaimContext(match);
            const rows = document.querySelectorAll("#cl-tbody tr[data-claim-id]");
            rows.forEach(function (row) {
              if (row.getAttribute("data-claim-id") === claimId) {
                row.classList.add("is-active");
                row.scrollIntoView({ block: "nearest", behavior: "smooth" });
              }
            });
          }
        }
      }
    } catch (_) {}
    return { ok: true, data: res.data };
  }

  function wireClaimsControls() {
    const btn = document.getElementById("btn-cl-refresh");
    if (btn && !btn._nr2ClBound) {
      btn._nr2ClBound = true;
      btn.addEventListener("click", function () {
        loadClaimsOutstanding().catch(function (err) {
          const summary = document.getElementById("cl-summary");
          if (summary) {
            summary.textContent =
              "Claims refresh fault · " + String(err && err.message ? err.message : err);
          }
        });
      });
    }
    const closeBtn = document.getElementById("btn-cl-dossier-close");
    if (closeBtn && !closeBtn._nr2ClBound) {
      closeBtn._nr2ClBound = true;
      closeBtn.addEventListener("click", function () {
        const panel = document.getElementById("cl-dossier");
        const wrap = document.getElementById("cl-body");
        if (panel) panel.hidden = true;
        if (wrap) wrap.classList.remove("has-dossier");
        clActiveClaimId = "";
        clActivePatientId = "";
        document.querySelectorAll("#cl-tbody tr.is-active").forEach(function (el) {
          el.classList.remove("is-active");
        });
      });
    }
  }

  async function boot() {
    W.setText("val-snap", null, "—");
    W.setText("val-era", "UNAVAILABLE");
    W.setText("val-denials", null, "—");
    W.setText("val-over30", null, "—");
    W.setBanner("partial", "Wiring claims feed · empty ≠ $0 · no SoftDent write-back");
    wireClaimsControls();

    const [claimsRes, aging, adj, ready] = await Promise.all([
      loadClaimsOutstanding(),
      W.getJson("/api/claims/aging-summary", 12000),
      W.getJson("/api/softdent/adjustment-log", 12000),
      W.getJson("/api/import-readiness", 12000),
    ]);
    const claims = {
      ok: !!(claimsRes && claimsRes.ok),
      data: claimsRes && claimsRes.data,
    };
    const readyData = ready.ok ? ready.data : null;
    const claimsStale = readyData
      ? W.keysHit(W.laserKeys(readyData), ["softdent.claims", "softdent."])
      : false;

    let live = false;
    if (claims.ok && claims.data && claims.data.hasData) {
      const list = Array.isArray(claims.data.claims) ? claims.data.claims : [];
      const count =
        claims.data.count != null ? Number(claims.data.count) : list.length;
      const total = W.money(claims.data.totalOutstanding);
      if (total == null || Number(total) === 0) {
        W.setText("val-snap", null, "empty (not zero)");
        const sh = document.getElementById("hint-snap");
        if (sh) {
          sh.textContent =
            "Outstanding total empty · count " +
            count +
            " · SoftDent READ-ONLY · empty ≠ $0";
        }
      } else {
        const shown = W.fmtMoney(total);
        if (shown) {
          W.setText("val-snap", shown + " · " + count);
          live = true;
        } else {
          W.setText("val-snap", null, "∅");
        }
      }
      const pending = list.filter(function (c) {
        return /pending|denial|denied|review/i.test(String(c.status || ""));
      });
      if (pending.length) {
        W.setText("val-denials", String(pending.length) + " in sample");
        const dh = document.getElementById("hint-denials");
        if (dh) {
          dh.textContent =
            "status flags in top sample · full open count " +
            count +
            " · empty ≠ $0";
        }
      } else {
        W.setText("val-denials", null, "∅");
      }
    } else {
      W.setText("val-snap", null, "NO SIGNAL");
      W.setText("val-denials", null, "NO SIGNAL");
    }

    if (aging.ok && aging.data && aging.data.hasData) {
      W.setText(
        "val-over30",
        String(aging.data.over30) + " / " + String(aging.data.count)
      );
      live = true;
    } else if (aging.ok && aging.data && aging.data.hasData === false) {
      W.setText("val-over30", null, "∅");
    }

    if (
      adj.ok &&
      adj.data &&
      adj.data.hasData &&
      Array.isArray(adj.data.adjustments) &&
      adj.data.adjustments.length
    ) {
      const tip = adj.data.adjustments[0];
      const amt = W.fmtMoney(W.money(tip && tip.amount));
      W.setText("val-era", amt ? "ADJ LOG " + amt : "ADJ LOG");
      const eraHint = document.getElementById("hint-era");
      if (eraHint) {
        eraHint.textContent =
          "ERA UNAVAILABLE · SoftDent adjustment-log" +
          (tip && tip.date ? " · " + tip.date : "") +
          " · read-only";
      }
      live = true;
    } else {
      W.setText("val-era", "UNAVAILABLE");
      const eraHint = document.getElementById("hint-era");
      if (eraHint) {
        eraHint.textContent = "ERA ingest pack removed · no SoftDent write-back";
      }
    }

    W.setBanner(
      claimsStale ? "partial" : live ? "live" : "partial",
      claimsStale
        ? "Claims STALE · lasers red on softdent · list + dossier · empty ≠ $0"
        : "Claims list LIVE · click row for context · ERA UNAVAILABLE · empty ≠ $0"
    );
  }

  boot().catch(function (err) {
    W.setBanner(
      "partial",
      "Claims wire fault · " + String(err && err.message ? err.message : err)
    );
  });
})();
