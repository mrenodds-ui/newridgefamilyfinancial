"""
Moonshot Package 1 validation gate runner (effort M: thorough fold checks).

Uses the live NR2 server + optional CDP via a printed checklist JSON that
Cursor browser automation (or a human) can verify. Also performs static
schema audits that do not need a browser.

Usage:
  python scripts/run_package1_viewport_gate.py
  python scripts/run_package1_viewport_gate.py --base https://127.0.0.1:8765
"""
from __future__ import annotations

import argparse
import json
import re
import ssl
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "NewRidgeFinancial2" / "site"
OUT = ROOT / "NewRidgeFinancial2" / "docs" / "_p1_gate_runs"
PAGES = sorted(p.name for p in SITE.glob("nr2-optical-page-*.html"))


def static_schema(page: Path) -> dict:
    t = page.read_text(encoding="utf-8")
    main_m = re.search(r'<main class="main">(.*?)</main>', t, re.S)
    main = main_m.group(1) if main_m else ""
    after = main.lstrip()
    return {
        "page": page.name,
        "ledge_first": after.startswith('<div class="ledge">'),
        "has_compact": "exec-compact-header" in main,
        "honesty_not_in_main": '<div class="honesty"' not in main,
        "honesty_after_main": bool(re.search(r"</main>[\s\S]*?<div class=\"honesty\"", t)),
        "has_beam": bool(re.search(r'<div class="beam"', main)),
        "sd_tokens": len(re.findall(r'\bclass="[^"]*\bsd\b', main)),
        "qb_tokens": len(re.findall(r'\bclass="[^"]*\bqb\b', main)),
        "hal_tokens": len(re.findall(r'\bclass="[^"]*\bhal\b', main)),
    }


def theme_concrete_moves(css: str) -> dict:
    checks = {
        "main_padding_top_0": "padding-top: 0" in css
        and re.search(r"\.main\s*\{[^}]*padding-top:\s*0", css, re.S),
        "main_height_banner_honesty": "calc(100dvh - 36px - 20px)" in css,
        "compact_inline_12": (
            ".exec-compact-header .mode-eyebrow" in css
            and "display: inline" in css
            and re.search(
                r"\.exec-compact-header \.mode-eyebrow,\s*"
                r"\.exec-compact-header \.type-staff,\s*"
                r"\.exec-compact-header h1\.type-staff,\s*"
                r"\.exec-compact-header \.kicker\s*\{[^}]*font-size:\s*12px[^}]*line-height:\s*1[^}]*margin:\s*0",
                css,
                re.S,
            )
            is not None
        ),
        "beam_laser_1px": re.search(
            r"\.main\s*>\s*\.beam\s*\{[^}]*height:\s*1px[^}]*"
            r"background:\s*rgba\(\s*201,\s*162,\s*39,\s*0\.3\s*\)",
            css,
            re.S,
        )
        is not None,
        "honesty_fixed_led": re.search(
            r"body\s*>\s*\.honesty\s*\{[^}]*position:\s*fixed[^}]*"
            r"bottom:\s*0[^}]*left:\s*220px[^}]*height:\s*20px[^}]*"
            r"font-size:\s*10px",
            css,
            re.S,
        )
        is not None,
        "ledge_sticky": re.search(
            r"\.main\s*>\s*\.ledge\s*\{[^}]*position:\s*sticky[^}]*top:\s*0",
            css,
            re.S,
        )
        is not None,
        "compact_sticky_under_ledge": "--nr2-ledge-sticky-h" in css
        and re.search(
            r"\.main\s*>\s*\.exec-compact-header\s*\{[^}]*position:\s*sticky",
            css,
            re.S,
        )
        is not None,
    }
    return {k: bool(v) for k, v in checks.items()}


def http_ok(base: str, path: str) -> dict:
    url = base.rstrip("/") + "/" + path.lstrip("/")
    ctx = ssl._create_unverified_context()
    req = urllib.request.Request(url, headers={"User-Agent": "nr2-p1-gate/1.0"})
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=12) as r:
            body = r.read(200)
            return {
                "url": url,
                "status": r.status,
                "ok": 200 <= r.status < 300,
                "bytes": len(body),
            }
    except urllib.error.HTTPError as e:
        return {"url": url, "status": e.code, "ok": False, "error": str(e)}
    except Exception as e:
        return {"url": url, "status": None, "ok": False, "error": str(e)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="https://127.0.0.1:8765")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    css = (SITE / "nr2-optical-theme.css").read_text(encoding="utf-8")
    theme = theme_concrete_moves(css)
    schemas = [static_schema(SITE / p) for p in PAGES]
    http = [http_ok(args.base, p) for p in PAGES]
    schema_fail = [s for s in schemas if not (s["ledge_first"] and s["has_compact"] and s["honesty_not_in_main"] and s["honesty_after_main"])]
    theme_fail = [k for k, v in theme.items() if not v]
    http_fail = [h for h in http if not h["ok"]]
    report = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "moonshot_package": 1,
        "effort": "M (2-3 hrs)",
        "theme_concrete_moves": theme,
        "theme_fail": theme_fail,
        "schema": schemas,
        "schema_fail": [s["page"] for s in schema_fail],
        "http": http,
        "http_fail": [h["url"] for h in http_fail],
        "browser_gate_todo": {
            "viewports": ["1920x1080", "2560x1440"],
            "per_page": [
                "ledge fully in first viewport",
                "primary actions in first viewport",
                "honesty LED visible fixed bottom",
                "scroll only below money-strip; ledge+compact sticky",
                "CLS≈0 when honesty text updates",
                "empty ≠ $0; .sd/.qb/.hal retained",
            ],
        },
        "pass_static": not schema_fail and not theme_fail and not http_fail,
    }
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = OUT / f"p1_gate_{stamp}.json"
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    latest = OUT / "p1_gate_latest.json"
    latest.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"out": str(out), "pass_static": report["pass_static"], "theme_fail": theme_fail, "schema_fail": report["schema_fail"], "http_fail": report["http_fail"]}, indent=2))
    return 0 if report["pass_static"] else 1


if __name__ == "__main__":
    sys.exit(main())
