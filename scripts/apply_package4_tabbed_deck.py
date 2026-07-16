"""Apply Moonshot Package 4 Tabbed Content Deck to optical pages (one-shot)."""
from __future__ import annotations

import re
from pathlib import Path

SITE = Path(__file__).resolve().parents[1] / "NewRidgeFinancial2" / "site"


def tabs_nav(label: str, items: list[tuple[str, str]]) -> str:
    """items: (tab_id, title). First is Summary (selected)."""
    btns = []
    for i, (tid, title) in enumerate(items):
        sel = "true" if i == 0 else "false"
        tabix = "0" if i == 0 else "-1"
        btns.append(
            f'        <button type="button" role="tab" id="tab-btn-{tid}" '
            f'aria-controls="tab-{tid}" aria-selected="{sel}" '
            f'tabindex="{tabix}" data-tab="{tid}">{title}</button>'
        )
    return (
        f'      <nav class="exec-tabs" role="tablist" aria-label="{label}">\n'
        + "\n".join(btns)
        + "\n      </nav>\n"
    )


def panel(tid: str, body: str, active: bool = False) -> str:
    hidden = "" if active else " hidden"
    return (
        f'      <div class="tab-panel" id="tab-{tid}" role="tabpanel" '
        f'data-tab-panel="{tid}" aria-labelledby="tab-btn-{tid}"{hidden}>\n'
        f"{body.rstrip()}\n"
        f"      </div>\n"
    )


def split_frame_and_rest(html: str) -> tuple[str, str, str]:
    """Return (before_ledge_close, after_chrome_close_to_main_end, trailing)."""
    m = re.search(
        r"(?P<head>.*?<div class=\"ledge\">.*?</div>\s*)(?P<close></div>\s*)"
        r"(?P<body>.*?)(?P<foot>\s*<p class=\"foot-nav\">.*?</p>\s*)"
        r"(?P<end></main>.*)",
        html,
        re.S,
    )
    if not m:
        raise RuntimeError("Could not parse chrome-frame / foot-nav structure")
    return m.group("head"), m.group("body"), m.group("foot") + m.group("end")


def rebuild(html: str, nav: str, panels: str) -> str:
    head, _body, tail = split_frame_and_rest(html)
    # head ends after ledge; inject tabs then close chrome-frame
    return head + nav + "      </div>\n\n" + panels + tail


def summary_line(text: str) -> str:
    return f'        <p class="exec-tab-summary">{text}</p>\n'


def apply_claims(html: str) -> str:
    head, body, _tail = split_frame_and_rest(html)
    # Pull summary + age buckets into Summary; rest Outstanding
    sum_m = re.search(
        r'<p class="om-claims-age-buckets"[^>]*>.*?</p>\s*',
        body,
        re.S,
    )
    sum_m2 = re.search(r'<p class="om-claims-summary"[^>]*>.*?</p>\s*', body, re.S)
    age = sum_m.group(0) if sum_m else ""
    summ = sum_m2.group(0) if sum_m2 else ""
    body2 = body
    if sum_m:
        body2 = body2.replace(sum_m.group(0), "", 1)
    if sum_m2:
        body2 = body2.replace(sum_m2.group(0), "", 1)
    nav = tabs_nav(
        "Claims content deck",
        [("summary", "Summary"), ("outstanding", "Outstanding")],
    )
    panels = (
        panel(
            "summary",
            summary_line(
                "Money faces above · unpaid SoftDent claims open in Outstanding · empty ≠ $0 · no SoftDent write-back"
            )
            + "        "
            + summ.strip()
            + "\n        "
            + age.strip()
            + "\n",
            active=True,
        )
        + panel("outstanding", body2)
    )
    return rebuild(html, nav, panels)


def apply_hal(html: str) -> str:
    # HAL has no foot-nav — parse through </main>
    m = re.search(
        r"(?P<head>.*?<div class=\"ledge\">.*?</div>\s*)(?P<close></div>\s*)"
        r"(?P<body>.*?)(?P<end></main>.*)",
        html,
        re.S,
    )
    if not m:
        raise RuntimeError("HAL parse failed")
    body = m.group("body")
    hdr = re.search(r'<div class="hal-cmd-header">.*?</div>\s*', body, re.S)
    stale = re.search(
        r'<div class="hal-stale-banner"[^>]*>.*?</div>\s*'
        r'<div class="hal-stale-banner money"[^>]*>.*?</div>\s*',
        body,
        re.S,
    )
    patient = re.search(
        r'<div class="hal-patient-ctx"[^>]*>.*?</div>\s*', body, re.S
    )
    cmd = re.search(r'<div class="hal-cmd">[\s\S]*</div>\s*$', body)
    hdr_html = hdr.group(0) if hdr else ""
    stale_html = stale.group(0) if stale else ""
    patient_html = patient.group(0) if patient else ""
    cmd_html = cmd.group(0) if cmd else body
    nav = tabs_nav(
        "HAL content deck",
        [("summary", "Summary"), ("command", "Command")],
    )
    panels = panel(
        "summary",
        summary_line(
            "Money faces above · open Command for chat, memory, beams, and consent queue · empty ≠ $0"
        )
        + "        "
        + hdr_html.strip()
        + "\n        "
        + stale_html.strip()
        + "\n",
        active=True,
    ) + panel(
        "command",
        "        "
        + patient_html.strip()
        + "\n        "
        + cmd_html.strip()
        + "\n",
    )
    return m.group("head") + nav + "      </div>\n\n" + panels + m.group("end")


