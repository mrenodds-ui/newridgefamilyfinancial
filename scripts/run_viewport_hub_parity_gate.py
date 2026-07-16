"""Static + optional HTTP gate for Hub viewport parity (Track A after P4)."""
from __future__ import annotations

import json
import re
import ssl
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "NewRidgeFinancial2" / "site"
OUT = ROOT / "NewRidgeFinancial2" / "docs" / "_viewport_hub_gate_runs"


def hub_schema() -> dict:
    t = (SITE / "nr2-optical-pages-hub.html").read_text(encoding="utf-8")
    m = re.search(
        r'<div class="chrome-frame">(.*?)</div>\s*\n\s*<div class="tab-panel"',
        t,
        re.S,
    )
    frame = m.group(1) if m else ""
    after_main = t.split("</main>", 1)[1] if "</main>" in t else ""
    return {
        "chrome_frame": 'class="chrome-frame"' in t,
        "letterhead": 'id="nr2-page-letterhead"' in t,
        "tabs_after_ledge": bool(m)
        and frame.find('class="ledge"') < frame.find('class="exec-tabs"'),
        "summary_default": 'data-tab="summary"' in t
        and not bool(re.search(r'data-tab-panel="summary"[^>]*\bhidden\b', t)),
        "bench_hidden": bool(
            re.search(r'data-tab-panel="bench"[^>]*\bhidden\b', t)
        ),
        "honesty_body_led": 'class="honesty"' in after_main,
        "no_old_h1_stack": '<h1 class="type-staff">' not in t,
        "ids_ok": all(
            x in t
            for x in (
                "hub-aligned",
                "hub-variance",
                "btn-force-close",
                "hub-sd-amt",
                "face-qb",
                "hub-rail",
            )
        ),
    }


def landing_ok() -> dict:
    t = (SITE / "nr2-optical-beam-touch-mockup.html").read_text(encoding="utf-8")
    head = t[:2500]
    return {
        "overflow_hidden": "overflow: hidden" in head,
        "landing_ledge": "exec-landing-ledge" in t,
        "money_strip": "money-strip" in t,
        "no_chrome_frame_required": True,
    }


def theme_ok() -> dict:
    css = (SITE / "nr2-optical-theme.css").read_text(encoding="utf-8")
    return {
        "hub_chrome_rule": "body.page-hub .chrome-frame" in css,
        "hub_rail_max_h": "body.page-hub .hub-rail" in css,
    }


def http_ok(base: str, path: str) -> dict:
    url = base.rstrip("/") + "/" + path.lstrip("/")
    ctx = ssl._create_unverified_context()
    req = urllib.request.Request(url, headers={"User-Agent": "nr2-hub-parity/1.0"})
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=12) as r:
            return {"url": url, "status": r.status, "ok": 200 <= r.status < 300}
    except Exception as e:
        return {"url": url, "status": None, "ok": False, "error": str(e)}


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="https://127.0.0.1:8765")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    hub = hub_schema()
    land = landing_ok()
    theme = theme_ok()
    hub_fail = [k for k, v in hub.items() if not v]
    land_fail = [k for k, v in land.items() if not v]
    theme_fail = [k for k, v in theme.items() if not v]
    http = [http_ok(args.base, "nr2-optical-pages-hub.html")]
    http_fail = [h["url"] for h in http if not h["ok"]]
    report = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "track": "A_viewport_hub_parity",
        "hub": hub,
        "hub_fail": hub_fail,
        "landing": land,
        "landing_fail": land_fail,
        "theme": theme,
        "theme_fail": theme_fail,
        "http": http,
        "http_fail": http_fail,
        "pass_static": not hub_fail and not land_fail and not theme_fail,
        "gate": [
            "Hub: letterhead + chrome-frame + ledge + exec-tabs",
            "Default Summary; Bench heavy faces tabbed",
            "Honesty body LED",
            "Landing: overflow hidden + money ledge (no chrome-frame)",
        ],
    }
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = OUT / f"hub_parity_{stamp}.json"
    latest = OUT / "hub_parity_latest.json"
    text = json.dumps(report, indent=2)
    out.write_text(text, encoding="utf-8")
    latest.write_text(text, encoding="utf-8")
    print(
        json.dumps(
            {
                "out": str(out),
                "pass_static": report["pass_static"],
                "hub_fail": hub_fail,
                "landing_fail": land_fail,
                "theme_fail": theme_fail,
                "http_fail": http_fail,
            },
            indent=2,
        )
    )
    return 0 if report["pass_static"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
