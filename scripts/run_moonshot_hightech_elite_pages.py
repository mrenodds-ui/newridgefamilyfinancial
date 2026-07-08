"""Moonshot AI consult: elite high-tech NR2 pages — HTML renderings + layout code (preview only)."""

from __future__ import annotations

import json
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / ".local_logs" / "moonshot_financial_eval"
PREVIEW = OUT / "page_mockups_elite"
OUT.mkdir(parents=True, exist_ok=True)
PREVIEW.mkdir(parents=True, exist_ok=True)
DATE = datetime.now(timezone.utc).strftime("%Y-%m-%d")

sys.path.insert(0, str(OUT))
from _run_moonshot_eval import extract_message_content, resolve_api_and_endpoint  # noqa: E402

DESIGN_RESEARCH = """
Design research (2025–2026 institutional finance / mission control):
- Bloomberg Terminal / Fortress / Signal dashboards: near-black (#0a0a0c–#181818), steel-blue accents, IBM Plex / JetBrains Mono for figures, compact density (32–40px KPI rows).
- SpaceX/Tesla mission control: 4-up grid, live animated sparklines, scrolling exception ticker, gold/cyan signal colors on charcoal, glassmorphism panels (backdrop-filter blur 12px, rgba borders).
- LobsterMC / trading command centers: bottom ticker, severity-coded alerts, portfolio P&L hero strip, agent/widget mosaic with hover glow.
- Animated charts WITHOUT new libraries: CSS @keyframes on SVG stroke-dashoffset, conic-gradient donut spin-in, bar grow-up transforms, dual-line path draw, heatmap cell pulse on refresh.
- Icons: inline SVG only (16–20px), stroke 1.5, no emoji in widget titles on production pages.
"""

SYSTEM = f"""You are Moonshot AI — elite product designer + front-end architect for NewRidge Financial 2.0.

The operator wants TOP-LINE, Elon Musk / SpaceX mission-control grade financial pages: extremely information-dense, compact, animated, professional — zero amateur UI.

{DESIGN_RESEARCH}

HARD RULES:
1. **Preview only** — deliver standalone HTML mockups + production JS/CSS patches. Do NOT assume changes are merged.
2. **50+ HAL widgets** — every key in HalSkills.WIDGET_ORDER must appear on exactly one staff page panel with `data-hal-widget-key`. HAL page shows mosaic tiles linking to all widgets (no duplicate keys per page).
3. **No diagnostic/debug UI on operator pages** — forbidden on staff page bodies: "Awaiting sync", "Import health", "DEGRADED", "publish status", "validation failed", boot errors, schema version banners, empty-state debug text. Use polished financial copy or neutral placeholders ($—, —%) instead.
4. **HAL integration** — each widget panel: `data-hal-widget-key="key"`, optional `data-hal-cmd`, bind via PageCanvasData. HAL refreshes via halWidgetFeed; mosaic on HAL page scrolls/highlights widgets.
5. **Stack** — vanilla JS IIFE modules, existing helpers only: stackOpen, dashboardPageOpen, heroKpiRow, canvasPanel, canvasGrid12, gridCol, chartContainer, vBarChart, dualLineChart, conicDonut, canvasTable, canvasKanbanLanes, canvasStatGrid, canvasGauge, canvasFunnel, canvasHeatmap, MoonshotLayoutEngine.render().
6. **Layouts** — moonshot-page-layouts.js manifest (panels array per page). Staff pages: widget-grid or dashboard-grid shells.
7. **Subpages** — HAL has zones: Command (Ask HAL), Mosaic (all widgets), Briefing. Treat each as a subpage section in the HTML mockup.

OUTPUT FORMAT (strict — every batch):

For EACH page in the batch:

### Preview: page_mockups_elite/<pageId>.html
```html
<!DOCTYPE html> ... full standalone dark page with CSS animations, nav rail, all widgets for that page ...
```

### Layout patch: moonshot-page-layouts.js — <pageId>
```javascript
// panels fragment for MOONSHOT_PAGE_LAYOUTS.pages.<pageId>
```

### Renderer note: moonshot-layout-engine.js — <pageId>
One paragraph: which panel types map to which chart animations.

### File: elite_css_snippet.css
```css
/* new animation + glass panel rules for this batch */
```

### Widget assignment table
Markdown table: widgetKey | page | panel title | chart type

End with ### Summary (5 lines): design rationale for this batch.

Be exhaustive — compact grids, animated SVG charts, monospace figures, mission-control ticker where appropriate."""

