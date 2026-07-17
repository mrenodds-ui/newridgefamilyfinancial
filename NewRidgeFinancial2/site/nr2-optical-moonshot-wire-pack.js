/* === Moonshot Canonical Wire Pack 2026-07-17 (source-of-truth excerpt) ===
 * Applied inside nr2-optical-page-wire.js (bootExecTabs / bootPackage1StickyStack / bootOpsGates).
 * Live SoftDent-safe mounts (mountOpsGates, bootExecutiveChrome, …) are preserved —
 * Moonshot's stub placeholders are NOT used because real implementations exist.
 * Load: do not include this file separately (would double-bind tabs).
 */
(function (global) {
  "use strict";
  function bootExecTabs() {
    const frame = document.querySelector("main.main > .chrome-frame");
    const tabs = frame && frame.querySelector(":scope > .exec-tabs");
    if (!tabs) return null;
    const main = document.querySelector("main.main");
    const panels = main
      ? Array.prototype.slice.call(main.querySelectorAll(":scope > .tab-panel"))
      : [];
    if (!panels.length) return null;
    function activate(id) {
      const tabBtns = tabs.querySelectorAll('[role="tab"]');
      tabBtns.forEach(function (btn) {
        const on = btn.getAttribute("data-tab") === id;
        btn.setAttribute("aria-selected", on ? "true" : "false");
        btn.tabIndex = on ? 0 : -1;
      });
      panels.forEach(function (p) {
        const on = p.getAttribute("data-tab-panel") === id;
        if (on) p.removeAttribute("hidden");
        else p.setAttribute("hidden", "");
      });
      try {
        main.scrollTop = 0;
      } catch (_) {
        /* ignore */
      }
    }
    tabs.addEventListener("click", function (e) {
      const btn = e.target && e.target.closest ? e.target.closest('[role="tab"]') : null;
      if (!btn || !tabs.contains(btn)) return;
      const id = btn.getAttribute("data-tab");
      if (id) activate(id);
    });
    tabs.addEventListener("keydown", function (e) {
      const keys = { ArrowLeft: -1, ArrowRight: 1, Home: "home", End: "end" };
      const move = keys[e.key];
      if (move == null) return;
      const list = Array.prototype.slice.call(tabs.querySelectorAll('[role="tab"]'));
      if (!list.length) return;
      let i = list.findIndex(function (b) {
        return b.getAttribute("aria-selected") === "true";
      });
      if (i < 0) i = 0;
      if (move === "home") i = 0;
      else if (move === "end") i = list.length - 1;
      else i = (i + move + list.length) % list.length;
      e.preventDefault();
      list[i].focus();
      activate(list[i].getAttribute("data-tab"));
    });
    activate("summary");
    return true;
  }
  function bootPackage1StickyStack() {
    const main = document.querySelector("main.main");
    const ledge =
      main &&
      (main.querySelector(":scope > .chrome-frame > .ledge") ||
        main.querySelector(":scope > .ledge"));
    if (!main || !ledge) return null;
    const halHdr = main.querySelector(":scope > .hal-cmd-header");
    const apply = function () {
      const h = Math.ceil(ledge.getBoundingClientRect().height);
      const hh = halHdr ? Math.ceil(halHdr.getBoundingClientRect().height) : 0;
      main.style.setProperty("--nr2-ledge-sticky-h", String(h) + "px");
      main.style.setProperty("--nr2-hal-hdr-h", String(hh) + "px");
    };
    apply();
    if (typeof ResizeObserver === "function") {
      const ro = new ResizeObserver(function () {
        apply();
      });
      ro.observe(ledge);
      if (halHdr) ro.observe(halHdr);
    } else {
      window.addEventListener("resize", apply);
    }
    return true;
  }
  global.NR2MoonshotWirePack = {
    bootExecTabs: bootExecTabs,
    bootPackage1StickyStack: bootPackage1StickyStack,
  };
})(window);
