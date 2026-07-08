"""Assemble full standalone elite HTML previews from Moonshot markdown blocks."""
from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / ".local_logs" / "moonshot_financial_eval"
PREVIEW = OUT / "page_mockups_elite"
REF = OUT / "page_mockups"
MD = OUT / "MOONSHOT_ELITE_PAGES_overview_2026-07-08.md"

ELITE_CSS = """
:root {
  --bg: #0a0a0c;
  --surface: #141418;
  --elevated: #1c1c22;
  --border: rgba(255,255,255,.08);
  --text: #f0f0f2;
  --muted: #8b8b96;
  --green: #78a86b;
  --blue: #60a5fa;
  --gold: #d6b15e;
  --cyan: #22d3ee;
  --red: #f87171;
  --amber: #fbbf24;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: "Segoe UI", system-ui, sans-serif;
  background: var(--bg);
  color: var(--text);
  min-height: 100vh;
}
.nav-rail {
  position: fixed; left: 0; top: 0; width: 210px; height: 100vh;
  background: var(--surface); border-right: 1px solid var(--border);
  padding: 16px 0; z-index: 10;
}
.nav-brand { padding: 0 18px 20px; border-bottom: 1px solid var(--border); margin-bottom: 12px; }
.nav-brand h2 { font-size: 13px; letter-spacing: .08em; }
.nav-brand span { font-size: 10px; color: var(--cyan); text-transform: uppercase; letter-spacing: .12em; }
.nav-item {
  display: block; padding: 10px 18px; color: var(--muted); text-decoration: none; font-size: 13px;
  border-left: 3px solid transparent;
}
.nav-item:hover, .nav-item.active { color: var(--text); background: var(--elevated); border-left-color: var(--cyan); }
.page-shell { margin-left: 210px; padding: 24px 28px 48px; }
.page-title { font-size: 26px; font-weight: 600; letter-spacing: -.02em; }
.page-sub { color: var(--muted); font-size: 14px; margin-top: 4px; margin-bottom: 16px; }
.page-filters { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 20px; }
.filter-chip {
  padding: 6px 12px; border-radius: 999px; font-size: 12px;
  border: 1px solid var(--border); color: var(--muted); background: var(--surface);
}
.filter-chip.primary { border-color: rgba(34,211,238,.35); color: var(--cyan); background: rgba(34,211,238,.08); }
.widget-grid {
  display: grid; grid-template-columns: repeat(12, 1fr); gap: 16px;
}
.col-3 { grid-column: span 3; }
.col-4 { grid-column: span 4; }
.col-6 { grid-column: span 6; }
.col-8 { grid-column: span 8; }
.col-12 { grid-column: span 12; }
.ms-panel {
  background: rgba(20,20,24,.72); backdrop-filter: blur(12px);
  border: 1px solid var(--border); border-radius: 10px; overflow: hidden;
  transition: box-shadow .2s, border-color .2s;
}
.ms-panel:hover { border-color: rgba(34,211,238,.25); box-shadow: 0 8px 28px rgba(0,0,0,.35); }
.ms-panel-head {
  padding: 10px 14px; font-size: 11px; text-transform: uppercase; letter-spacing: .08em;
  color: var(--muted); border-bottom: 1px solid var(--border);
}
.ms-panel-body { padding: 14px; }
.kpi-hero-row { display: grid; grid-template-columns: repeat(5, 1fr); gap: 10px; }
.kpi-hero-tile {
  background: var(--elevated); border: 1px solid var(--border); border-radius: 8px; padding: 12px;
}
.kpi-label { font-size: 10px; text-transform: uppercase; letter-spacing: .06em; color: var(--muted); }
.kpi-value { font-family: Consolas, "Courier New", monospace; font-size: 22px; font-weight: 700; margin-top: 4px; }
.kpi-hint { font-size: 12px; color: var(--green); margin-top: 2px; }
.alert-ticker { overflow: hidden; border: 1px solid var(--border); border-radius: 8px; background: var(--surface); }
.ticker-track {
  display: flex; gap: 28px; padding: 10px 14px; white-space: nowrap;
  animation: ticker 28s linear infinite;
}
.ticker-item { font-size: 12px; color: var(--muted); }
.severity-gold { color: var(--gold); }
.severity-cyan { color: var(--cyan); }
@keyframes ticker { from { transform: translateX(0); } to { transform: translateX(-50%); } }
.trend-chart-svg { width: 100%; height: 140px; display: block; }
@keyframes dashDraw { to { stroke-dashoffset: 0; } }
.bar-chart { display: flex; align-items: flex-end; gap: 8px; height: 120px; }
.bar-chart-column { flex: 1; display: flex; flex-direction: column; align-items: center; gap: 6px; height: 100%; justify-content: flex-end; }
.bar-chart-fill {
  width: 100%; border-radius: 4px 4px 0 0; transform-origin: bottom;
  animation: barGrow .8s ease-out forwards; transform: scaleY(0);
}
.bar-chart-label { font-size: 10px; color: var(--muted); }
@keyframes barGrow { to { transform: scaleY(1); } }
.gauge-wrap { position: relative; height: 120px; display: flex; align-items: center; justify-content: center; }
.gauge-center { position: absolute; text-align: center; }
.gauge-value { font-size: 28px; font-weight: 700; font-family: Consolas, monospace; color: var(--gold); }
.gauge-label { font-size: 10px; color: var(--muted); text-transform: uppercase; }
.canvas-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.canvas-table th, .canvas-table td { padding: 8px 6px; border-bottom: 1px solid var(--border); text-align: left; }
.canvas-table .num { text-align: right; font-family: Consolas, monospace; }
.stat-grid { display: flex; flex-direction: column; gap: 10px; }
.stat-row { display: grid; grid-template-columns: 90px 1fr 64px; gap: 10px; align-items: center; }
.stat-label { font-size: 12px; color: var(--muted); }
.stat-bar-bg { height: 8px; background: var(--elevated); border-radius: 999px; overflow: hidden; }
.stat-bar-fill { height: 100%; width: var(--w, 50%); border-radius: 999px; animation: barGrow .9s ease-out forwards; transform-origin: left; }
.stat-num { font-family: Consolas, monospace; font-size: 12px; text-align: right; }
.donut-wrap { display: flex; gap: 16px; align-items: center; }
.donut-chart { border-radius: 50%; display: flex; align-items: center; justify-content: center; animation: spinIn .8s ease-out; }
.donut-hole {
  width: 56px; height: 56px; border-radius: 50%; background: var(--surface);
  display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 600;
}
.chart-legend { display: flex; flex-direction: column; gap: 6px; font-size: 12px; }
.legend-row { display: flex; align-items: center; gap: 8px; }
.legend-dot { width: 8px; height: 8px; border-radius: 50%; }
.sparkline-svg { width: 80px; height: 30px; }
@keyframes spinIn { from { transform: rotate(-90deg) scale(.8); opacity: 0; } to { transform: rotate(0) scale(1); opacity: 1; } }
@keyframes gaugeDraw { to { stroke-dashoffset: 40; } }
.financial-moonshot .kpi-value { color: var(--text); }
.taxes-moonshot .kpi-value { color: var(--blue); }
@media (max-width: 1100px) {
  .col-3, .col-4, .col-6, .col-8 { grid-column: span 12; }
  .kpi-hero-row { grid-template-columns: repeat(2, 1fr); }
}
"""

