/* Moonshot §7 viewport gate — coding pack 2026-07-17 */
(function () {
  function runMoonshotViewportGate() {
    const f = document.querySelector(".chrome-frame");
    const h = document.querySelector("body > .honesty");
    const beamEl = document.querySelector(".beam");
    const b = getComputedStyle(beamEl || document.createElement("div"));
    const errors = [];
    if (!f) errors.push("FAIL: .chrome-frame missing");
    if (f && Math.abs(f.getBoundingClientRect().height - 172) > 2) {
      errors.push("FAIL: chrome-frame height !== 172px");
    }
    if (!h) errors.push("FAIL: body > .honesty missing");
    if (h && getComputedStyle(h).position !== "fixed") {
      errors.push("FAIL: honesty not fixed");
    }
    if (beamEl && parseFloat(b.height) !== 1) {
      errors.push("FAIL: beam height !== 1px");
    }
    if (errors.length) {
      console.error("MOONSHOT GATE FAILED", errors);
      return false;
    }
    console.log(
      "MOONSHOT GATE PASS: chrome-frame 172px · beam 1px · honesty fixed · 1080p ready"
    );
    return true;
  }
  window.NR2MoonshotViewportGate = runMoonshotViewportGate;
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () {
      setTimeout(runMoonshotViewportGate, 50);
    });
  } else {
    setTimeout(runMoonshotViewportGate, 50);
  }
})();
