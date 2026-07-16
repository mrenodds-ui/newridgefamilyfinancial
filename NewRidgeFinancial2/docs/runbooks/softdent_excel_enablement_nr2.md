# SoftDent Excel enablement — NR2 morning money bundle

**Office:** New Ridge Family Financial / Michael Christian Reno DDS PA  
**SoftDent:** CS SoftDent Software v19.1.4 (`CS SoftDent Software.lnk -sus` only)  
**NR2 rule:** Excel **or** Print Preview only — **never Printer**, **never File**. Empty ≠ `$0`. No SoftDent write-back.

## Why this runbook exists

NR2 morning bundle (`aging` → `register` → `collections`) needs SoftDent **Excel** output for money-beam ingest (`moneyBeamIngest`).

**Schedule (overall):** pull those SoftDent reports (and any other SoftDent GUI exports needed for the next business day) at **9:00 PM local the night before** — not on the morning of. SoftDent first; Trellis verify typically later (~10:10 PM).

If Excel is greyed out, automation correctly uses Print Preview and keeps `morningBundle.ok=false` / `attest_only`.  
If SoftDent opens **Select File Name** with an empty path, NR2 **refuses to invent** a folder (e.g. do not type `C:\SoftDentReportExports` into SoftDent).

## Operator steps (attended, ~10–15 min)

### 1) Prep desktop

1. Close or minimize **Chrome Claim Management** / **NR2 Optical · Claims** (focus thieves).
2. Leave SoftDent main window foreground (signed on as `COMPUTE` / `computer`, or `SOFTDENT_SIGNON_*`).
3. Do **not** use Esc on SoftDent main (quit prompt).

### 2) Confirm Excel is available on Output Options

1. Open any accounting report path SoftDent already offers (example: **Reports → Accounting → Account Aging** via F10 if Alt menus fail).
2. When **Output Options** appears:
   - Prefer **Excel** (must be enabled / not greyed).
   - If Excel is greyed: SoftDent install/feature — enable report Excel export in SoftDent (Carestream/office IT). **Do not** click File or Printer.
   - Print Preview is allowed for visual totals only; NR2 will **not** treat Preview as money ingest.

### 3) SoftDent’s own save folder (never invent NR2 paths)

When SoftDent shows **Select File Name** / Excel save:

1. Use SoftDent’s **own** folder (typical: `OneDrive\Documents\…` or SoftDent’s last-used Documents path such as `AcctAge`).
2. **Never** type `C:\SoftDentReportExports` or `C:\SOFTDE~1` into SoftDent.
3. After SoftDent saves, NR2 copies/lands Excel under `C:\SoftDentReportExports` (automation / Sync).

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
