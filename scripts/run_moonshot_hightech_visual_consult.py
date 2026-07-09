"""Moonshot AI consult — high-tech visual polish of CURRENT live-wire pages.

Uses existing widgets only. Returns report + paste-ready CSS/JS.
Does NOT apply any code changes (operator validation required).
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / ".local_logs" / "moonshot_financial_eval"
DOCS = REPO / "NewRidgeFinancial2" / "docs"
OUT.mkdir(parents=True, exist_ok=True)
DATE = datetime.now(timezone.utc).strftime("%Y-%m-%d")

sys.path.insert(0, str(OUT))
from _run_moonshot_eval import extract_message_content, resolve_api_and_endpoint  # noqa: E402

SYSTEM = """You are Moonshot AI (kimi-k2 class) — elite product designer + front-end architect
for NewRidge Financial 2.0 (dental practice financial OS).

OPERATOR REQUEST (CRITICAL):
- Improve the LOOK of the CURRENT live staff pages to a highly professional, high-tech
  mission-control / institutional-finance program.
- Use ONLY the widgets / panel keys already present in moonshot-page-layouts.js and
  MoonshotLayoutEngine (do NOT invent new widget keys or data pipelines).
- Deliver a REPORT + paste-ready CODE.
- Do NOT assume anything is merged. This is CONSULT-ONLY. Operator will validate before any apply.

