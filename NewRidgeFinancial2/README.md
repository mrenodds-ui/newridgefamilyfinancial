# NewRidgeFinancial 2.0

Single-window desktop mission-control program for New Ridge Family Financial.

The legacy program in `_legacy/` is for reference only and is not used here.

## Run

Double-click `StartNewRidgeFinancial2.bat` (repo root), or run:

```powershell
scripts\start_nr2_1966.ps1
```

The launcher opens one desktop app window. It does not start a localhost
server and does not open Chrome.

## Files

```
NewRidgeFinancial2/
  desktop_app.py     single-window pywebview app launcher
  import_sync.py     syncs live SoftDent/QuickBooks exports into import cache
  import_loader.py   reads SoftDent / QuickBooks export files for HAL
  accounting_tools.py  single-source chart of accounts + journal templates (Python)
  accounting_bridge.py journal draft + SQLite posting queue bridge for desktop
  import-manifest.json shared import filename contract (Python + JS)
  local_store.py     local SQLite state store
  site/
    import-loader.js maps import files into dashboard shapes HAL uses
    index.html        desktop app shell
    styles.css        mission-control shell styling
    app.js            internal routing and local app state
    page-views.js     real client-side screens for program pages
    hal-page.js       real HAL Command Center screen
    desktop-bridge.js local file + SQLite bridge
```

## Stop

`StopNewRidgeFinancial2.bat`

## SoftDent / QuickBooks imports (read-only)

In desktop mode, HAL automatically reads local export files from the document-inbox cache:

- `app_data/nr2/document_inbox/softdent/` (dashboard, claims, clinical notes, A/R)
- `app_data/nr2/document_inbox/quickbooks/` (revenue/P&L, expenses, optional A/R)

Override with `SOFTDENT_IMPORT_DIR` or `QUICKBOOKS_IMPORT_DIR` if needed.

On first sync, any files still in the legacy `app/data/imports/` folders are migrated into the document-inbox cache automatically.

When imports are missing, dashboards show empty shells — there is no bundled mock or demo data.

Automation is in `import-automation/`:

- `Sync-HAL-Imports.ps1` — copies approved SoftDent and QuickBooks exports into the document-inbox cache (financial widgets).
- `Sync-HAL-Document-Sources.ps1` — import pull plus Documents page queue sync.
- `Verify-HAL-Readiness.ps1` — pre-flight check for upstream paths and required exports.
- `Register-HAL-Import-Automation.ps1` — registers a Windows scheduled task (import sync every 5 minutes).
- `Register-HAL-Document-Source-Automation.ps1` — registers document-source sync (every 30 minutes).

Default upstream source folders (override in repo `.env`):

- SoftDent: `NR2_SOFTDENT_EXPORT_SOURCE` or `SOFTDENT_SOURCE_DIR` (see `import-manifest.json` defaults)
- QuickBooks: `NR2_QUICKBOOKS_EXPORT_SOURCE` or `QUICKBOOKS_SOURCE_DIR`

After files are copied, ask HAL **"refresh imports"** or restart the app. HAL reads only — nothing is posted or written back to SoftDent or QuickBooks.

HAL's top priority is to monitor the program, place correct import data into the right financial and accounting views, apply accounting and Excel-style review, and recommend the next safe staff action.

## Tests

From `NewRidgeFinancial2/`:

```powershell
python -m unittest discover -s . -p "test_*.py"
node test_import_loader_accounting.mjs
node test_import_diagnostics_node.mjs
node test_month_end_close.mjs
node validate-hal.mjs
node validate-pages.mjs
```

CI runs the same checks via `.github/workflows/validate-nr2.yml`.
