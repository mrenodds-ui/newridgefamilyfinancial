"""Run Package 1 §8 1440p deskPass gate via headless Chromium."""
from __future__ import annotations

import json
import ssl
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "NewRidgeFinancial2" / "docs" / "_p1_gate_runs" / "p1_browser_1440_full.json"
BASE = "https://127.0.0.1:8765"
PAGES = [
    "nr2-optical-page-ar.html",
    "nr2-optical-page-softdent.html",
    "nr2-optical-page-claims.html",
    "nr2-optical-page-hal.html",
    "nr2-optical-page-office-manager.html",
    "nr2-optical-page-analytics.html",
    "nr2-optical-page-quickbooks.html",
    "nr2-optical-page-taxes.html",
    "nr2-optical-page-content.html",
    "nr2-optical-page-narratives.html",
]

MEASURE = """(() => {
  const main = document.querySelector('main.main');
  const ledge = main.querySelector(':scope > .ledge');
  const compact = main.querySelector(':scope > .exec-compact-header');
  const beam = main.querySelector(':scope > .beam');
  let el = beam ? beam.nextElementSibling : null;
  while (el && (el.id === 'nr2-crumb' || /excel-probe|nr2-crumb/.test(String(el.className||'')))) el = el.nextElementSibling;
  const fully = (x) => { const b = x.getBoundingClientRect(); return b.top >= 0 && b.bottom <= innerHeight; };
  const topOk = (x) => { const b = x.getBoundingClientRect(); return b.top >= 0 && b.top < innerHeight; };
  return {
    path: location.pathname,
    viewport: {w: innerWidth, h: innerHeight},
    ledgeFully: fully(ledge),
    compactFully: fully(compact),
    firstBelow: el ? String(el.className||el.id||el.tagName).split(' ')[0] : null,
    firstTopOk: el ? topOk(el) : false,
    deskPass: fully(ledge) && fully(compact) && el && topOk(el)
  };
})()"""


def main() -> int:
    results: list[dict] = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 2560, "height": 1440},
            ignore_https_errors=True,
        )
        page = context.new_page()
        for name in PAGES:
            url = f"{BASE}/{name}"
            page.goto(url, wait_until="networkidle", timeout=30000)
            page.wait_for_timeout(500)
            row = page.evaluate(MEASURE)
            results.append(row)
        browser.close()

    payload = {
        "viewport": "2560x1440",
        "pages": results,
        "allPass": all(r.get("deskPass") for r in results),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0 if payload["allPass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