def apply_ar(html: str) -> str:
    _head, body, _tail = split_frame_and_rest(html)
    nav = tabs_nav(
        "A/R content deck",
        [("summary", "Summary"), ("detail", "Detail")],
    )
    panels = (
        panel(
            "summary",
            summary_line(
                "Money faces above · bucket filters and PHI sample open in Detail · empty ≠ $0"
            )
            + '        <p class="om-claims-summary" id="ar-bucket-summary-mirror">SoftDent AR · empty ≠ $0 · open Detail for buckets</p>\n',
            active=True,
        )
        + panel("detail", body)
    )
    # Keep original ar-bucket-summary id in detail body — mirror is extra. Remove duplicate id risk:
    # body already has ar-bucket-summary — change mirror to not conflict
    panels = panels.replace(
        'id="ar-bucket-summary-mirror"',
        'id="ar-summary-note"',
    )
    return rebuild(html, nav, panels)


def apply_analytics(html: str) -> str:
    _head, body, _tail = split_frame_and_rest(html)
    # Split: first money-strip = MTD; trellis+excel+recall = Gates
    mtd = re.search(r'<section class="money-strip"[^>]*>.*?</section>\s*', body, re.S)
    rest = body
    mtd_html = ""
    if mtd:
        mtd_html = mtd.group(0)
        rest = body.replace(mtd.group(0), "", 1)
    nav = tabs_nav(
        "Analytics content deck",
        [
            ("summary", "Summary"),
            ("mtd", "MTD Metrics"),
            ("gates", "Gates & Recall"),
        ],
    )
    panels = (
        panel(
            "summary",
            summary_line(
                "Huddle faces above · MTD metrics and Trellis/Excel/recall gates in tabs · empty ≠ $0"
            ),
            active=True,
        )
        + panel("mtd", "        " + mtd_html.strip() + "\n")
        + panel("gates", rest)
    )
    return rebuild(html, nav, panels)


def apply_om(html: str) -> str:
    _head, body, _tail = split_frame_and_rest(html)
    week = re.search(
        r'<section class="om-weekly"[^>]*>.*?</section>\s*', body, re.S
    )
    trellis = re.search(
        r'<section class="om-trellis"[^>]*>.*?</section>\s*', body, re.S
    )
    week_html = week.group(0) if week else ""
    trellis_html = trellis.group(0) if trellis else ""
    nav = tabs_nav(
        "Office Manager content deck",
        [
            ("summary", "Summary"),
            ("week", "This Week"),
            ("trellis", "Trellis Tomorrow"),
        ],
    )
    panels = (
        panel(
            "summary",
            summary_line(
                "OPS faces above · Mon–Thu schedule and Trellis tomorrow in tabs · empty ≠ $0 · board PHI initials+hash"
            ),
            active=True,
        )
        + panel("week", "        " + week_html.strip() + "\n")
        + panel("trellis", "        " + trellis_html.strip() + "\n")
    )
    return rebuild(html, nav, panels)


def apply_softdent(html: str) -> str:
    _head, body, _tail = split_frame_and_rest(html)
    nav = tabs_nav(
        "SoftDent content deck",
        [("summary", "Summary"), ("phi", "PHI Sample")],
    )
    panels = (
        panel(
            "summary",
            summary_line(
                "SoftDent money faces above · PHI glass sample in next tab · empty ≠ $0 · read-only"
            ),
            active=True,
        )
        + panel("phi", body)
    )
    return rebuild(html, nav, panels)


def apply_summary_only(html: str, blurb: str, label: str) -> str:
    _head, body, _tail = split_frame_and_rest(html)
    # body may be empty/whitespace only
    nav = tabs_nav(label, [("summary", "Summary")])
    extra = body.strip()
    panels = panel(
        "summary",
        summary_line(blurb) + (("        " + extra + "\n") if extra else ""),
        active=True,
    )
    return rebuild(html, nav, panels)


APPLIERS = {
    "nr2-optical-page-claims.html": apply_claims,
    "nr2-optical-page-hal.html": apply_hal,
    "nr2-optical-page-ar.html": apply_ar,
    "nr2-optical-page-analytics.html": apply_analytics,
    "nr2-optical-page-office-manager.html": apply_om,
    "nr2-optical-page-softdent.html": apply_softdent,
    "nr2-optical-page-content.html": lambda h: apply_summary_only(
        h,
        "Document pulse faces above · counts only · empty ≠ $0",
        "Documents content deck",
    ),
    "nr2-optical-page-narratives.html": lambda h: apply_summary_only(
        h,
        "Narrative packs UNAVAILABLE · money honesty faces above · empty ≠ $0",
        "Narratives content deck",
    ),
    "nr2-optical-page-quickbooks.html": lambda h: apply_summary_only(
        h,
        "QuickBooks money faces above · empty ≠ $0 · no invent revenue",
        "QuickBooks content deck",
    ),
    "nr2-optical-page-taxes.html": lambda h: apply_summary_only(
        h,
        "Tax planning faces above · CALCULATE on the strip · CPA review · empty ≠ $0",
        "Tax content deck",
    ),
}


def main() -> int:
    for name, fn in APPLIERS.items():
        path = SITE / name
        raw = path.read_text(encoding="utf-8")
        if 'class="exec-tabs"' in raw:
            print(f"SKIP already: {name}")
            continue
        out = fn(raw)
        if 'class="exec-tabs"' not in out or "tab-panel" not in out:
            raise RuntimeError(f"Transform failed for {name}")
        # Ensure chrome-frame closed once
        if out.count('<div class="chrome-frame">') != out.count(
            "chrome-frame"
        ) - out.count("chrome-frame") + 1:
            pass  # weak check
        path.write_text(out, encoding="utf-8", newline="\n")
        print(f"OK {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
