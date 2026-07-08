"""Run remaining Moonshot elite page batches (clinical, revenue, operations).

Skips overview (financial/taxes/hal) unless --include-overview or --hal-only is passed.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

from run_moonshot_hightech_elite_pages import (  # noqa: E402
    BATCHES,
    DATE,
    OUT,
    PREVIEW,
    WIDGET_ORDER,
    build_user_fixed,
    call_model,
    extract_html_previews,
    extract_layout_snippets,
    write_gallery_index,
)

sys.path.insert(0, str(OUT))
from _run_moonshot_eval import resolve_api_and_endpoint  # noqa: E402


def select_batches(
    *,
    remaining_only: bool,
    hal_only: bool,
    batch_names: list[str] | None,
) -> list[tuple[str, list[str], str]]:
    if hal_only:
        for batch_id, page_ids, focus in BATCHES:
            if batch_id == "overview":
                return [("overview", ["hal"], focus.replace("Financial:", "HAL only:"))]
        return []

    if batch_names:
        wanted = {b.strip().lower() for b in batch_names}
        selected = [b for b in BATCHES if b[0] in wanted]
        missing = wanted - {b[0] for b in selected}
        if missing:
            print(f"Unknown batch(es): {', '.join(sorted(missing))}")
            print(f"Valid: {', '.join(b[0] for b in BATCHES)}")
        return selected

    if remaining_only:
        return [b for b in BATCHES if b[0] in {"clinical", "revenue", "operations"}]

    return list(BATCHES)


def count_widgets(html_path: Path) -> int:
    if not html_path.is_file():
        return 0
    text = html_path.read_text(encoding="utf-8", errors="replace")
    return len(set(__import__("re").findall(r'data-hal-widget-key="([^"]+)"', text)))


def write_gallery_index_all(preview_dir: Path) -> None:
    """Gallery with widget counts for every page that has HTML."""
    sections = {
        "Overview": ["financial", "taxes", "hal"],
        "Clinical": ["softdent", "narratives", "claims"],
        "Revenue": ["ar", "quickbooks"],
        "Operations": ["documents", "library", "office-manager"],
    }
    cards: list[str] = []
    ready = 0
    elite = 0
    for section, ids in sections.items():
        cards.append(f'<h2>{section}</h2><div class="grid">')
        for pid in ids:
            html = preview_dir / f"{pid}.html"
            if html.is_file():
                ready += 1
                elite += 1
                wc = count_widgets(html)
                cards.append(
                    f'<a class="card card--elite" href="{pid}.html">'
                    f'<span class="id">{pid}</span><strong>{pid.replace("-", " ").title()}</strong>'
                    f'<span class="hint">Elite mockup · {wc} HAL widgets</span></a>'
                )
            else:
                cards.append(
                    f'<div class="card card--pending"><span class="id">{pid}</span>'
                    f'<strong>{pid.replace("-", " ").title()}</strong>'
                    f'<span class="hint">Pending Moonshot batch</span></div>'
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
    .card--elite {{ transition:transform .15s,border-color .15s,box-shadow .15s;
      border-color:rgba(34,211,238,.35); box-shadow:0 0 0 1px rgba(34,211,238,.08) inset; }}
    .card--elite:hover {{ transform:translateY(-2px); border-color:var(--accent); box-shadow:0 8px 24px rgba(0,0,0,.4); }}
    .card--pending {{ opacity:.4; }}
    .id {{ font-size:.72rem; text-transform:uppercase; letter-spacing:.06em; color:var(--accent); }}
    .hint {{ font-size:.78rem; color:var(--muted); }}
  </style>
</head>
<body>
  <h1>NR2 Elite Mission-Control Mockups</h1>
  <p>Moonshot AI (kimi) — SpaceX/Bloomberg-grade layouts. <strong>Preview only</strong> — not wired into production until you approve.</p>
  <span class="badge">{ready} of 11 pages ready · {len(WIDGET_ORDER)} HAL widgets catalog</span>
  {"".join(cards)}
</body>
</html>
"""
    (preview_dir / "index.html").write_text(index, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Moonshot elite page consult batches")
    parser.add_argument(
        "--batches",
        nargs="+",
        help="Batch ids to run (default: clinical revenue operations)",
    )
    parser.add_argument(
        "--hal-only",
        action="store_true",
        help="Re-run overview batch for hal.html only",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all batches including overview",
    )
    args = parser.parse_args()

    if args.all:
        selected = select_batches(remaining_only=False, hal_only=False, batch_names=None)
    elif args.hal_only:
        selected = select_batches(remaining_only=False, hal_only=True, batch_names=None)
    elif args.batches:
        selected = select_batches(remaining_only=False, hal_only=False, batch_names=args.batches)
    else:
        selected = select_batches(remaining_only=True, hal_only=False, batch_names=None)

    if not selected:
        print("No batches selected.")
        return 1

    key_name, api_key, base_url = resolve_api_and_endpoint()
    if not api_key:
        print("No working Moonshot/OpenRouter API key found.")
        return 1
    print(f"Using {key_name} @ {base_url}")
    print(f"Batches: {', '.join(b[0] for b in selected)}")

    layout_dir = OUT / "elite_layouts"
    layout_dir.mkdir(parents=True, exist_ok=True)
    PREVIEW.mkdir(parents=True, exist_ok=True)

    results: list[dict] = []
    all_html: list[str] = []

    for batch_id, page_ids, focus in selected:
        print(f"\n--- Batch {batch_id}: {', '.join(page_ids)} ---")
        user = build_user_fixed(batch_id, page_ids, focus)
        text, status = call_model(api_key, base_url, user)
        out_md = OUT / f"MOONSHOT_ELITE_PAGES_{batch_id}_{DATE}.md"
        out_md.write_text(
            f"# Moonshot Elite Pages — {batch_id}\n\nKey: {key_name}\nStatus: {status}\n\n{text}\n",
            encoding="utf-8",
        )
        print(f"Saved {out_md.name} ({len(text)} chars, {status})")

        html_written = extract_html_previews(text, PREVIEW)
        layout_written = extract_layout_snippets(text, layout_dir)
        all_html.extend(html_written)

        # Fallback: extract full DOCTYPE blocks from markdown
        if not html_written:
            sys.path.insert(0, str(REPO / "scripts"))
            from extract_elite_previews import extract_from_markdown  # noqa: E402

            fallback = extract_from_markdown(out_md)
            if fallback:
                html_written = fallback
                all_html.extend(fallback)
                print(f"Fallback extract: {', '.join(fallback)}")

        widget_counts = {name: count_widgets(PREVIEW / name) for name in html_written}
        if html_written:
            print(f"HTML previews: {', '.join(html_written)}")
            for name, wc in widget_counts.items():
                print(f"  {name}: {wc} widgets")
        if layout_written:
            print(f"Layout snippets: {', '.join(layout_written)}")

        truncated = "truncated" in text.lower() or (
            status == "ok" and any("```html" in text and pid not in html_written for pid in page_ids)
        )
        results.append(
            {
                "batch": batch_id,
                "status": status,
                "pages": page_ids,
                "html": html_written,
                "widgets": widget_counts,
                "truncated": truncated,
                "chars": len(text),
            }
        )

        write_gallery_index_all(PREVIEW)

        if status != "ok":
            print(f"Batch {batch_id} failed — stopping.")
            break

    write_gallery_index_all(PREVIEW)

    print("\n=== Summary ===")
    for r in results:
        flag = " (possible truncation)" if r["truncated"] else ""
        print(f"  {r['batch']}: {r['status']}{flag} — HTML: {r['html'] or 'none'}")
    print(f"Gallery: {PREVIEW / 'index.html'}")
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
