"""Moonshot AI — elite mock HTML → live moonshot-mockup schema (exact parity + paste-ready code)."""

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
DOCS = REPO / "NewRidgeFinancial2" / "docs"
ELITE = OUT / "page_mockups_elite"
DATE = datetime.now(timezone.utc).strftime("%Y-%m-%d")

sys.path.insert(0, str(OUT))
from _run_moonshot_eval import extract_message_content, resolve_api_and_endpoint  # noqa: E402

SYSTEM = """You are Moonshot AI — lead front-end architect for NewRidge Financial 2.0.

The operator approved a consult ONLY (no deploy yet). Your job: design how to implement
**elite mock HTML pages** (`page_mockups_elite/*.html`) into the **live moonshot-mockup schema**
so the running app renders the SAME structure/classes as elite HTML — but wired to PageCanvasData
and HAL — replacing today's iframe mock-embed gate.

CURRENT STATE:
- staffRenderMode: mock-embed — PageCanvas.renderBody() → mockupPreviewGate() → iframe
- Target: staffRenderMode: live-wire — MoonshotLayoutEngine.render(pageId, H) from moonshot-page-layouts.js
- Layout engine + layouts live in deferred-live-wire/ (not loaded in index.html today)
- PageSchema epoch: moonshot-mockup (moonshot-page-registry.js)
- validate-pages.mjs blocks live-wire until operator flips flags

HARD RULES:
1. Match elite HTML DOM structure and CSS class names exactly (widget-grid, dashboard-grid, ms-panel,
   kpi-large, chart-container, kanban-board, stats-bar, data-hal-widget-key, col-* spans).
2. Use ONLY existing PageCanvas helpers — no new chart libraries.
3. Every PageSchema widget key for the page must appear exactly once as data-hal-widget-key.
4. Provide **paste-ready code blocks** with target file paths — operator will review before merge.
5. Do NOT delete mock-embed path until operator sign-off — show feature-flag flip.
6. HAL tab (#hal) stays on hal-page.js — staff pages only for this migration.

OUTPUT FORMAT (strict markdown sections):
# Verdict (one paragraph — go/no-go for live-wire flip)
## Executive Summary
## Elite vs Layout Manifest Gap Analysis (per page: financial, taxes, softdent, narratives, claims, ar, quickbooks, documents, library, office-manager)
For each page: elite HTML structure summary, manifest gaps, CSS gaps, dataBind gaps.
## Architecture Flip (mock-embed → live-wire)
Numbered steps: nr2-build.json, index.html script list, page-canvas.js, validate-pages.mjs, moonshot-site.manifest.json.
## Moonshot Code Deliverables
Subsections with ### File: <relative-path> and fenced code blocks for EVERY changed file.
Minimum deliverables:
- page-canvas.js renderBody() with flag-gated live-wire
- moonshot-page-layouts.js patches per page (merge into deferred-live-wire/)
- moonshot-layout-engine.js patches if panel types missing
- nr2-mockup-page-vocabulary.css / theme CSS deltas to match elite HTML
- index.html deferred script block to restore live-wire bundle
- validate-pages.mjs assertion updates
- nr2-build.json staffRenderMode flip snippet
## Per-Page Renderer Checklist
Table: pageId | shell | panel count | widget keys | chart types | acceptance test
## Risks & Rollback
## Operator Approval Gate
What the operator must verify in browser before approving merge.
## Prioritized Commits (max 5, with acceptance criteria)
"""

BATCHES: list[tuple[str, list[str], str]] = [
    (
        "overview",
        ["financial", "taxes"],
        "Overview batch: financial widget-grid executive cockpit; taxes S-corp planning panels.",
    ),
    (
        "clinical",
        ["softdent", "narratives", "claims"],
        "Clinical: softdent production/aging charts; narratives composer; claims analytics + kanban.",
    ),
    (
        "revenue",
        ["ar", "quickbooks"],
        "Revenue: A/R heatmap/waterfall; QuickBooks dashboard-grid P&L.",
    ),
    (
        "operations",
        ["documents", "library", "office-manager"],
        "Operations: documents table; library search; office-manager stats-bar + dashboard-grid.",
    ),
]

CONTEXT_FILES: list[tuple[str, int]] = [
    ("NewRidgeFinancial2/site/moonshot-page-registry.js", 220),
    ("NewRidgeFinancial2/site/page-canvas.js", 120),
    ("NewRidgeFinancial2/site/page-canvas.js", 120),  # tail — will dedupe
    ("NewRidgeFinancial2/deferred-live-wire/moonshot-layout-engine.js", 200),
    ("NewRidgeFinancial2/deferred-live-wire/moonshot-page-layouts.js", 200),
    ("NewRidgeFinancial2/nr2-build.json", 20),
    ("NewRidgeFinancial2/moonshot-site.manifest.json", 120),
    ("NewRidgeFinancial2/site/index.html", 80),
]


def read_truncated(rel: str, max_lines: int = 180) -> str:
    path = REPO / rel
    if not path.is_file():
        return f"(missing {rel})"
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    body = "\n".join(lines[:max_lines])
    if len(lines) > max_lines:
        body += f"\n... [{len(lines) - max_lines} lines truncated]"
    return body


