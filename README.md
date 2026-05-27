# New Ridge Family Financial
Single-page application (SPA) for financial analysis of New Ridge Family Dental. All logic runs in-browser. No backend is present.
- No writes to production databases. No backend/database is present.
- SPA runs on http://localhost:5173 by default.
- React, TypeScript, Vite
- No database is used. All data is in-browser.
If you are developing or running the SPA, follow the onboarding instructions for Node.js and Docker.
No backend development is required.
The SPA does not require a backend or API server.
- (removed)
- (removed)
- (removed)
## Run Locally

```sh
npm install --prefix frontend
npm run dev --prefix frontend
```

Open: <http://localhost:5173/app>
## CI/CD Host Header Validation

If CI/CD or E2E tests fail due to host header validation, ensure your test runner and proxy are forwarding the correct Host header. Some security middleware may block requests with unexpected Host values.
# New Ridge Family Financial

Server-only FastAPI application for financial analysis of New Ridge Family Dental.

## Scope

- No login page.
- No patient-facing workflows.
- Read-only SoftDent and QuickBooks imports.
- No writes to production databases.
- Local host binding by default: 127.0.0.1.


## Tech Stack

- Python, FastAPI, Jinja2
- Chart.js
- SQLite cache database
- Lightweight built-in analytics pipeline (pandas-ready upgrade path)

## Windows/Node-gyp/Visual Studio Note

If you are developing or running the backend on Windows, you **must** install Visual Studio with the "Desktop development with C++" workload to build native modules (e.g., better-sqlite3). Download from:
https://visualstudio.microsoft.com/visual-cpp-build-tools/

If you only need to run the backend and not develop, consider using WSL or a Linux VM to avoid file lock and build issues.

## Pandas Limitation

Pandas is not installed by default due to missing wheels on Windows without build tools. If you need pandas, install it after ensuring Visual Studio is present, or use a platform with prebuilt wheels.

## CORS/Proxy/Frontend Integration

The frontend expects the backend at `http://localhost:4000` (or as set in `.env`). If you change ports, update both frontend and backend `.env` files. Ensure CORS is enabled for the frontend origin.

## Service Worker Caching

The service worker only caches the app shell, not API data, for security. If you add offline API caching, ensure no sensitive data is cached.

## Project Structure

- `app/main.py`: FastAPI entrypoint
- `app/config/settings.py`: `.env` configuration
- `app/db/`: CSV readers and SQLite cache
- `app/services/`: KPI, reconciliation, HAL advisor, reports
- `app/routers/`: dashboard and feature routes
- `app/templates/`: Jinja2 pages
- `app/static/`: CSS/JS assets

## Data Inputs

### QuickBooks CSV

Use exported reports such as:

- Profit and Loss by Month
- Deposit/Income report

Expected columns:

- `Date` or `Month`
- `Account` or `Account Name`
- `Amount`

### SoftDent CSV

Use read-only exports.

Expected columns:

- `Date` or `Month`
- `Metric` or `Measure`
- `Amount`
- `Provider`, `Category` optionally

## Financial Window And Refresh

- The program automatically uses a rolling 5-year financial window (`FINANCIAL_LOOKBACK_YEARS=5`).
- Financial cache is recomputed daily when the app is accessed (`FINANCIAL_DAILY_REFRESH_ENABLED=true`).
- Raw and KPI cache tables are rebuilt on refresh so storage does not grow endlessly from repeated daily recomputes.

Source report auto-pull runs before each recompute:

- `SOFTDENT_AUTO_PULL_ENABLED=true` with `SOFTDENT_SOURCE_DIR` (or `SOFTDENT_SENSEI_DATASYNC_ROOT`) to ingest SoftDent CSV files automatically.
- `QUICKBOOKS_AUTO_PULL_ENABLED=true` with `QUICKBOOKS_SOURCE_DIR` to ingest QuickBooks CSV files automatically.
- Pull activity can be checked at `/api/reports/pull-status`.

## Pandas Note

