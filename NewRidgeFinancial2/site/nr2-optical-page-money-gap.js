/* Metric gap honesty — SoftDent AR outstanding vs QB monthly revenue (optical only) */
(function () {
  const W = window.NR2OpticalWire;
  if (!W) return;

  async function boot() {
    W.markFacesLoading(["gap-sd", "gap-qb", "gap-delta"]);
    let readyData = null;
    try {
      readyData = await W.getJson("/api/import-readiness", 8000);
    } catch (_) {
      readyData = null;
    }
    let beams = null;
    try {
      beams = await W.getMoneyBeams(12000);
    } catch (_) {
      beams = null;
    }

    if (W.applyBeamHeadline) {
      W.applyBeamHeadline({
        id: "gap-sd",
        hintId: "hint-gap-sd",
        beams: beams,
        ready: readyData,
        side: "softdent",
      });
      W.applyBeamHeadline({
        id: "gap-qb",
        hintId: "hint-gap-qb",
        beams: beams,
        ready: readyData,
        side: "quickbooks",
      });
    }

    if (W.paintMetricGapHonesty) {
      W.paintMetricGapHonesty({
        id: "gap-delta",
        hintId: "hint-gap-delta",
        beams: beams,
        ready: readyData,
      });
    }

    const gap = beams && beams.metricGapHonesty;
    const chip = document.getElementById("gap-honesty-chip");
    if (chip) {
      chip.textContent =
        (gap && gap.label) || "Different Metrics — Not Auto-Reconciled";
    }
    const note = document.getElementById("gap-summary-note");
    if (note) {
      const sd = (gap && gap.softdentDisplay) || "∅";
      const qb = (gap && gap.quickbooksDisplay) || "∅";
      const raw = (gap && gap.rawDeltaDisplay) || "∅";
      note.textContent =
        "SoftDent AR outstanding " +
        sd +
        " vs QB monthly revenue " +
        qb +
        " · raw |Δ| " +
        raw +
        " · Different Metrics — Not Auto-Reconciled · empty ≠ $0 · ERA inbox awaiting real 835 files · no Reconcile CTA";
    }

    const bind = document.querySelector(".bind");
    if (bind && W.beamProvenanceLine) {
      bind.textContent = W.beamProvenanceLine(beams, readyData) + " · empty ≠ $0";
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
