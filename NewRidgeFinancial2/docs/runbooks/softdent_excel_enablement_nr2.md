# SoftDent Excel enablement — NR2 morning money bundle

**Office:** New Ridge Family Financial / Michael Christian Reno DDS PA  
**SoftDent:** CS SoftDent Software v19.1.4 (`CS SoftDent Software.lnk -sus` only)  
**NR2 rule:** Excel **or** Print Preview only — **never Printer**, **never File**. Empty ≠ `$0`. No SoftDent write-back.

## Why this runbook exists

NR2 morning bundle (`aging` → `register` → `collections`) needs SoftDent **Excel** output for money-beam ingest (`moneyBeamIngest`).

**Schedule (overall):** pull those SoftDent reports (and any other SoftDent GUI exports needed for the next business day) at **9:00 PM local the night before** — not on the morning of. SoftDent first; Trellis report pull **1:00 AM** Mon–Thu.

If Excel is greyed out, SoftDent is **intentionally blocking extractable data pulls** (Excel / file-style export). That gate can apply **across all SoftDent reports** that open the shared **Output Options** dialog — not only collections or morning-bundle reports. The only SoftDent-allowed path then is **Print Preview** for optical / visual reading. NR2 must treat Preview as read-with-eyes only — never invent dollars from Preview, never fall through to Printer or File, and keep money-beam ingest / `morningBundle` Excel paths empty ≠ `$0` until SoftDent itself re-enables Excel.

Carestream SoftDent Help documents the same Output Options pattern for running reports (select output, then OK) and documents Excel as an Output Option when SoftDent offers it for a report family (registers, account lists, recall, user-selected, provider daily summary, etc.). See Carestream SoftDent Help: [Running Reports](https://help.carestreamdental.com/rh/web/server/SoftDent/projects_responsive/DE1055_SD_Wkbk/Running_Reports.htm) and Excel-export notes under Accounting / Account / Recall / User-Selected report topics on help.carestreamdental.com. When Excel is grey on this practice’s SoftDent, SoftDent is denying the extract path; Preview remains the optical stop-gap.

**Select File Name** for every Excel report (when Excel is clickable) is forced to `C:\SoftDentReportExports` — never OneDrive, never SoftDent’s legacy `C:\SoftDent\softdentexportreports`.

## Operator steps (attended, ~10–15 min)

### 1) Prep desktop

1. Close or minimize **Chrome Claim Management** / **NR2 Optical · Claims** (focus thieves).
2. Leave SoftDent main window foreground (signed on as **Dr** admin via `SOFTDENT_SIGNON_*`; prefer Dr over COMPUTE for Excel Output Options).
3. Do **not** use Esc on SoftDent main (quit prompt).

### 2) Confirm Excel is available on Output Options

1. Open any accounting report path SoftDent already offers (example: **Reports → Accounting → Account Aging** via F10 if Alt menus fail).
2. When **Output Options** appears:
   - Prefer **Excel** (must be enabled / not greyed).
   - If Excel is greyed: SoftDent is **blocking data-pull actions** by design for that Output Options surface — and the same grey can appear on **any** SoftDent report that uses Output Options. Only **Print Preview** (optical read). Enable Excel in SoftDent (Carestream/office IT) when extractable drops are required. **Do not** click File or Printer.
   - Also check **System → Printing Preferences → Default Path for Excel Files** → `C:\SoftDentReportExports` (short `C:\SOFTDE~1` is OK). Quitting a stuck Excel process alone does **not** un-grey the radio when SoftDent has Excel disabled at feature level (probed 2026-07-17).
   - Print Preview = visual totals only; NR2 will **not** treat Preview as money ingest.

### 3) SoftDentReportExports save folder

When SoftDent shows **Select File Name** / Excel save:

1. SoftDent **Select File Name** for **all** Excel reports must use `C:\SoftDentReportExports`. Override with `SOFTDENT_SELECT_FILE_FOLDER` only if SoftDent requires a different path.
2. **Never** leave SoftDent on OneDrive or SoftDent’s legacy `C:\SoftDent\softdentexportreports`.
3. After SoftDent saves, NR2 canonicalizes / Syncs Excel under `C:\SoftDentReportExports`.

### 4) Attended morning-bundle re-run gate

After Excel is clickable and SoftDent has a real folder:

1. Tell Cursor/HAL: **approve** / **continue** for attended morning bundle.
2. Automation runs: aging → register → collections (Excel preferred).
3. Success gate:
   - `periodCloseStatus.morningBundle.ok == true` (or honest partial with Excel paths)
   - Files present under `C:\SoftDentReportExports` (or NR2 ingest paths)
   - `emptyNotZero` still true (no invented `$0`)
   - `forceCloseAvailable` stays laser-gated (GREEN+MATCH alone does **not** flip Force Close)

### 5) If it still fails

| Symptom | Action |
|---------|--------|
| Excel greyed | SoftDent feature/license — Preview only until Excel enabled |
| Select File Name empty path | Pick SoftDent’s Documents folder manually once; do not invent paths in code |
| Waiting for printer… | Cancel (Alt+C); choose Excel or Print Preview |
| Claim Management steals focus | Minimize Chrome Claims; re-run attended |

## HAL / staff one-liner

Ask HAL: “SoftDent report pull” / `policy:softdent-report-pull` — same Excel-or-Preview hard rules, Claim Management focus thieves, Excel-greyed → Preview with empty ≠ `$0`.

## Related code (do not invent new modules)

- `NewRidgeFinancial2/softdent_gui_export.py`
- `NewRidgeFinancial2/hal_brain_tools.py` → `softdent_export_morning_bundle` (`excelEnablementGate`)
- `NewRidgeFinancial2/softdent_report_pull.py`
- `NewRidgeFinancial2/desk_smoke.py` (Force Close laser-gated)
- `NewRidgeFinancial2/daily_closeout.py` → `period_close_status.morningBundle`
- Optional QB staff drops: `docs/runbooks/qb_ap_payroll_inbox_drop_nr2.md`
- Trellis AM proof after nightly scrape: `scripts/prove_trellis_withbenefits_am.py`