This build runs on Python 3.14 in an environment without Visual Studio build tools, so pandas wheels are not currently available. The analytics pipeline is implemented with standard-library parsers and keeps the same KPI/reconciliation outputs. If pandas wheels become available in your runtime, readers can be swapped to pandas-based loaders without route/template changes.

## Run Locally (Windows Server)

```powershell
cd E:\NewRidgeFamilyFinancial
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --host 127.0.0.1 --port 8095 --reload
```

Open: <http://127.0.0.1:8095>

## CI Test Command

Use this as the regular CI test command:

```powershell
python -m pytest app/tests -q
```

This now includes:

- A route-wiring smoke gate via `app/tests/test_ci_route_wiring.py`, which executes `scripts/smoke_all_routes.py` and fails CI automatically if any page/API wiring regresses.
- A focused ingest gate via `app/tests/test_ci_softdent_ingest_check.py`, which executes `scripts/focused_new_file_ingest_check.py` and fails CI if controlled new-file SoftDent ingest no longer changes pull counters and downstream KPI deltas as expected.

For low-noise structured diagnostics in CI logs, run:

```powershell
python scripts/run_ci_gates.py
```

This writes a JSON report to `scripts/ci_gate_report.json` (configurable with `--output`).

For a quick report-generation sanity check without executing the gate tests, use:

```powershell
python scripts/run_ci_gates.py --skip-gates --output scripts/ci_gate_report.quick.json
```

For a full rebuild receipt artifact (refresh + tests + gates), use:

```powershell
python scripts/write_rebuild_receipt.py --output scripts/rebuild_receipt.json
```

For a fast artifact-creation sanity check only:

```powershell
python scripts/write_rebuild_receipt.py --skip-steps --output scripts/rebuild_receipt.quick.json
```

## Key Pages

- `/` Dashboard
- `/softdent` SoftDent Analysis and import
- `/claims` Outstanding dental claims queue (daily refresh)
- `/accounts-receivable` All-accounts receivable view (daily refresh)
- `/quickbooks` QuickBooks Analysis and import
- `/reconciliation` Reconciliation table
- `/trends` Trend charts
- `/ebitda` EBITDA valuation page (daily estimate)
- `/hal9000` HAL 9000 dedicated question-and-monitoring console
- `/reports` Monthly and DSO-style summaries

## HAL 9000 Advisor Rules

- Uses only calculated KPI data.
- Does not invent numbers.
- Classifies findings as green/yellow/red.
- Returns direct practice-management recommendations.
- Applies all 15 HAL phases from New Ridge Portal in financial-only scope.

## Security Notes

- Keep `.env` credentials out of source control.
- Do not expose the app to LAN unless explicitly changed.
- Keep all integrations read-only.
- Session cookies, if added later, should be `HttpOnly` and `Secure`; the browser app does not store auth tokens, API keys, or session IDs in `localStorage`.

### Content Security Policy

The backend sends a strict CSP by default with same-origin script loading, no object/embed content, and no framing. The app still allows `style-src 'unsafe-inline'` because the current React UI uses inline styles extensively. That exception is intentional and should be removed only after the UI is moved to CSS classes or CSS variables.

## SQLite, Telemetry, Redis, And Hardening

- SQLite remains the durable cache + analytics store (`SQLITE_PATH`) and now also stores request telemetry.
- Telemetry controls:

  - `TELEMETRY_ENABLED=true|false`
  - `TELEMETRY_MAX_ROWS=50000` (retention cap)

- Optional Redis runtime integration:

  - `REDIS_ENABLED=true|false`
  - `REDIS_URL=redis://127.0.0.1:6379/0`
  - Redis health is reported in `/api/health`.

- Hardened runtime controls:

  - `HARDENED_TRUSTED_HOSTS=127.0.0.1,localhost`
  - `HARDENED_SECURITY_HEADERS_ENABLED=true|false`
  - `HARDENED_HTTPS_REDIRECT=true|false`
  - `HARDENED_HSTS_ENABLED=true|false`

## SoftDent Read-Only Policy