BATCHES: list[tuple[str, list[str], str]] = [
    (
        "overview",
        ["financial", "taxes", "hal"],
        "Executive cockpit + S-corp tax bridge + HAL command mosaic. Financial: hero KPI strip, dual-line production/collections, payer donut, reconciliation table, alert ticker. HAL: Ask HAL, situational hero, 50-widget mosaic grid (compact 4-col), morning briefing — NO import-health panel.",
    ),
    (
        "clinical",
        ["softdent", "narratives", "claims"],
        "Clinical velocity: operatory grid, A/R aging heatmap, case acceptance funnel, hygiene gauge. Narratives: composer workflow kanban. Claims: pipeline kanban + analytics row.",
    ),
    (
        "revenue",
        ["ar", "quickbooks"],
        "Revenue cycle: A/R waterfall + collections heatmap + follow-up queue. QuickBooks: dashboard-grid P&L, EBITDA bridge, expense treemap, cash flow dual-line.",
    ),
    (
        "operations",
        ["documents", "library", "office-manager"],
        "Ops: document intake + preview split, period close stat grid, AP automation. Library: search + preview. Office manager: stats-bar + today's priorities dashboard-grid.",
    ),
]

WIDGET_ORDER = [
    "practiceFinancialOverview", "nr2KpiRibbon", "nr2ProductionReconciliation", "nr2CollectionLag",
    "nr2GoalScorecard", "nr2AlertTicker", "nr2MonthlyTrendCombo", "nr2ProviderCompensationWidget",
    "softdentProductionDaily", "financialProductionTrend", "payerMixAndCollections", "providerPerformance",
    "ebitdaNormalization", "quickbooksProfitLossDetail", "quickbooksMonthlyRevenue", "quickbooksNetIncomeSummary",
    "quickbooksBalanceSheetSummary", "quickbooksCashFlowTrend", "quickbooksRevenueByService", "quickbooksArAging",
    "quickbooksExpenseBreakdown", "accountsPayableAutomation", "documentIntakeQueue", "documentPreview",
    "periodCloseAndPosting", "journalPostingQueue", "smartClaimsAndReceivables", "claimsPipeline",
    "arAgingAndCollections", "arOutstandingClaims", "careDeliveryPerformance", "softdentArAging",
    "softdentResponsibility", "newPatients", "treatmentPlanSummary", "caseAcceptance", "hygieneRecall",
    "softdentOperatoryGrid", "softdentCollectionsDaily", "softdentNewPatientsMTD", "softdentClaimsOutstanding",
    "softdentProviderProduction", "softdentAppointmentsSnapshot", "narrativeWorkflow", "documentLibrary",
    "halMorningBriefing", "halSituationalHero", "halAskHal", "sidenotesProgram", "halImportHealth",
]


def read_truncated(rel: str, max_lines: int = 200) -> str:
    path = REPO / rel
    if not path.is_file():
        return f"(missing {rel})"
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    body = "\n".join(lines[:max_lines])
    if len(lines) > max_lines:
        body += f"\n... [{len(lines) - max_lines} lines truncated]"
    return body