NAV = """
<nav class="nav-rail">
  <div class="nav-brand"><h2>NEW RIDGE</h2><span>Financial 2.0 · Elite</span></div>
  <a class="nav-item" href="financial.html">Financial</a>
  <a class="nav-item" href="taxes.html">Taxes</a>
  <a class="nav-item" href="../page_mockups/hal.html">HAL</a>
  <a class="nav-item" href="../page_mockups/softdent.html">SoftDent</a>
  <a class="nav-item" href="../page_mockups/narratives.html">Narratives</a>
  <a class="nav-item" href="../page_mockups/claims.html">Claims</a>
  <a class="nav-item" href="../page_mockups/ar.html">A/R</a>
  <a class="nav-item" href="../page_mockups/quickbooks.html">QuickBooks</a>
  <a class="nav-item" href="../page_mockups/documents.html">Documents</a>
  <a class="nav-item" href="../page_mockups/library.html">Library</a>
  <a class="nav-item" href="../page_mockups/office-manager.html">Office Manager</a>
  <a class="nav-item" href="index.html">Gallery</a>
</nav>
"""


def extract_blocks(md_text: str) -> dict[str, str]:
    out: dict[str, str] = {}
    pattern = re.compile(r"```html\s*\n(<!DOCTYPE html>[\s\S]*?</html>)\s*```", re.I)
    for match in pattern.finditer(md_text):
        html = match.group(1)
        title = re.search(r"<title>([^<]+)</title>", html, re.I)
        if not title:
            continue
        t = title.group(1).lower()
        if re.search(r"\btaxes\b", t):
            out["taxes"] = html
        elif re.search(r"\bfinancial\b", t):
            out["financial"] = html
        elif re.search(r"\bhal\b", t):
            out["hal"] = html
    return out


def assemble(page_id: str, raw: str) -> str:
    body_match = re.search(r"<body[^>]*>([\s\S]*)</body>", raw, re.I)
    body = body_match.group(1) if body_match else raw
    body = body.replace('<div class="nav-rail">...</div>', NAV.strip())
    body = re.sub(r"<style>[\s\S]*?</style>", "", body, count=1)
    active_nav = f'href="{page_id}.html"'
    nav = NAV.replace(active_nav, f'href="{page_id}.html" class="nav-item active"').replace(
        'class="nav-item active"', 'class="nav-item"', 1
    )
    nav = nav.replace(f'href="{page_id}.html"', f'href="{page_id}.html" class="nav-item active"', 1)
    body = re.sub(r"<div class=\"nav-rail\">[\s\S]*?</nav>", nav.strip(), body, count=1)
    if "<nav class=\"nav-rail\">" not in body:
        body = nav + body
    title = {"financial": "Financial", "taxes": "Taxes", "hal": "HAL"}.get(page_id, page_id.title())
    accent = {"financial": "green", "taxes": "blue", "hal": "gold"}.get(page_id, "green")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — NewRidge Financial 2.0 · Elite Preview</title>