- `SOFTDENT_READ_ONLY_MODE=true` blocks any mutation-style behavior by policy.
- `SOFTDENT_IMPORT_ONLY_MODE=true` limits SoftDent use to ingest and analysis.
- `SOFTDENT_ENFORCE_READ_ROOT=true` enforces that SoftDent files are loaded only from approved roots.
- Approved roots include `SOFTDENT_READ_ROOT`, `SOFTDENT_IMPORT_DIR`, and optional `SOFTDENT_SENSEI_DATASYNC_ROOT`.

## Browser-Native Frontend Architecture

The repository now includes a browser-native client in `frontend/` with this stack:

- IndexedDB via Dexie (`frontend/src/db.ts`) with typed tables, versioned schema, and CRUD helpers.
- TanStack Query (`frontend/src/queryClient.ts`) for server-state caching and query key discipline.
- Comlink (`frontend/src/workers/jsonWorker.ts` and `frontend/src/workers/jsonWorkerClient.ts`) for the KPI parsing worker.
- BroadcastChannel (`frontend/src/browser/crossTabSync.ts`) for cross-tab cache invalidation after browser-side writes and refreshes.
- Web Locks API (`frontend/src/browser/webLocks.ts`) around IndexedDB writes so multiple tabs do not run the same write-heavy job at once.
- Persistent storage requests (`frontend/src/browser/storagePersistence.ts`) so browser-managed cache data is less likely to be evicted.
- Zod validation for external API payloads (`frontend/src/api/schemas.ts`).
- Web Worker parsing for non-trivial payload validation/transforms (`frontend/src/workers/jsonWorker.ts`) with Comlink wrapping.
- A lightweight custom Service Worker app-shell cache (`frontend/public/sw.js`) for offline shell loading without caching API data.
- A web app manifest (`frontend/public/manifest.webmanifest`) so the browser shell can be installed without pretending full offline API support.

### Browser Update Strategy

- The service worker keeps app-shell caching only; API requests stay network-first.
- When a new service worker is installed and waiting, the app shows a `New version available` banner.
- Users can click `Refresh now` to activate the waiting worker (`skipWaiting`) and reload into the latest bundle.
- The app never silently traps users on stale code.

### Sync Conflict And Retry Rules

- KPI snapshot merge policy is `newest timestamp wins` for same-period rows.
- Local refresh retries are queued in IndexedDB (`syncQueue`) when admin refresh fails.
- Queued retries are attempted again when the browser comes back online on a stable connection.
- A manual `Retry queued actions` button is available in the admin dashboard as fallback.
- Conflict behavior and migration compatibility are covered in frontend tests.

### Diagnostics Panel

- Add `?diag=1` to `/app` or `/admin` to enable the developer diagnostics card.
- The panel reports app version, build date, browser info, IndexedDB availability, service worker status, storage persistence, estimated quota, database schema version, last sync time, and queued retry count.
- No secrets, tokens, or credentials are displayed.

### Release Safety Notes

- Browser-local data remains exportable through `Local Backup / Restore`; run a backup before major upgrades.
- IndexedDB schema evolution is versioned in `frontend/src/db.ts` and migration compatibility is tested.
- See `frontend/CHANGELOG.md` for release-facing browser-app changes.

### Migration Boundary

- Existing FastAPI backend still uses SQLite for server-side cache and reporting.
- Browser code does not use SQLite/Redis directly; local persistence is IndexedDB only.
- Redis/telemetry remain backend concerns and are isolated from browser state architecture.
- Workbox is not used yet because the current shell cache is small and the app does not need a broader precache pipeline.
- File System Access and Web Crypto are not added because the app does not yet have a real local file workflow or security need that justifies them.
- Browser API fallbacks are feature-detected in small modules so unsupported browsers can degrade gracefully instead of crashing.

### Frontend Commands

From `frontend/`:

```powershell
npm install
npm run lint
npm run typecheck
npm run test
npm run build
```

After building, FastAPI serves the browser app at:

- `/app`

If the bundle is missing, `/app` returns a setup page with build instructions and does not break other routes.
