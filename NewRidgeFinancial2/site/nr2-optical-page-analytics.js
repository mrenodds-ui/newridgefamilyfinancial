/* Analytics / morning huddle — Jarvis-style OPS face (counts + attested beams) */
(function () {
  const W = window.NR2OpticalWire;
  if (!W) return;

  async function boot() {
    W.setBanner("partial", "Wiring morning huddle · empty ≠ $0");

    const [beamsRes, ready, smoke, aging, trellis] = await Promise.all([
      W.getMoneyBeams(12000),
      W.getJson("/api/import-readiness", 12000),
      W.getJson("/api/health/desk-smoke?run=0", 8000),
      W.getJson("/api/claims/aging-summary", 12000),
      W.getJson("/api/trellis/eligibility-report", 12000),
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
    const closeStatus = String(pc.status || (readyData && readyData.operationContext && readyData.operationContext.periodCloseStatus) || "—").toUpperCase();
    W.setText("an-close", closeStatus, closeStatus === "COMPLETED" ? "hal" : "stale");
    const hintClose = document.getElementById("hint-an-close");
    if (hintClose) {
      hintClose.textContent =
        "Shadow SOR=false · completedAt " + String(pc.completedAt || pc.lastCloseAt || "—");
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
      live = true;
    } else {
      W.setText("an-trellis", null, "NO SIGNAL");
      W.setText("an-trellis-date", "—");
      const summary = document.getElementById("an-trellis-summary");
      if (summary) summary.textContent = "No Trellis report for target date yet";
    }

    W.setBanner(
      live ? "live" : "partial",
      live
        ? "Morning huddle LIVE · beams + counts · empty ≠ $0"
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
