# SoftDent Excel Enablement — BLOCKED (attended probe 2026-07-17)

**Date:** 2026-07-17  
**Consult:** `MOONSHOT_WHATS_NEXT_AFTER_SOFTDENT_GREY_EXCEL_UNIVERSAL_2026-07-17.md`  
**Operator:** continue (re-probe)  
**Runbook:** `docs/runbooks/softdent_excel_enablement_nr2.md`

## Verdict

**Cannot complete morning-bundle Excel refresh.** SoftDent Output Options still shows **Excel greyed** (`IsWindowEnabled=False`) on Account Aging and Collection Summary. SoftDent is **intentionally blocking extractable pulls** across Output Options reports; only Print Preview is optical-allowed. Automation cancelled Output Options (never Printer OK). Prior `morningBundle.ok=true` (aging+register Excel paths) left intact — did **not** re-run `morning_bundle_attended`.

## Live probes (COMPUTE signed on)

| When | Report | Excel |
|------|--------|-------|
| ~05:48 local | Account Aging | **disabled** |
| ~05:48 local | Collection Summary | **disabled** |
| ~05:59 local (re-probe after continue) | Account Aging | **disabled** |
| ~05:59 local | Collection Summary | **disabled** |

Quitting Excel earlier did **not** un-grey. SoftDent-side pull block, not “Excel busy.”

## What Cursor did

1. SoftDent ready / focused  
2. Opened Output Options via win32 menu for aging + collections  
3. Enumerated radios (enabled/checked)  
4. **Cancel** only — never Enter on Printer  
5. Documented block — no invented Excel drops / dollars / Preview money invent  

## Operator / Carestream next (required)

1. SoftDent install/feature: enable report **Excel** export so Output Options Excel is clickable (can apply across all Output Options reports).  
2. Confirm on Account Aging: Excel enabled, not greyed.  
3. Tell Cursor: **Excel is clickable — run morning bundle**  
4. Cursor then runs:  
   `.\.venv\Scripts\python.exe scripts/morning_bundle_attended.py --yes --refresh-close`

Until then: Preview optical-only · empty ≠ `$0` · `failed:["collections"]` · Force Close stays laser-gated.

## Backlog (unchanged)

2. ERA real `.835` drop  
3. Trellis withBenefits ~2026-07-20  
4. Shadow Day 30 attestation prep  
