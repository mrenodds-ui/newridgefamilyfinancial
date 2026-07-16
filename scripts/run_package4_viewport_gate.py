"""Static schema gate for Moonshot Package 4 Tabbed Content Deck."""
from __future__ import annotations

import json
import re
import ssl
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "NewRidgeFinancial2" / "site"
OUT = ROOT / "NewRidgeFinancial2" / "docs" / "_p4_gate_runs"
PAGES = sorted(p.name for p in SITE.glob("nr2-optical-page-*.html"))


def schema(page: Path) -> dict:
    t = page.read_text(encoding="utf-8")
    m = re.search(
        r'<div class="chrome-frame">(.*?)</div>\s*\n\s*<div class="tab-panel"',
        t,
        re.S,
    )
    frame = m.group(1) if m else ""
    ledge_idx = frame.find('class="ledge"')
    tabs_idx = frame.find('class="exec-tabs"')
    return {
        "page": page.name,
        "has_exec_tabs": 'class="exec-tabs"' in t,
        "has_summary_tab": 'data-tab="summary"' in t,
        "tabs_in_frame_after_ledge": bool(m) and 0 <= ledge_idx < tabs_idx,
        "summary_not_hidden": not bool(
            re.search(r'data-tab-panel="summary"[^>]*\bhidden\b', t)
        ),
        "has_tab_panel": 'class="tab-panel"' in t,
    }


def theme_ok(css: str) -> dict:
    return {
        "chrome_h_172": "--nr2-chrome-frame-h: 172px" in css,
        "exec_tabs_rule": ".chrome-frame > .exec-tabs" in css,
        "tab_panel_hidden": ".main > .tab-panel[hidden]" in css,
        "main_uses_chrome_var": "var(--nr2-chrome-frame-h)" in css,
    }


def wire_ok(js: str) -> dict:
    return {
        "bootExecTabs_fn": "function bootExecTabs" in js,
        "bootExecTabs_call": "bootExecTabs()" in js,
        "default_summary": 'activate("summary")' in js,
    }


def http_ok(base: str, path: str) -> dict:
    url = base.rstrip("/") + "/" + path.lstrip("/")
    ctx = ssl._create_unverified_context()
    req = urllib.request.Request(url, headers={"User-Agent": "nr2-p4-gate/1.0"})
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
    schemas = [schema(SITE / n) for n in PAGES]
    schema_fail = [
        s["page"]
        for s in schemas
        if not (
            s["has_exec_tabs"]
            and s["has_summary_tab"]
            and s["tabs_in_frame_after_ledge"]
            and s["summary_not_hidden"]
            and s["has_tab_panel"]
        )
    ]
    theme = theme_ok((SITE / "nr2-optical-theme.css").read_text(encoding="utf-8"))
    wire = wire_ok((SITE / "nr2-optical-page-wire.js").read_text(encoding="utf-8"))
    theme_fail = [k for k, v in theme.items() if not v]
    wire_fail = [k for k, v in wire.items() if not v]
    http = [http_ok(args.base, n) for n in ("nr2-optical-page-claims.html",)]
    http_fail = [h["url"] for h in http if not h["ok"]]
    report = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "moonshot_package": 4,
        "schema": schemas,
        "schema_fail": schema_fail,
        "theme": theme,
        "theme_fail": theme_fail,
        "wire": wire,
        "wire_fail": wire_fail,
        "http": http,
        "http_fail": http_fail,
        "pass_static": not schema_fail and not theme_fail and not wire_fail,
        "gate": [
            "exec-tabs immediately after .ledge inside chrome-frame",
            "default Summary tab visible; heavy panels hidden",
            "chrome-frame height 172px (desk + tabs)",
            "1080p: money-strip + tab bar without scroll (manual/CDP)",
        ],
    }
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = OUT / f"p4_gate_{stamp}.json"
    latest = OUT / "p4_gate_latest.json"
    text = json.dumps(report, indent=2)
    out.write_text(text, encoding="utf-8")
    latest.write_text(text, encoding="utf-8")
    print(
        json.dumps(
            {
                "out": str(out),
                "pass_static": report["pass_static"],
                "schema_fail": schema_fail,
                "theme_fail": theme_fail,
                "wire_fail": wire_fail,
                "http_fail": http_fail,
            },
            indent=2,
        )
    )
    return 0 if report["pass_static"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
