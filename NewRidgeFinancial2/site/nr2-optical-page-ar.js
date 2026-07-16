/* A/R optical bench — SoftDent AR buckets + live money-beams headline */
(function () {
  const W = window.NR2OpticalWire;
  if (!W) return;
  const Nav = window.NR2OpticalNav;
  const AR_NS = "ar";
  let arBucketsCache = null;

  function bucketNorm(label) {
    const s = String(label || "")
      .toLowerCase()
      .replace(/\s+/g, "");
    if (!s) return "";
    if (s.indexOf("90") >= 0 && (s.indexOf("+") >= 0 || s.indexOf("over") >= 0 || s.indexOf(">") >= 0)) {
      return "90+";
    }
    if (/0[-–]?30|≦?30|<=?30/.test(s) || s === "current" || s.indexOf("0-30") >= 0) return "0-30";
    if (/31[-–]?60|30[-–]?60/.test(s)) return "31-60";
    if (/61[-–]?90|60[-–]?90/.test(s)) return "61-90";
    if (s.indexOf("90") >= 0) return "90+";
    return s;
  }

  function currentBucketFilter() {
    const sel = document.getElementById("ar-filter-bucket");
    return sel ? String(sel.value || "all") : "all";
  }

  function restoreArFilterEarly() {
    const sel = document.getElementById("ar-filter-bucket");
    if (!sel || !Nav || !Nav.restoreBeamState) return "all";
    const st = Nav.restoreBeamState(AR_NS);
    if (st && st.bucket) {
      const v = String(st.bucket);
      if ([].some.call(sel.options, function (o) {
        return o.value === v;
      })) {
        sel.value = v;
      }
    }
    return currentBucketFilter();
  }

  function persistArFilter() {
    if (!Nav || !Nav.persistBeamState) return;
    Nav.persistBeamState(AR_NS, { bucket: currentBucketFilter() });
  }

  function bucketLine(buckets, filterKey) {
    if (!Array.isArray(buckets) || !buckets.length) return null;
    const key = filterKey || "all";
    const list =
      key === "all"
        ? buckets
        : buckets.filter(function (b) {
            return bucketNorm(b && b.bucket) === key;
          });
    if (!list.length) return null;
    return list
      .map(function (b) {
        const v = W.money(b.amount != null ? b.amount : b.balance);
        let amt = "—";
        if (v == null) amt = "—";
        else if (v === 0) amt = "Empty";
        else amt = W.fmtMoney(v) || "—";
        return String(b.bucket || "?") + " " + amt;
      })
      .join(" · ");
  }

  function paintBuckets(buckets) {
    const key = currentBucketFilter();
    const line = bucketLine(buckets, key);
    const summary = document.getElementById("ar-bucket-summary");
    if (line) {
      W.setText("val-buckets", line, "∅");
      if (summary) {
        summary.textContent =
          key === "all"
            ? "SoftDent AR buckets · all · empty ≠ $0"
            : "SoftDent AR · filter " + key + " · empty ≠ $0";
      }
    } else {
      W.setText("val-buckets", null, key === "all" ? "∅" : "no match");
      if (summary) {
        summary.textContent =
          key === "all"
            ? "No SoftDent AR bucket signal · empty ≠ $0"
            : "No SoftDent AR rows for " + key + " · empty ≠ $0";
      }
    }
  }

  function wireArFilter() {
    const sel = document.getElementById("ar-filter-bucket");
    if (!sel || sel._nr2ArBound) return;
    sel._nr2ArBound = true;
    sel.addEventListener("change", function () {
      persistArFilter();
      if (arBucketsCache) paintBuckets(arBucketsCache);
    });
  }

  async function boot() {
    // Restore filter before paint — no flash of unfiltered buckets.
    restoreArFilterEarly();
    wireArFilter();
    W.markFacesLoading(["val-total", "val-buckets", "val-collect", "val-status"]);
    W.setBanner("partial", "Wiring SoftDent AR + money-beams · empty ≠ $0 · no invent $");
    if (W.bindPrintHygiene) {
      W.bindPrintHygiene({
        breakSelector: ".phi-sample-list li",
        breakEvery: 3,
      });
    }

    const aging = await W.getJson("/api/softdent/ar-aging", 12000);
    const claims = await W.getJson("/api/softdent/claims-outstanding", 12000);
    const ready = await W.getJson("/api/import-readiness", 12000);
    const beamsRes = await W.getMoneyBeams(12000);
    if (W.applyExcelProbeHint) {
      W.applyExcelProbeHint("hint-total", 8000).catch(function () {});
    }

    let live = false;
    let stale = false;
    const readyData = ready.ok ? ready.data : null;
    const beams = beamsRes.ok ? beamsRes.data : null;

    if (readyData) {
      const keys = W.laserKeys(readyData);
      const arHit = W.keysHit(keys, ["softdent.ar"]);
      stale = arHit || W.lasersRed(readyData);
      W.setText("val-status", arHit || W.lasersRed(readyData) ? "STALE · lasers" : "READY");
    } else {
      W.setText("val-status", null, "NO SIGNAL");
    }

    const beamHit = W.applyBeamHeadline({
      id: "val-total",
      hintId: "hint-total",
      beams: beams,
      ready: readyData,
      side: "softdent",
    });
    if (beamHit.applied && beamHit.live) {
      live = true;
    } else if (!beamHit.applied) {
      if (aging.ok && aging.data && aging.data.hasData) {
        const hit = W.setMoneyText
          ? W.setMoneyText("val-total", aging.data.total, { emptyLabel: "∅" })
          : null;
        if (hit && hit.live) live = true;
        else if (!W.setMoneyText) {
          const shown = W.fmtMoney(aging.data.total);
          if (shown) {
            W.setText("val-total", shown);
            live = true;
          } else {
            W.setText("val-total", null, "∅");
          }
        }
        if (aging.data.stale) stale = true;
      } else if (claims.ok && claims.data && claims.data.hasData) {
        const list = Array.isArray(claims.data.claims) ? claims.data.claims : [];
        const total =
          W.money(claims.data.totalOutstanding) != null
            ? W.money(claims.data.totalOutstanding)
            : list.reduce(function (s, c) {
                return s + (W.money(c.amount) || 0);
              }, 0);
        const hit = W.setMoneyText
          ? W.setMoneyText("val-total", total, { emptyLabel: "∅" })
          : null;
        if (hit && hit.live) live = true;
        else if (!W.setMoneyText) {
          const shown = W.fmtMoney(total);
          W.setText("val-total", shown, shown ? null : "∅");
          if (shown) live = true;
        }
        const totalHint = document.getElementById("hint-total");
        if (totalHint) totalHint.textContent = "claims proxy · money-beams UNAVAILABLE";
      } else {
        W.setText("val-total", null, stale ? "STALE / ∅" : "NO SIGNAL");
      }
    }

    if (aging.ok && aging.data && aging.data.hasData) {
      arBucketsCache = Array.isArray(aging.data.buckets) ? aging.data.buckets : [];
      paintBuckets(arBucketsCache);
      if (aging.data.stale) stale = true;
      const ageHint = document.getElementById("hint-buckets");
      if (ageHint) {
        ageHint.textContent =
          "SoftDent AR buckets" +
          (aging.data.ageHours != null ? " · age " + aging.data.ageHours + "h" : "") +
          " · empty ≠ $0";
      }
    } else {
      arBucketsCache = [];
      W.setText("val-buckets", null, aging.ok ? "∅" : "NO SIGNAL");
    }

    if (claims.ok && claims.data && claims.data.hasData) {
      const list = Array.isArray(claims.data.claims) ? claims.data.claims : [];
      W.setText("val-collect", String(list.length) + " open claims");
      if (W.fillPhiSampleList) {
        W.fillPhiSampleList(document.getElementById("phi-sample"), list, 6);
      }
    } else {
      W.setText("val-collect", null, "∅");
      if (W.fillPhiSampleList) {
        W.fillPhiSampleList(document.getElementById("phi-sample"), [], 6);
      }
    }

    const provenance = W.beamProvenanceLine(beams, readyData);
    if (stale || (beams && beams.importStale) || W.lasersRed(readyData)) {
      const el = document.getElementById("val-total");
      if (el) el.classList.add("stale");
      W.setBanner(
        "partial",
        "SoftDent lasers STALE · " + provenance + " · empty ≠ $0 · no SoftDent write-back"
      );
    } else {
      W.setBanner(
        W.bannerModeFromReady(readyData, live),
        "SoftDent A/R · money-beams · " + provenance + " · empty ≠ $0"
      );
    }

    if (Nav && Nav.bindBeamBusScroll) Nav.bindBeamBusScroll(AR_NS);
    if (Nav && Nav.restoreScroll) Nav.restoreScroll(AR_NS);
  }

  boot();
})();