def build_user(batch_id: str, page_ids: list[str], focus: str) -> str:
    registry = read_truncated("NewRidgeFinancial2/site/moonshot-page-registry.js", 220)
    layouts = read_truncated("NewRidgeFinancial2/site/moonshot-page-layouts.js", 180)
    canvas = read_truncated("NewRidgeFinancial2/site/page-canvas.js", 200)
    engine = read_truncated("NewRidgeFinancial2/site/moonshot-layout-engine.js", 120)
    hal_widgets = read_truncated("NewRidgeFinancial2/site/hal-skills.js", 80, start=1330)

    widget_list = "\n".join(f"- `{k}`" for k in WIDGET_ORDER)
    return f"""Design elite mission-control pages for batch `{batch_id}`.

## Operator intent (TOP LINE — like Elon would demand)
{focus}

## Pages in this batch
{", ".join(page_ids)}

## All {len(WIDGET_ORDER)} HAL widgets (assign each to a page in your tables; HAL mosaic shows all)
{widget_list}

## MoonshotPageRegistry (excerpt)
```javascript
{registry}
```

## moonshot-page-layouts.js (excerpt)
```javascript
{layouts}
```

## PageCanvas helpers (excerpt)
```javascript
{canvas}
```

## MoonshotLayoutEngine (excerpt)
```javascript
{engine}
```

## HalSkills.WIDGET_ORDER (excerpt)
```javascript
{hal_widgets}
```

Deliver full standalone HTML mockup per page + layout JS fragments + CSS animation snippets.
Remember: NO diagnostic/import-health/debug copy on staff pages. HAL page: widget mosaic yes, but no "Import & Source Health" hero panel — fold health into subtle footer dot if needed."""


def read_truncated_start(rel: str, max_lines: int, start: int) -> str:
    path = REPO / rel
    if not path.is_file():
        return f"(missing {rel})"
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    chunk = lines[start - 1 : start - 1 + max_lines]
    return "\n".join(chunk)


# Fix build_user to use read_truncated_start for hal-skills
def build_user_fixed(batch_id: str, page_ids: list[str], focus: str) -> str:
    registry = read_truncated("NewRidgeFinancial2/site/moonshot-page-registry.js", 220)
    layouts = read_truncated("NewRidgeFinancial2/site/moonshot-page-layouts.js", 180)
    canvas = read_truncated("NewRidgeFinancial2/site/page-canvas.js", 200)
    engine = read_truncated("NewRidgeFinancial2/site/moonshot-layout-engine.js", 120)
    hal_widgets = read_truncated_start("NewRidgeFinancial2/site/hal-skills.js", 60, 1330)

    widget_list = "\n".join(f"- `{k}`" for k in WIDGET_ORDER)
    return f"""Design elite mission-control pages for batch `{batch_id}`.

## Operator intent (TOP LINE — like Elon would demand)
{focus}

## Pages in this batch
{", ".join(page_ids)}

## All {len(WIDGET_ORDER)} HAL widgets (assign each to a page in your tables; HAL mosaic shows all)
{widget_list}

## MoonshotPageRegistry (excerpt)
```javascript
{registry}
```

## moonshot-page-layouts.js (excerpt)
```javascript
{layouts}
```

## PageCanvas helpers (excerpt)
```javascript
{canvas}
```

## MoonshotLayoutEngine (excerpt)
```javascript
{engine}
```

## HalSkills.WIDGET_ORDER (excerpt)
```javascript
{hal_widgets}
```

Deliver full standalone HTML mockup per page + layout JS fragments + CSS animation snippets.
Remember: NO diagnostic/import-health/debug copy on staff pages. HAL page: widget mosaic yes, but no "Import & Source Health" hero panel — fold health into subtle footer dot if needed."""