CURRENT STATE (2026-07-09, build ~hal-10164):
- staffRenderMode: live-wire-pilot — MoonshotLayoutEngine renders all 11 staff pages.
- Elite Jul 8 mockups exist at page_mockups_elite/*.html (visual target language).
- Honesty rules stay: empty widgets show honest CTAs naming exact export files — never fabricate $.
- Operator feedback: "updated pages look no different from old schema" — visual delta is too weak.

DESIGN TARGET:
- Bloomberg / SpaceX mission-control density: near-black surfaces, glass panels, monospace figures,
  cyan/gold signal accents, animated SVG charts (CSS keyframes only — no new chart libraries),
  compact KPI heroes, severity-coded alerts, crisp kanban boards.
- Keep existing PageCanvas helpers: heroKpiRow, canvasPanel, chartContainer, vBarChart, dualLineChart,
  conicDonut, canvasTable, canvasKanbanLanes, canvasStatGrid, canvasGauge, canvasFunnel, canvasHeatmap.

HARD RULES:
1. Existing widgets only — reference keys already in layouts (claimsPipeline, narrativeWorkflow,
   quickbooksProfitLossDetail, softdentOperatoryGrid, etc.).
2. Prefer CSS + small layout-engine chrome tweaks over rewriting data binders.
3. Preserve live-wire honesty empty states (widgetImportCta / canvasEmptyFor).
4. Paste-ready code with exact file paths under NewRidgeFinancial2/site/ (or deferred-live-wire/).
5. Mark every change P0/P1/P2 with acceptance criteria.
6. No emoji in production widget titles.

OUTPUT FORMAT (strict markdown):
# Verdict (one paragraph — will this make pages look clearly high-tech vs today?)
## 1. Why pages still look like the old schema
Root causes (CSS specificity, mock-embed chrome hiding tools, missing elite glass/animation classes,
kanban density, KPI typography, etc.).
## 2. Visual Design System (tokens + rules)
CSS variables, typography (display vs mono figures), panel glass, glow, motion budget (2–4 intentional animations).
## 3. Page-by-page polish plan
For EACH of: financial, softdent, quickbooks, ar, taxes, claims, narratives, documents, library, office-manager, hal
list: current weak spots, target look, which EXISTING widgets to emphasize, CSS/class changes only.
## 4. Moonshot Code Deliverables
### File: <path>
```css or javascript
paste-ready patch
```
Minimum deliverables:
- nr2-mockup-page-vocabulary.css (or nr2-moonshot-glow.css) — elite glass + KPI + kanban + dashboard density
- moonshot-layout-engine.js — small className / shell chrome tweaks if needed (no new widgets)
- Optional: page-canvas.js hero/kanban markup class upgrades
Do NOT change import/data honesty logic.
## 5. Diff vs Jul 8 elite mockups
What elite has that live still lacks visually (even when structure matches).
## 6. Operator Validation Gate
Browser checklist before approving any merge (Claims 6-lane look, QB glass panels, Narratives print+kanban, Financial hero density).
## 7. Prioritized apply order (max 4 commits) — WAIT for operator "proceed"
"""


def read_truncated(rel: str, max_lines: int = 180) -> str:
    path = REPO / rel
    if not path.is_file():
        return f"(missing {rel})"
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    body = "\n".join(lines[:max_lines])
    if len(lines) > max_lines:
        body += f"\n... [{len(lines) - max_lines} lines truncated] ..."
    return f"### {rel}\n```\n{body}\n```\n"


def elite_snippet(page_id: str, max_chars: int = 3500) -> str:
    path = OUT / "page_mockups_elite" / f"{page_id}.html"
    if not path.is_file():
        return f"(missing elite {page_id}.html)"
    text = path.read_text(encoding="utf-8", errors="replace")
    return text[:max_chars] + ("\n...[truncated]..." if len(text) > max_chars else "")


def build_user_prompt() -> str:
    parts = [
        "# Operator brief",
        "Improve LOOK of current live-wire pages to high-tech professional mission-control grade.",
        "Use existing widgets only. Return report + code. Do not apply.",
        "",
        "# Current build",
        read_truncated("NewRidgeFinancial2/nr2-build.json", 40),
        "# Live layouts (widget inventory — do not invent keys)",
        read_truncated("NewRidgeFinancial2/site/deferred-live-wire/moonshot-page-layouts.js", 220),
        "# Layout engine (render chrome)",
        read_truncated("NewRidgeFinancial2/site/deferred-live-wire/moonshot-layout-engine.js", 160),
        "# Page canvas helpers / hero / kanban",
        read_truncated("NewRidgeFinancial2/site/page-canvas.js", 120),
        "# Current vocabulary CSS (what live already has)",
        read_truncated("NewRidgeFinancial2/site/nr2-mockup-page-vocabulary.css", 100),
        read_truncated("NewRidgeFinancial2/site/nr2-moonshot-glow.css", 80),
        "# Elite visual targets (Jul 8) — sample pages",
    ]
    for pid in ("claims", "quickbooks", "financial", "narratives", "softdent"):
        parts.append(f"## Elite {pid}.html (truncated)\n```html\n{elite_snippet(pid)}\n```\n")
    parts.append(
        "Respond with the strict OUTPUT FORMAT. Emphasize CSS/visual delta that an operator "
        "will notice in 5 seconds vs today's live pages."
    )
    return "\n".join(parts)


def call_moonshot(system: str, user: str) -> tuple[str, str, str]:
    # resolve_api_and_endpoint → (key_name, api_key, base_url)
    key_name, api_key, base_url = resolve_api_and_endpoint()
    if not api_key:
        raise RuntimeError("No Moonshot/OpenRouter API key available")

    candidates: list[tuple[str, str]] = []
    if "openrouter" in (base_url or "").lower() or "OPENROUTER" in (key_name or "").upper():
        candidates.append((base_url, "moonshotai/kimi-k2"))
        candidates.append((base_url, "moonshotai/kimi-k2.5"))
        candidates.append(("https://api.moonshot.ai/v1/chat/completions", "kimi-k2.5"))
    else:
        candidates.append((base_url or "https://api.moonshot.ai/v1/chat/completions", "kimi-k2.5"))
        candidates.append(("https://api.moonshot.ai/v1/chat/completions", "kimi-k2.6"))
        candidates.append(("https://openrouter.ai/api/v1/chat/completions", "moonshotai/kimi-k2"))

    last_err = ""
    for url, mdl in candidates:
        payload = {
            "model": mdl,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": 1,
        }
        if "api.moonshot." in url:
            payload["top_p"] = 0.95
        body = json.dumps(payload).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }
        if "openrouter.ai" in url:
            headers["HTTP-Referer"] = os.getenv("OPENROUTER_HTTP_REFERER") or "https://github.com/NewRidgeFamilyFinancial"
            headers["X-Title"] = os.getenv("OPENROUTER_X_TITLE") or "NR2 High-Tech Visual Consult"
        req = urllib.request.Request(url, data=body, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=360) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            content = extract_message_content(data)
            if content and len(content.strip()) > 200:
                return content, mdl, key_name or "API_KEY"
            last_err = f"empty/short response from {mdl} @ {url}"
        except urllib.error.HTTPError as e:
            err_body = e.read()[:400]
            last_err = f"HTTP {e.code} {mdl} @ {url}: {err_body!r}"
        except Exception as e:  # noqa: BLE001
            last_err = f"{type(e).__name__} {mdl} @ {url}: {e}"
    raise RuntimeError(last_err or "Moonshot call failed")


def main() -> int:
    print("Building Moonshot high-tech visual consult prompt…")
    user = build_user_prompt()
    prompt_path = OUT / f"HIGHTECH_VISUAL_PROMPT_{DATE}.md"
    prompt_path.write_text(user, encoding="utf-8")
    print(f"Prompt saved: {prompt_path} ({len(user)} chars)")

    try:
        content, model, key_name = call_moonshot(SYSTEM, user)
    except Exception as e:  # noqa: BLE001
        err = f"# Moonshot High-Tech Visual Consult FAILED\n\n{e}\n"
        fail_path = DOCS / f"MOONSHOT_HIGHTECH_VISUAL_CONSULT_{DATE}_FAILED.md"
        fail_path.write_text(err, encoding="utf-8")
        print(err, file=sys.stderr)
        return 1

    header = (
        f"# Moonshot AI — High-Tech Visual Polish Consult\n"
        f"**Date:** {DATE}\n"
        f"**Model:** {model} via {key_name}\n"
        f"**Status:** REVIEW ONLY — do not apply until operator validates\n"
        f"**Script:** `scripts/run_moonshot_hightech_visual_consult.py`\n"
        f"**Scope:** Existing live-wire widgets only; CSS/chrome polish to mission-control look\n\n"
        f"---\n\n"
    )
    report = header + content.strip() + "\n"
    out_docs = DOCS / f"MOONSHOT_HIGHTECH_VISUAL_CONSULT_{DATE}.md"
    out_log = OUT / f"MOONSHOT_HIGHTECH_VISUAL_CONSULT_{DATE}.md"
    out_docs.write_text(report, encoding="utf-8")
    out_log.write_text(report, encoding="utf-8")
    print(f"Wrote {out_docs}")
    print(f"Wrote {out_log}")
    print(f"Chars: {len(report)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
