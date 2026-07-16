/* Claims optical bench — outstanding list + click dossier (schedule-style) */
(function () {
  const W = window.NR2OpticalWire;
  if (!W) return;

  let clActiveClaimId = "";
  let clActivePatientId = "";
  let clClaimsCache = null;
  let clClaimsMeta = null;

  const CLAIM_ACTION_LABELS = {
    called_payer: "Called payer",
    waiting_era: "Waiting ERA",
    needs_attachment: "Needs attachment",
    resubmit_path: "Resubmit path",
    patient_followup: "Patient follow-up",
    note: "Note",
  };

  function isGenericPayer(payer) {
    const p = String(payer || "")
      .trim()
      .toLowerCase();
    return !p || p === "insurance" || p === "unknown" || p === "n/a" || p === "-" || p === "—";
  }

  function normalizePayerKey(payer) {
    return String(payer || "")
      .trim()
      .toLowerCase()
      .replace(/\s+/g, " ");
  }

  function claimPassesFilters(c) {
    const ageSel = document.getElementById("cl-filter-age");
    const gapSel = document.getElementById("cl-filter-gap");
    const payerSel = document.getElementById("cl-filter-payer");
    const ageMode = ageSel ? String(ageSel.value || "all") : "all";
    const gapMode = gapSel ? String(gapSel.value || "all") : "all";
    const payerMode = payerSel ? String(payerSel.value || "all") : "all";
    const age = claimAgeDays(c && c.serviceDate);
    if (ageMode === "0-30" && !(age != null && age <= 30)) return false;
    if (ageMode === "31-60" && !(age != null && age >= 31 && age <= 60)) return false;
    if (ageMode === "61-90" && !(age != null && age >= 61 && age <= 90)) return false;
    if (ageMode === "90+" && !(age != null && age > 90)) return false;
    const unnamed = isGenericPayer(c && c.payer);
    const noPatient = !String((c && c.patientId) || "").trim();
    if (gapMode === "unnamed_payer" && !unnamed) return false;
    if (gapMode === "no_patient" && !noPatient) return false;
    if (gapMode === "any_gap" && !(unnamed || noPatient)) return false;
    if (payerMode !== "all" && normalizePayerKey(c && c.payer) !== payerMode) return false;
    return true;
  }

  function refreshPayerFilterOptions(claims) {
    const sel = document.getElementById("cl-filter-payer");
    if (!sel) return;
    const prev = String(sel.value || "all");
    const counts = {};
    const labels = {};
    (claims || []).forEach(function (c) {
      const raw = String((c && c.payer) || "").trim() || "—";
      const key = normalizePayerKey(raw);
      if (!key) return;
      counts[key] = (counts[key] || 0) + 1;
      if (!labels[key]) labels[key] = raw;
    });
    const keys = Object.keys(counts).sort(function (a, b) {
      const ca = counts[b] - counts[a];
      if (ca !== 0) return ca;
      return String(labels[a] || a).localeCompare(String(labels[b] || b));
    });
    sel.textContent = "";
    const allOpt = document.createElement("option");
    allOpt.value = "all";
    allOpt.textContent = "All payers";
    sel.appendChild(allOpt);
    keys.forEach(function (key) {
      const opt = document.createElement("option");
      opt.value = key;
      opt.textContent = String(labels[key] || key) + " (" + String(counts[key]) + ")";
      sel.appendChild(opt);
    });
    if (prev !== "all" && counts[prev]) sel.value = prev;
    else sel.value = "all";
  }

  function setPayerBatchFilter(payer) {
    const sel = document.getElementById("cl-filter-payer");
    if (!sel) return;
    const key = normalizePayerKey(payer);
    if (!key || key === "all") {
      sel.value = "all";
    } else {
      let found = false;
      for (let i = 0; i < sel.options.length; i++) {
        if (sel.options[i].value === key) {
          found = true;
          break;
        }
      }
      if (!found) {
        const opt = document.createElement("option");
        opt.value = key;
        opt.textContent = String(payer || key);
        sel.appendChild(opt);
      }
      sel.value = key;
    }
    if (clClaimsCache) renderClaimsOutstanding(null);
  }

  function appendClaimActionLog(body, claim, rev) {
    const actWrap = (rev && rev.actions && typeof rev.actions === "object" ? rev.actions : {}) || {};
    const actions = Array.isArray(actWrap.actions) ? actWrap.actions : [];
    const choices = Array.isArray(actWrap.choices) && actWrap.choices.length
      ? actWrap.choices
      : Object.keys(CLAIM_ACTION_LABELS);
    const head = document.createElement("h4");
    head.className = "wk-dossier-sub";
    head.textContent = "Staff actions (local)";
    body.appendChild(head);
    if (actions.length) {
      const ul = document.createElement("ul");
      ul.className = "wk-claim-list";
      actions.slice(0, 8).forEach(function (a) {
        if (!a || typeof a !== "object") return;
        const li = document.createElement("li");
        const label = CLAIM_ACTION_LABELS[a.action] || String(a.action || "action");
        const when = String(a.at || "").replace("T", " ").slice(0, 16);
        li.textContent =
          when +
          " · " +
          label +
          (a.note ? " — " + String(a.note) : "") +
          (a.actor ? " · " + String(a.actor) : "");
        ul.appendChild(li);
      });
      body.appendChild(ul);
    } else {
      const empty = document.createElement("p");
      empty.className = "wk-dossier-muted";
      empty.textContent = "No staff actions yet · SoftDent READ-ONLY log";
      body.appendChild(empty);
    }
    const form = document.createElement("div");
    form.className = "cl-action-log";
    const sel = document.createElement("select");
    sel.setAttribute("aria-label", "Staff action type");
    choices.forEach(function (key) {
      const opt = document.createElement("option");
      opt.value = key;
      opt.textContent = CLAIM_ACTION_LABELS[key] || key;
      sel.appendChild(opt);
    });
    const note = document.createElement("input");
    note.type = "text";
    note.placeholder = "Optional note";
    note.setAttribute("aria-label", "Staff action note");
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "btn-quiet";
    btn.textContent = "Log action";
    btn.addEventListener("click", function () {
      if (!W.postJson) return;
      btn.disabled = true;
      W.postJson(
        "/api/softdent/claims-actions",
        {
          claimId: String((claim && claim.claimId) || ""),
          patientId: String((claim && claim.patientId) || ""),
          patientName: displayPatientName(claim),
          action: String(sel.value || "note"),
          note: String(note.value || "").trim(),
          actor: "Staff",
        },
        12000
      )
        .then(function (res) {
          btn.disabled = false;
          if (!res || !res.ok || !res.data || !res.data.ok) {
            btn.textContent = "Failed";
            setTimeout(function () {
              btn.textContent = "Log action";
            }, 1200);
            return;
          }
          note.value = "";
          openClaimContext(claim);
        })
        .catch(function () {
          btn.disabled = false;
          btn.textContent = "Failed";
          setTimeout(function () {
            btn.textContent = "Log action";
          }, 1200);
        });
    });
    form.appendChild(sel);
    form.appendChild(note);
    form.appendChild(btn);
    body.appendChild(form);
  }

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
      if (!isGenericPayer(claim && claim.payer)) {
        const batchBtn = document.createElement("button");
        batchBtn.type = "button";
        batchBtn.className = "btn-quiet";
        batchBtn.textContent = "Same payer batch";
        batchBtn.title = "Filter unpaid list to this payer (combine with Age for phone block)";
        batchBtn.addEventListener("click", function () {
          setPayerBatchFilter(claim.payer);
        });
        revActions.appendChild(batchBtn);
      }
      const appealBtn = document.createElement("button");
      appealBtn.type = "button";
      appealBtn.className = "btn-quiet";
      appealBtn.textContent = "Appeal packet";
      appealBtn.title = "Local denial/appeal draft — SoftDent READ-ONLY · not submitted";
      const appealBox = document.createElement("div");
      appealBox.className = "cl-appeal-box";
      appealBox.hidden = true;
      appealBtn.addEventListener("click", function () {
        if (!W.postJson) return;
        appealBtn.disabled = true;
        appealBtn.textContent = "Building…";
        const procs = Array.isArray(rev.procedures) ? rev.procedures : [];
        const procCodes = procs
          .map(function (p) {
            return String((p && p.code) || "").trim();
          })
          .filter(Boolean)
          .slice(0, 6);
        W.postJson(
          "/api/claims/appeal-packet",
          {
            claimId: String((claim && claim.claimId) || ""),
            payer: String((claim && claim.payer) || ""),
            patientId: String((claim && claim.patientId) || ""),
            patient: displayPatientName(claim),
            PatientName: displayPatientName(claim),
            status: String((claim && claim.status) || ""),
            amount: claim && claim.amount,
            procedure: procCodes.join(" ") || String((claim && claim.procedure) || ""),
            cdt: procCodes[0] || "",
            narrative: nar && nar.summary ? String(nar.summary) : "",
            denialReason: "",
          },
          20000
        )
          .then(function (res) {
            appealBtn.disabled = false;
            appealBtn.textContent = "Appeal packet";
            const data = res && res.data ? res.data : null;
            if (!res || !res.ok || !data || !data.ok) {
              appealBox.hidden = false;
              appealBox.textContent =
                "Appeal packet failed · " +
                String((data && (data.error || data.emptyMessage)) || res.status || "NO SIGNAL") +
                " · empty ≠ $0";
              return;
            }
            appealBox.hidden = false;
            appealBox.textContent = "";
            const head = document.createElement("p");
            head.className = "wk-dossier-muted";
            head.textContent =
              "Local appeal draft · not submitted · SoftDent READ-ONLY" +
              (data.consentRequiredForZip ? " · zip needs consent" : "");
            appealBox.appendChild(head);
            const pre = document.createElement("pre");
            pre.className = "cl-appeal-pre";
            pre.textContent = String(data.narrative || data.summary || "—");
            appealBox.appendChild(pre);
            const copyAppeal = document.createElement("button");
            copyAppeal.type = "button";
            copyAppeal.className = "btn-quiet";
            copyAppeal.textContent = "Copy appeal draft";
            copyAppeal.addEventListener("click", function () {
              const text = String(data.narrative || "");
              if (navigator.clipboard && navigator.clipboard.writeText) {
                navigator.clipboard.writeText(text).catch(function () {});
              }
              copyAppeal.textContent = "Copied";
              setTimeout(function () {
                copyAppeal.textContent = "Copy appeal draft";
              }, 1200);
            });
            appealBox.appendChild(copyAppeal);
          })
          .catch(function () {
            appealBtn.disabled = false;
            appealBtn.textContent = "Appeal packet";
            appealBox.hidden = false;
            appealBox.textContent = "Appeal packet fault · empty ≠ $0";
          });
      });
      revActions.appendChild(appealBtn);
      body.appendChild(revActions);
      body.appendChild(appealBox);

      appendClaimActionLog(body, claim, rev);
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
    if (data) {
      clClaimsCache = data;
      clClaimsMeta = {
        count: data.count != null ? Number(data.count) : null,
        sampleLimit: data.sampleLimit != null ? Number(data.sampleLimit) : null,
        totalOutstanding: data.totalOutstanding,
        hasData: data.hasData,
        emptyMessage: data.emptyMessage,
      };
    }
    const source = data || clClaimsCache;
    let claims = source && Array.isArray(source.claims) ? source.claims.slice() : [];
    const count =
      clClaimsMeta && clClaimsMeta.count != null ? clClaimsMeta.count : claims.length;
    const sampleLimit =
      clClaimsMeta && clClaimsMeta.sampleLimit != null
        ? clClaimsMeta.sampleLimit
        : claims.length;
    const totalRaw =
      clClaimsMeta && clClaimsMeta.totalOutstanding != null
        ? clClaimsMeta.totalOutstanding
        : source && source.totalOutstanding;
    const total = totalRaw != null ? W.money(totalRaw) : null;
    let totalBit = "total —";
    if (total != null && total !== 0) {
      const shown = W.fmtMoney ? W.fmtMoney(total) : "$" + String(total);
      if (shown) totalBit = "total " + shown;
    } else if (
      ((clClaimsMeta && clClaimsMeta.hasData) || (source && source.hasData)) &&
      (total == null || total === 0)
    ) {
      totalBit = "total empty (not zero)";
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
    if (data) refreshPayerFilterOptions(claims);
    const beforeFilter = claims.length;
    claims = claims.filter(claimPassesFilters);
    if (rangeEl) {
      rangeEl.textContent =
        String(claims.length) +
        " shown · " +
        String(Math.min(beforeFilter, sampleLimit || beforeFilter)) +
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
        (claims.length !== beforeFilter
          ? " · filter " + String(claims.length) + "/" + String(beforeFilter)
          : "") +
        " · SoftDent READ-ONLY · empty ≠ $0";
    }
    if (!claims.length) {
      const tr = document.createElement("tr");
      const td = document.createElement("td");
      td.colSpan = 6;
      td.className = "cl-empty";
      td.textContent =
        beforeFilter > 0
          ? "No unpaid SoftDent claims match this filter — empty ≠ $0."
          : (source && source.emptyMessage) ||
            "No unpaid SoftDent claims in sample — empty ≠ $0.";
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

  function patientJoinBit(data, list) {
    const sample = Array.isArray(list) ? list : [];
    if (data && data.sampleWithPatientId != null && Number.isFinite(Number(data.sampleWithPatientId))) {
      return {
        joined: Number(data.sampleWithPatientId),
        sample: sample.length,
      };
    }
    const joined = sample.filter(function (c) {
      return !!(c && c.patientId);
    }).length;
    return { joined: joined, sample: sample.length };
  }

  function snapHintText(data, count, totalBit) {
    const list = data && Array.isArray(data.claims) ? data.claims : [];
    const pj = patientJoinBit(data, list);
    let base =
      totalBit ||
      "Outstanding total · count " + count + " · SoftDent READ-ONLY · empty ≠ $0";
    if (pj.sample > 0) {
      base += " · patient join " + pj.joined + "/" + pj.sample + " in sample";
    }
    return base;
  }

  function applyClaimsJoinHonesty(data) {
    const honesty = document.getElementById("cl-honesty");
    if (!honesty || !data) return;
    const list = Array.isArray(data.claims) ? data.claims : [];
    const pj = patientJoinBit(data, list);
    if (pj.sample > 0) {
      honesty.textContent =
        "Honesty: empty ≠ $0 · patient join " +
        pj.joined +
        "/" +
        pj.sample +
        " in sample · no SoftDent write-back · staff shows full names";
    }
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
    applyClaimsJoinHonesty(res.data);
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
    ["cl-filter-age", "cl-filter-gap", "cl-filter-payer"].forEach(function (id) {
      const el = document.getElementById(id);
      if (el && !el._nr2ClBound) {
        el._nr2ClBound = true;
        el.addEventListener("change", function () {
          if (clClaimsCache) renderClaimsOutstanding(null);
        });
      }
    });
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

    const [claimsRes, aging, adj, eraInbox, ready] = await Promise.all([
      loadClaimsOutstanding(),
      W.getJson("/api/claims/aging-summary", 12000),
      W.getJson("/api/softdent/adjustment-log", 12000),
      W.getJson("/api/apex/hal/era-inbox/status", 12000),
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
          sh.textContent = snapHintText(
            claims.data,
            count,
            "Outstanding total empty · count " + count + " · SoftDent READ-ONLY · empty ≠ $0"
          );
        }
      } else {
        const shown = W.fmtMoney(total);
        if (shown) {
          W.setText("val-snap", shown + " · " + count);
          live = true;
        } else {
          W.setText("val-snap", null, "∅");
        }
        const sh = document.getElementById("hint-snap");
        if (sh) sh.textContent = snapHintText(claims.data, count);
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

    let eraLive = false;
    if (eraInbox.ok && eraInbox.data && eraInbox.data.ok !== false) {
      const era = eraInbox.data;
      const count = Number(era.fileCount != null ? era.fileCount : (era.inbox && era.inbox.fileCount) || 0);
      const chip = String(era.chipLabel || (era.inbox && era.inbox.chipLabel) || "").trim();
      const ingested = era.gap && era.gap.rowCount != null ? Number(era.gap.rowCount) : null;
      if (count > 0) {
        W.setText("val-era", String(count) + " in inbox");
        eraLive = true;
      } else if (ingested != null && ingested > 0) {
        W.setText("val-era", String(ingested) + " ingested");
        eraLive = true;
      } else {
        W.setText("val-era", null, "∅");
      }
      const eraHint = document.getElementById("hint-era");
      if (eraHint) {
        eraHint.textContent =
          (chip || "ERA inbox") +
          " · read-only · empty ≠ $0 · no SoftDent write-back";
      }
    } else if (
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
          "ERA inbox NO SIGNAL · SoftDent adjustment-log" +
          (tip && tip.date ? " · " + tip.date : "") +
          " · read-only";
      }
      live = true;
    } else {
      W.setText("val-era", null, "NO SIGNAL");
      const eraHint = document.getElementById("hint-era");
      if (eraHint) {
        eraHint.textContent = "ERA inbox unavailable · no SoftDent write-back";
      }
    }
    if (eraLive) live = true;

    W.setBanner(
      claimsStale ? "partial" : live ? "live" : "partial",
      claimsStale
        ? "Claims STALE · lasers red on softdent · list + dossier · empty ≠ $0"
        : "Claims list LIVE · click row for context · ERA inbox read-only · empty ≠ $0"
    );
    applyClaimsJoinHonesty(claims.ok ? claims.data : null);
  }

  boot().catch(function (err) {
    W.setBanner(
      "partial",
      "Claims wire fault · " + String(err && err.message ? err.message : err)
    );
  });
})();