def call_model(api_key: str, base_url: str, user: str, model: str = "kimi-k2.6") -> tuple[str, str]:
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": user},
        ],
        "temperature": 1.0,
        "max_tokens": 32768,
    }
    req = urllib.request.Request(
        base_url,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=1200) as resp:
            body = json.loads(resp.read().decode())
        return extract_message_content(body), "ok"
    except urllib.error.HTTPError as exc:
        err = exc.read().decode("utf-8", errors="replace")[:4000]
        if model == "kimi-k2.6":
            print(f"  kimi-k2.6 failed ({exc.code}), retrying kimi-k2.5...")
            return call_model(api_key, base_url, user, model="kimi-k2.5")
        return f"HTTP {exc.code}: {err}", f"HTTP {exc.code}"
    except Exception as exc:
        if model == "kimi-k2.6":
            print(f"  kimi-k2.6 error ({exc}), retrying kimi-k2.5...")
            return call_model(api_key, base_url, user, model="kimi-k2.5")
        return str(exc), "error"


def extract_html_previews(markdown: str, dest: Path) -> list[str]:
    dest.mkdir(parents=True, exist_ok=True)
    written: list[str] = []
    patterns = [
        re.compile(
            r"### Preview:\s*page_mockups_elite/([^\s]+\.html)\s*\n```html\s*\n([\s\S]*?)```",
            re.MULTILINE,
        ),
        re.compile(
            r"### File:\s*page_mockups_elite/([^\s]+\.html)\s*\n```html\s*\n([\s\S]*?)```",
            re.MULTILINE,
        ),
    ]
    for pattern in patterns:
        for match in pattern.finditer(markdown):
            name, content = match.group(1), match.group(2).strip()
            path = dest / name
            if name not in written:
                path.write_text(content + "\n", encoding="utf-8")
                written.append(name)
    return written


def extract_layout_snippets(markdown: str, dest: Path) -> list[str]:
    dest.mkdir(parents=True, exist_ok=True)
    written: list[str] = []
    pattern = re.compile(
        r"### Layout patch:\s*moonshot-page-layouts\.js\s*—\s*(\S+)\s*\n```javascript\s*\n([\s\S]*?)```",
        re.MULTILINE,
    )
    for match in pattern.finditer(markdown):
        page_id, content = match.group(1), match.group(2).strip()
        name = f"layout_{page_id}.js"
        (dest / name).write_text(content + "\n", encoding="utf-8")
        written.append(name)
    return written


def write_gallery_index(preview_dir: Path, pages: list[str]) -> None:
    sections = {
        "Overview": ["financial", "taxes", "hal"],
        "Clinical": ["softdent", "narratives", "claims"],
        "Revenue": ["ar", "quickbooks"],
        "Operations": ["documents", "library", "office-manager"],
    }
    cards = []
    ready = 0
    for section, ids in sections.items():
        cards.append(f'<h2>{section}</h2><div class="grid">')
        for pid in ids:
            html = preview_dir / f"{pid}.html"
            if html.is_file():
                ready += 1
                cards.append(
                    f'<a class="card card--ready" href="{pid}.html">'
                    f'<span class="id">{pid}</span><strong>{pid.replace("-", " ").title()}</strong>'
                    f'<span class="hint">Elite mockup · open preview</span></a>'
                )
            else:
                cards.append(
                    f'<div class="card card--pending"><span class="id">{pid}</span>'
                    f'<strong>{pid}</strong><span class="hint">Pending Moonshot batch</span></div>'
                )
        cards.append("</div>")
    index = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>NR2 Elite Page Mockups — Moonshot {DATE}</title>
  <style>
    :root {{ --bg:#0a0a0c; --surface:#141418; --accent:#22d3ee; --gold:#d4a853; --text:#f0f0f2; --muted:#8b8b96; }}
    * {{ box-sizing:border-box; }}
    body {{ margin:0; font-family:'Segoe UI',system-ui,sans-serif; background:var(--bg); color:var(--text); padding:2rem; }}
    h1 {{ margin:0 0 .35rem; font-size:1.85rem; letter-spacing:-.02em; }}
    h2 {{ margin:2rem 0 .75rem; font-size:.85rem; text-transform:uppercase; letter-spacing:.12em; color:var(--gold); }}
    p {{ color:var(--muted); max-width:58rem; line-height:1.6; }}
    .badge {{ display:inline-block; margin-top:.5rem; padding:.3rem .75rem; border-radius:999px;
      background:rgba(34,211,238,.12); color:var(--accent); font-size:.82rem; border:1px solid rgba(34,211,238,.25); }}
    .grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(220px,1fr)); gap:1rem; }}
    .card {{ display:flex; flex-direction:column; gap:.35rem; padding:1rem 1.1rem; background:var(--surface);
      border:1px solid rgba(255,255,255,.06); border-radius:10px; text-decoration:none; color:inherit; }}
    .card--ready {{ transition:transform .15s,border-color .15s,box-shadow .15s; }}
    .card--ready:hover {{ transform:translateY(-2px); border-color:var(--accent); box-shadow:0 8px 24px rgba(0,0,0,.4); }}
    .card--pending {{ opacity:.4; }}
    .id {{ font-size:.72rem; text-transform:uppercase; letter-spacing:.06em; color:var(--accent); }}
    .hint {{ font-size:.78rem; color:var(--muted); }}
  </style>