<style>{ELITE_CSS}</style>
</head>
<body data-page="{page_id}" data-accent="{accent}">
{body.strip()}
</body>
</html>
"""


def write_index() -> None:
    pages = [
        ("Overview", [
            ("financial.html", "Financial", "Moonshot elite · 18 HAL widgets", True),
            ("taxes.html", "Taxes", "Moonshot elite · 12 HAL widgets", True),
            ("../page_mockups/hal.html", "HAL Command", "50-widget mosaic · reference mockup", False),
        ]),
        ("Clinical", [
            ("../page_mockups/softdent.html", "SoftDent", "Reference mockup", False),
            ("../page_mockups/narratives.html", "Narratives", "Reference mockup", False),
            ("../page_mockups/claims.html", "Claims", "Reference mockup", False),
        ]),
        ("Revenue", [
            ("../page_mockups/ar.html", "A/R", "Reference mockup", False),
            ("../page_mockups/quickbooks.html", "QuickBooks", "Reference mockup", False),
        ]),
        ("Operations", [
            ("../page_mockups/documents.html", "Documents", "Reference mockup", False),
            ("../page_mockups/library.html", "Library", "Reference mockup", False),
            ("../page_mockups/office-manager.html", "Office Manager", "Reference mockup", False),
        ]),
    ]
    cards = []
    elite = 0
    for section, items in pages:
        cards.append(f"<h2>{section}</h2><div class=\"grid\">")
        for href, label, hint, is_elite in items:
            cls = "card card--elite" if is_elite else "card"
            if is_elite:
                elite += 1
            cards.append(
                f'<a class="{cls}" href="{href}"><span class="id">{label}</span>'
                f"<strong>{label}</strong><span class=\"hint\">{hint}</span></a>"
            )
        cards.append("</div>")
    html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><title>NR2 Elite Review Gallery</title>
<style>
:root {{ --bg:#0a0a0c; --surface:#141418; --cyan:#22d3ee; --gold:#d6b15e; --text:#f0f0f2; --muted:#8b8b96; }}
body {{ margin:0; font-family:Segoe UI,system-ui,sans-serif; background:var(--bg); color:var(--text); padding:2rem; }}
h1 {{ margin:0 0 .5rem; }}
p {{ color:var(--muted); max-width:60rem; line-height:1.6; }}
.badge {{ display:inline-block; margin:.5rem 0 1.5rem; padding:.35rem .8rem; border-radius:999px;
  border:1px solid rgba(34,211,238,.3); color:var(--cyan); font-size:.82rem; }}
h2 {{ margin:1.5rem 0 .75rem; font-size:.85rem; text-transform:uppercase; letter-spacing:.1em; color:var(--gold); }}
.grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(220px,1fr)); gap:1rem; }}
.card {{ padding:1rem; background:var(--surface); border:1px solid rgba(255,255,255,.06); border-radius:10px;
  text-decoration:none; color:inherit; display:flex; flex-direction:column; gap:.3rem; }}
.card--elite {{ border-color:rgba(34,211,238,.35); box-shadow:0 0 0 1px rgba(34,211,238,.08) inset; }}
.card:hover {{ transform:translateY(-2px); border-color:var(--cyan); }}
.id {{ font-size:.72rem; color:var(--cyan); text-transform:uppercase; letter-spacing:.06em; }}
.hint {{ font-size:.78rem; color:var(--muted); }}
</style></head><body>
<h1>NR2 Elite Mission-Control — Review Before Integration</h1>
<p>Moonshot AI (kimi-k2.6) delivered new <strong>Financial</strong> and <strong>Taxes</strong> layouts with 50 HAL widgets mapped, animated charts, and zero diagnostic copy. Remaining 9 pages use Jul 7 reference mockups until batches 2–4 complete. <strong>Nothing wired into production yet.</strong></p>
<span class="badge">{elite} Moonshot elite pages · 50 HAL widgets · preview only</span>
{"".join(cards)}
</body></html>"""
    (PREVIEW / "index.html").write_text(html, encoding="utf-8")


def main() -> int:
    PREVIEW.mkdir(parents=True, exist_ok=True)
    if not MD.is_file():
        print(f"Missing {MD}")
        return 1
    blocks = extract_blocks(MD.read_text(encoding="utf-8"))
    for pid, raw in blocks.items():
        path = PREVIEW / f"{pid}.html"
        path.write_text(assemble(pid, raw), encoding="utf-8")
        print(f"Wrote {path.name}")
    write_index()
    print(f"Gallery: {PREVIEW / 'index.html'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