def elite_body_excerpt(page_id: str, max_lines: int = 120) -> str:
    path = ELITE / f"{page_id}.html"
    if not path.is_file():
        return f"(missing elite HTML for {page_id})"
    text = path.read_text(encoding="utf-8", errors="replace")
    # Prefer main content after page-shell / widget-grid
    for marker in ("<div class=\"page-shell", "<div class=\"widget-grid", "<main"):
        idx = text.find(marker)
        if idx >= 0:
            snippet = text[idx : idx + 8000]
            lines = snippet.splitlines()[:max_lines]
            return "\n".join(lines)
    lines = text.splitlines()[:max_lines]
    return "\n".join(lines)


def build_user(batch_id: str, page_ids: list[str], focus: str) -> str:
    ctx_parts: list[str] = []
    seen: set[str] = set()
    for rel, max_lines in CONTEXT_FILES:
        if rel in seen:
            continue
        seen.add(rel)
        ctx_parts.append(f"### {rel}\n```\n{read_truncated(rel, max_lines)}\n```")

    elite_parts = []
    for pid in page_ids:
        elite_parts.append(f"### Elite HTML body excerpt: {pid}\n```html\n{elite_body_excerpt(pid, 100)}\n```")

    page_widgets = []
    for pid in page_ids:
        page_widgets.append(
            f"- **{pid}**: all widgets from PageSchema when live-wire (see registry PAGE_META + layouts manifest)"
        )

    return f"""Consult batch `{batch_id}` — elite mock HTML → live schema (REVIEW ONLY — operator has NOT approved deploy).

## Operator intent
Implement mock pages into the new moonshot-mockup schema **exactly** matching elite HTML structure.
Provide paste-ready code for operator review before any merge.

## Batch focus
{focus}

## Pages in this batch
{chr(10).join(page_widgets)}

## Program context
{chr(10).join(ctx_parts)}

## Elite mock HTML (this batch)
{chr(10).join(elite_parts)}

## Deliverables for this batch
1. Gap analysis for each page in batch vs deferred moonshot-page-layouts.js
2. Complete ### File: code blocks for all files touched to wire these pages live
3. CSS class parity notes referencing nr2-mockup-page-vocabulary.css
4. Feature-flag pattern so mock-embed remains fallback until operator sets staffRenderMode: live-wire

Do not skip code blocks. Be exact about col-span, panel types, and data-hal-widget-key assignments."""


def call_model(api_key: str, base_url: str, user: str) -> tuple[str, str]:
    payload = {
        "model": "kimi-k2.5",
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": user},
        ],
        "temperature": 1.0,
        "max_tokens": 16384,
    }
    req = urllib.request.Request(
        base_url,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=900) as resp:
            body = json.loads(resp.read().decode())
        return extract_message_content(body), "ok"
    except urllib.error.HTTPError as exc:
        return f"HTTP {exc.code}: {exc.read().decode('utf-8', errors='replace')[:4000]}", f"HTTP {exc.code}"
    except Exception as exc:
        return str(exc), "error"


def extract_code_files(markdown: str, dest: Path) -> list[str]:
    dest.mkdir(parents=True, exist_ok=True)
    written: list[str] = []
    pattern = re.compile(
        r"### File:\s*([^\n]+)\s*\n```(?:\w+)?\s*\n([\s\S]*?)```",
        re.MULTILINE,
    )
    for match in pattern.finditer(markdown):
        name = match.group(1).strip().replace("\\", "/")
        content = match.group(2).strip()
        safe = re.sub(r"[^\w./\-]", "_", name)
        path = dest / safe
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content + "\n", encoding="utf-8")
        written.append(str(path.relative_to(dest)))
    return written


def main() -> int:
    key_name, api_key, base_url = resolve_api_and_endpoint()
    if not api_key:
        print("No working Moonshot/OpenRouter API key found.")
        return 1
    print(f"Using {key_name} @ {base_url}")

    code_dir = OUT / "elite_to_live_schema_code"
    combined: list[str] = [
        f"# Moonshot AI — Elite Mock → Live Schema Consult\n",
        f"**Date:** {DATE}  \n**Model:** kimi-k2.5 via {key_name}  \n",
        f"**Status:** REVIEW ONLY — operator approval required before merge  \n",
        f"**Script:** `scripts/run_moonshot_elite_to_live_schema.py`\n",
    ]
    all_written: list[str] = []

    for batch_id, page_ids, focus in BATCHES:
        print(f"\n--- Batch {batch_id}: {', '.join(page_ids)} ---")
        user = build_user(batch_id, page_ids, focus)
        text, status = call_model(api_key, base_url, user)
        print(f"Status: {status} ({len(text)} chars)")
        combined.append(f"\n\n---\n\n## Batch: {batch_id}\n\n{text}")
        written = extract_code_files(text, code_dir / batch_id)
        all_written.extend(written)
        batch_path = OUT / f"MOONSHOT_ELITE_TO_LIVE_{batch_id}_{DATE}.md"
        batch_path.write_text(f"# Batch {batch_id}\n\n{text}\n", encoding="utf-8")
        print(f"Wrote {batch_path}")

    report_path = DOCS / f"MOONSHOT_ELITE_TO_LIVE_SCHEMA_{DATE}.md"
    report_path.write_text("".join(combined), encoding="utf-8")
    print(f"\nCombined report: {report_path}")
    if all_written:
        print(f"Extracted code files ({len(all_written)}): {code_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
