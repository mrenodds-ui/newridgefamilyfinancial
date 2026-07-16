/* Analytics / morning huddle — Jarvis-style OPS face (counts + attested beams) */
(function () {
  const W = window.NR2OpticalWire;
  if (!W) return;

  function currentMonthPrefix() {
    const d = new Date();
    return d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0");
  }

  function sumCollectionsMtd(data) {
    if (!data || !data.hasData || !Array.isArray(data.values)) return null;
    const labels = Array.isArray(data.labels) ? data.labels : [];
    const prefix = currentMonthPrefix();
    let sum = 0;
    let any = false;
    data.values.forEach(function (v, i) {
      const day = String(labels[i] || "");
      if (!day.startsWith(prefix)) return;
      const n = W.money(v);
      if (n != null) {
        sum += n;
        any = true;
      }
    });
    return any ? sum : null;
  }

  function morningBundleLabel(ready) {
    const bundle = ready && ready.periodClose && ready.periodClose.morningBundle;
    if (!bundle || typeof bundle !== "object") return { text: "—", tone: "NO SIGNAL", hint: "No morning bundle signal" };
    if (bundle.ok) {
      return {
        text: "OK",
        tone: "hal",
        hint:
          "Morning bundle ok" +
          (bundle.okCount != null ? " · " + bundle.okCount + " reports" : "") +
          " · empty ≠ $0",
      };
    }
    if (bundle.fallback) {
      return {
        text: "FALLBACK",
        tone: "stale",
        hint: "Attest-only fallback · run morning_bundle_attended after Excel enable",
      };
    }
    const err = bundle.error || bundle.detail || "";
    return {
      text: "FAIL",
      tone: "stale",
      hint: "Excel gate or export fault" + (err ? " · " + String(err).slice(0, 40) : ""),
    };
  }

  async function boot() {
    W.setBanner("partial", "Wiring morning huddle · empty ≠ $0");

    const [
      beamsRes,
      ready,
      smoke,
      aging,
      trellis,
      trellisProof,
      collections,
      npm,
      production,
      hygiene,
      recall,
      excelProbe,
    ] = await Promise.all([
      W.getMoneyBeams(12000),
      W.getJson("/api/import-readiness", 12000),
      W.getJson("/api/health/desk-smoke?run=0", 8000),
      W.getJson("/api/claims/aging-summary", 12000),
      W.getJson("/api/trellis/eligibility-report", 12000),
      W.getJson("/api/trellis/am-proof", 12000),
      W.getJson("/api/softdent/collections-daily", 12000),
      W.getJson("/api/softdent/new-patients-mtd", 12000),
      W.getJson("/api/softdent/provider-production", 12000),
      W.getJson("/api/softdent/hygiene-recall", 12000),
      W.getJson("/api/nr2/financial-recall", 12000),
      W.getJson("/api/softdent/excel-probe", 12000),
    ]);

    const readyData = ready.ok ? ready.data : null;
    const beams = beamsRes.ok ? beamsRes.data : null;
    let live = false;

    W.applyBeamHeadline({
      id: "an-sd",
      hintId: "hint-an-sd",
      beams: beams,
      ready: readyData,
      side: "softdent",
    });
    W.applyBeamHeadline({
      id: "an-qb",
      hintId: "hint-an-qb",
      beams: beams,
      ready: readyData,
      side: "quickbooks",
    });
    if (beams && beams.ok) live = true;

    const pc = (readyData && readyData.periodClose) || {};
    const closeStatus = String(
      pc.status ||
        (readyData &&
          readyData.operationContext &&
          readyData.operationContext.periodCloseStatus) ||
        "—"
    ).toUpperCase();
    W.setText("an-close", closeStatus, closeStatus === "COMPLETED" ? "hal" : "stale");
    const hintClose = document.getElementById("hint-an-close");
    if (hintClose) {
      const mb = morningBundleLabel(readyData);
      hintClose.textContent =
        "Shadow SOR=false · completedAt " +
        String(pc.completedAt || pc.lastCloseAt || "—") +
        " · bundle " +
        mb.text;
    }

    if (smoke.ok && smoke.data) {
      const st = String(smoke.data.status || "—");
      const proof = String(smoke.data.deskProof || "");
      W.setText("an-smoke", st + (proof ? " · " + proof : ""), st === "GREEN" ? "hal" : "stale");
      const hintSmoke = document.getElementById("hint-an-smoke");
      if (hintSmoke) {
        hintSmoke.textContent =
          proof === "MATCH"
            ? "Beam proof MATCH · patient attest eligible when MATCH"
            : "Run VERIFY BEAM or refresh_period_close_beam.py if drift";
      }
      if (st === "GREEN") live = true;
    } else {
      W.setText("an-smoke", null, "NO SIGNAL");
    }

    if (aging.ok && aging.data && aging.data.hasData) {
      const over30 = aging.data.over30 != null ? aging.data.over30 : "—";
      const total = aging.data.count != null ? aging.data.count : "—";
      W.setText("an-aging", String(over30) + " / " + String(total));
      const hintAging = document.getElementById("hint-an-aging");
      if (hintAging) {
        hintAging.textContent =
          "Over 30 / total claims in summary · empty ≠ $0 on dollar tiles only";
      }
      live = true;
    } else {
      W.setText("an-aging", null, "∅");
    }

    if (trellis.ok && trellis.data) {
      const tr = trellis.data;
      const patients = tr.patients != null ? tr.patients : "—";
      const wb = tr.withBenefits != null ? tr.withBenefits : "—";
      const statusOnly = tr.statusOnly != null ? tr.statusOnly : "—";
      W.setText("an-trellis", String(wb) + " / " + String(patients));
      W.setText("an-trellis-date", tr.targetDate || tr.date || "—");
      const summary = document.getElementById("an-trellis-summary");
      if (summary) {
        summary.textContent =
          "Patients " +
          patients +
          " · withBenefits " +
          wb +
          " · statusOnly " +
          statusOnly +
          " · empty ≠ $0";
      }
      const link = document.getElementById("an-trellis-link");
      if (link && tr.reportUrl) link.href = tr.reportUrl;
      if (trellisProof.ok && trellisProof.data) {
        const proof = trellisProof.data;
        const proofEl = document.getElementById("an-trellis-proof");
        if (proofEl) {
          const chip = String(proof.chipLabel || proof.chipStatus || "—");
          proofEl.textContent =
            "AM proof · " +
            chip +
            (proof.passed ? " · PASS" : " · pending scrape") +
            " · counts only · empty ≠ $0";
        }
        if (proof.passed) live = true;
      }
      live = true;
    } else {
      W.setText("an-trellis", null, "NO SIGNAL");
      W.setText("an-trellis-date", "—");
      const summary = document.getElementById("an-trellis-summary");
      if (summary) summary.textContent = "No Trellis report for target date yet";
      if (trellisProof.ok && trellisProof.data) {
        const proof = trellisProof.data;
        const proofEl = document.getElementById("an-trellis-proof");
        if (proofEl) {
          proofEl.textContent =
            "AM proof · " +
            String(proof.chipLabel || proof.chipStatus || "—") +
            (proof.passed ? " · PASS" : " · pending scrape") +
            " · counts only · empty ≠ $0";
        }
      }
    }

    if (collections.ok && collections.data) {
      const mtd = sumCollectionsMtd(collections.data);
      const shown = W.fmtMoney(mtd);
      if (shown) {
        W.setText("an-coll", shown);
        live = true;
      } else {
        W.setText("an-coll", null, "∅");
      }
      const hintColl = document.getElementById("hint-an-coll");
      if (hintColl) {
        hintColl.textContent =
          "MTD " +
          currentMonthPrefix() +
          " · source " +
          String(collections.data.source || "sd_payments") +
          " · empty ≠ $0";
      }
    } else {
      W.setText("an-coll", null, "NO SIGNAL");
    }

    if (npm.ok && npm.data && npm.data.hasData) {
      const n = npm.data.count != null ? Number(npm.data.count) : null;
      W.setText("an-npm", n != null ? String(n) : "—");
      const hintNpm = document.getElementById("hint-an-npm");
      if (hintNpm) {
        hintNpm.textContent =
          "Period " +
          String(npm.data.period || currentMonthPrefix()) +
          " · " +
          String(npm.data.source || "sd_patients");
      }
      live = true;
    } else {
      W.setText("an-npm", null, "∅");
    }

    if (production.ok && production.data && production.data.hasData) {
      const shown = W.fmtMoney(W.money(production.data.total));
      if (shown) {
        W.setText("an-prod", shown);
        live = true;
      } else {
        W.setText("an-prod", null, "∅");
      }
      const providers = Array.isArray(production.data.providers)
        ? production.data.providers.slice(0, 3)
        : [];
      const hintProd = document.getElementById("hint-an-prod");
      if (hintProd) {
        hintProd.textContent = providers.length
          ? providers
              .map(function (p) {
                return (
                  String(p.providerCode || "?") +
                  " " +
                  (W.fmtMoney(W.money(p.production)) || "∅")
                );
              })
              .join(" · ")
          : String(production.data.source || "sd_procedures");
      }
    } else {
      W.setText("an-prod", null, "NO SIGNAL");
    }

    const bundle = morningBundleLabel(readyData);
    W.setText("an-bundle", bundle.text, bundle.tone === "hal" ? "hal" : bundle.tone === "stale" ? "stale" : null);
    const hintBundle = document.getElementById("hint-an-bundle");
    if (hintBundle) hintBundle.textContent = bundle.hint;
    if (bundle.tone === "hal") live = true;

    const excelSummary = document.getElementById("an-excel-summary");
    if (excelProbe.ok && excelProbe.data) {
      const ep = excelProbe.data;
      if (ep.hasProbe) {
        const avail = ep.excelAvailable === true;
        if (excelSummary) {
          excelSummary.textContent =
            (avail ? "Excel available" : "Excel blocked") +
            " · probe " +
            String(ep.at || ep.fileMtime || "—") +
            " · empty ≠ $0";
        }
        if (avail) live = true;
      } else if (excelSummary) {
        excelSummary.textContent =
          "No probe on record — run scripts/probe_softdent_excel_output_options.py · empty ≠ $0";
      }
    } else if (excelSummary) {
      excelSummary.textContent = "Excel probe NO SIGNAL";
    }

    if (hygiene.ok && hygiene.data) {
      const hr = hygiene.data;
      if (hr.hasData) {
        const due = hr.recallDue != null ? Number(hr.recallDue) : null;
        const done = hr.hygieneCompleted != null ? Number(hr.hygieneCompleted) : null;
        const overdue = hr.overdue != null ? Number(hr.overdue) : null;
        if (due != null && done != null) {
          W.setText("an-hygiene", String(overdue != null ? overdue : due) + " gap");
        } else if (due != null) {
          W.setText("an-hygiene", String(due) + " due");
        } else {
          W.setText("an-hygiene", null, "∅");
        }
        const hintHy = document.getElementById("hint-an-hygiene");
        if (hintHy) {
          hintHy.textContent =
            "Period " +
            String(hr.period || currentMonthPrefix()) +
            " · due " +
            String(due != null ? due : "—") +
            " · completed " +
            String(done != null ? done : "—") +
            " · counts only · empty ≠ $0";
        }
        live = true;
      } else {
        W.setText("an-hygiene", null, "∅");
        const hintHy = document.getElementById("hint-an-hygiene");
        if (hintHy) hintHy.textContent = "No hygiene recall export yet · empty ≠ $0";
      }
    } else {
      W.setText("an-hygiene", null, "NO SIGNAL");
    }

    const recallSummary = document.getElementById("an-recall-summary");
    if (recall.ok && recall.data && recall.data.ok) {
      const count = Number(recall.data.count || 0);
      if (recallSummary) {
        recallSummary.textContent =
          count > 0
            ? "Recall candidates " +
              String(count) +
              " · min $" +
              String((recall.data.config && recall.data.config.minBalance) || "—") +
              " · " +
              String((recall.data.config && recall.data.config.minMonthsSinceVisit) || "—") +
              " mo since visit · board-safe"
            : "No recall rows match filters yet · empty ≠ $0";
      }
      if (count > 0) live = true;
    } else if (recallSummary) {
      recallSummary.textContent = "Financial recall NO SIGNAL · check sd_claims + sd_patients";
    }

    W.setBanner(
      live ? "live" : "partial",
      live
        ? "Morning huddle LIVE · beams + MTD + counts · empty ≠ $0"
        : "Morning huddle partial · check import readiness"
    );
  }

  boot().catch(function (err) {
    W.setBanner(
      "partial",
      "Analytics wire fault · " + String(err && err.message ? err.message : err)
    );
  });
})();
