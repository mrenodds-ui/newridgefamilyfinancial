"""Extract standalone HTML mockups from Moonshot elite markdown reports."""
from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / ".local_logs" / "moonshot_financial_eval"
PREVIEW = OUT / "page_mockups_elite"


def page_id_from_html(html: str) -> str | None:
    title = re.search(r"<title>([^<]+)</title>", html, re.I)
    if title:
        t = title.group(1).lower()
        for pid in (
            "financial", "taxes", "hal", "softdent", "narratives", "claims",
            "ar", "quickbooks", "documents", "library", "office-manager",
        ):
            if pid.replace("-", " ") in t or pid in t:
                return pid
    for pid in (
        "financial", "taxes", "hal", "softdent", "narratives", "claims",
        "ar", "quickbooks", "documents", "library", "office-manager",
    ):
        if f'data-page="{pid}"' in html or f"{pid}-moonshot" in html:
            return pid
    return None


def extract_from_markdown(md_path: Path) -> list[str]:
    text = md_path.read_text(encoding="utf-8", errors="replace")
    written: list[str] = []
    pattern = re.compile(r"```html\s*\n(<!DOCTYPE html>[\s\S]*?</html>)\s*```", re.I)
    for i, match in enumerate(pattern.finditer(text)):
        html = match.group(1).strip()
        pid = page_id_from_html(html)
        if not pid:
            # infer from preceding heading
            before = text[: match.start()][-400:]
            for candidate in (
                "financial", "taxes", "hal", "softdent", "narratives", "claims",
                "ar", "quickbooks", "documents", "library", "office-manager",
            ):
                if re.search(rf"\*\*{candidate}\b", before, re.I) or re.search(rf"#+\s*{candidate}\b", before, re.I):
                    pid = candidate
                    break
        if not pid:
            pid = f"page_{i + 1}"
        dest = PREVIEW / f"{pid}.html"
        if dest.is_file() and len(html) <= len(dest.read_text(encoding="utf-8")):
            continue
        dest.write_text(html + "\n", encoding="utf-8")
        written.append(dest.name)
    return written


def main() -> int:
    PREVIEW.mkdir(parents=True, exist_ok=True)
    all_written: list[str] = []
    for md in sorted(OUT.glob("MOONSHOT_ELITE_PAGES_*.md")):
        if md.name.endswith("_ALL_"):
            continue
        written = extract_from_markdown(md)
        if written:
            print(f"{md.name}: {', '.join(written)}")
            all_written.extend(written)
    print(f"Total: {len(set(all_written))} files in {PREVIEW}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