</head>
<body>
  <h1>NR2 Elite Mission-Control Mockups</h1>
  <p>Moonshot AI (kimi) — SpaceX/Bloomberg-grade layouts. <strong>Preview only</strong> — not wired into production until you approve.</p>
  <span class="badge">{ready} of 11 pages ready · {len(WIDGET_ORDER)} HAL widgets</span>
  {"".join(cards)}
</body>
</html>
"""
    (preview_dir / "index.html").write_text(index, encoding="utf-8")


def main() -> int:
    key_name, api_key, base_url = resolve_api_and_endpoint()
    if not api_key:
        print("No working Moonshot/OpenRouter API key found.")
        return 1
    print(f"Using {key_name} @ {base_url}")

    layout_dir = OUT / "elite_layouts"
    layout_dir.mkdir(parents=True, exist_ok=True)
    combined: list[str] = []
    all_html: list[str] = []

    for batch_id, page_ids, focus in BATCHES:
        print(f"\n--- Batch {batch_id}: {', '.join(page_ids)} ---")
        user = build_user_fixed(batch_id, page_ids, focus)
        text, status = call_model(api_key, base_url, user)
        out_md = OUT / f"MOONSHOT_ELITE_PAGES_{batch_id}_{DATE}.md"
        out_md.write_text(
            f"# Moonshot Elite Pages — {batch_id}\n\nKey: {key_name}\nStatus: {status}\n\n{text}\n",
            encoding="utf-8",
        )
        print(f"Saved {out_md.name} ({len(text)} chars, {status})")
        combined.append(f"\n\n# Batch {batch_id}\n\n{text}")
        html_written = extract_html_previews(text, PREVIEW)
        layout_written = extract_layout_snippets(text, layout_dir)
        all_html.extend(html_written)
        if html_written:
            print(f"HTML previews: {', '.join(html_written)}")
        if layout_written:
            print(f"Layout snippets: {', '.join(layout_written)}")
        write_gallery_index(PREVIEW, all_html)
        if status != "ok":
            print(f"Batch {batch_id} failed — stopping.")
            break

    combined_path = OUT / f"MOONSHOT_ELITE_PAGES_ALL_{DATE}.md"
    combined_path.write_text(
        f"# Moonshot Elite Pages — all batches\n\nKey: {key_name}\nWidgets: {len(WIDGET_ORDER)}\n\n{''.join(combined)}\n",
        encoding="utf-8",
    )
    write_gallery_index(PREVIEW, all_html)
    print(f"\nCombined report: {combined_path}")
    print(f"Gallery: {PREVIEW / 'index.html'}")
    print(f"HTML files: {sorted(set(all_html))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
