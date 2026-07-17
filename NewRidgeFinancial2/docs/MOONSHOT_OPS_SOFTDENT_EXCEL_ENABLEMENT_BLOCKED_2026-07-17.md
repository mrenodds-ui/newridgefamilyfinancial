# SoftDent Excel Enablement — BLOCKED (attended probe 2026-07-17)

**Date:** 2026-07-17  
**Consult:** `MOONSHOT_WHATS_NEXT_AFTER_SHADOW_CLOCK_HYGIENE_2026-07-17.md`  
**Operator:** continue  
**Runbook:** `docs/runbooks/softdent_excel_enablement_nr2.md`

## Verdict

**Cannot complete morning-bundle Excel refresh.** SoftDent Output Options still shows **Excel greyed** (`IsWindowEnabled=False`) on both Account Aging and Collection Summary. Automation cancelled Output Options (never Printer OK). Prior `morningBundle.ok=true` (aging+register Excel paths) left intact — did **not** re-run `morning_bundle_attended` (would fail Excel gate / risk Preview-only pollution).

## Live probe (COMPUTE signed on)

| Report | Output Options | Excel | Printer (default) |
|--------|----------------|-------|-------------------|
| Account Aging | open | **disabled** | checked |
| Collection Summary | open | **disabled** | checked |

Also tried: quit running Excel (`Office16\EXCEL.EXE`) — Excel radio **still greyed**. SoftDent-side feature/license, not “Excel busy.”

## What Cursor did

1. SoftDent sign-on ready / focused  
2. Opened Output Options via win32 menu for aging + collections  
3. Enumerated radios (enabled/checked)  
4. **Cancel** only — never Enter on Printer  
5. Documented block — no invented Excel drops / dollars  

## Operator / Carestream next (required)

1. SoftDent install/feature: enable report **Excel** export (Carestream/office IT) so Output Options Excel is clickable.  
2. Confirm on Account Aging: Excel enabled, not greyed.  
3. Tell Cursor: **Excel is clickable — run morning bundle**  
4. Cursor then runs:  
   `.\.venv\Scripts\python.exe scripts/morning_bundle_attended.py --yes --refresh-close`

Until then: Preview-only stays honest · empty ≠ `$0` · `failed:["collections"]` · Force Close stays laser-gated.

## Backlog (unchanged)

2. ERA real `.835` drop  
3. Trellis withBenefits ~2026-07-20  
4. Shadow Day 30 attestation prep  
