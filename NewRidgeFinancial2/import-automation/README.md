# HAL Import Automation

This folder automates HAL's read-only import lane for SoftDent and QuickBooks export files.

## Import cache (HAL reads from here)

| System | Default path |
|--------|----------------|
| SoftDent | `app_data/nr2/document_inbox/softdent` |
| QuickBooks | `app_data/nr2/document_inbox/quickbooks` |

Override destinations with `SOFTDENT_IMPORT_DIR` or `QUICKBOOKS_IMPORT_DIR` (see `NewRidgeFinancial2/.env.example`).

Legacy `app/data/imports/` is retired for NR2. `import_sync.py` migrates any remaining files on first sync.

## Upstream export sources

Configure in repo-root `.env`:

```powershell
NR2_SOFTDENT_EXPORT_SOURCE=C:\Path\To\SoftDentExports
NR2_QUICKBOOKS_EXPORT_SOURCE=C:\Path\To\QuickBooksExports
# or
SOFTDENT_SOURCE_DIR=C:\ProgramData\Sensei Gateway Client\DataSync
QUICKBOOKS_SOURCE_DIR=C:\Path\To\QuickBooksExports
```

Default machine paths are listed in `NewRidgeFinancial2/import-manifest.json` under `upstreamRoots`.

## Pre-flight

```powershell
powershell -ExecutionPolicy Bypass -File .\NewRidgeFinancial2\import-automation\Verify-HAL-Readiness.ps1
```

Phase 0 fails when no upstream folder exists for SoftDent or QuickBooks — set `.env` before scheduling sync.

## Financial import sync (widgets / HAL aggregates)

```powershell
powershell -ExecutionPolicy Bypass -File .\NewRidgeFinancial2\import-automation\Sync-HAL-Imports.ps1
```

Watch mode (continuous):

```powershell
powershell -ExecutionPolicy Bypass -File .\NewRidgeFinancial2\import-automation\Sync-HAL-Imports.ps1 -Watch
```

Register scheduled task (every 5 minutes):

```powershell
powershell -ExecutionPolicy Bypass -File .\NewRidgeFinancial2\import-automation\Register-HAL-Import-Automation.ps1
```

## Documents page sync (imports + document queue)

```powershell
powershell -ExecutionPolicy Bypass -File .\NewRidgeFinancial2\import-automation\Sync-HAL-Document-Sources.ps1
```

Register scheduled task (every 30 minutes):

```powershell
powershell -ExecutionPolicy Bypass -File .\NewRidgeFinancial2\import-automation\Register-HAL-Document-Source-Automation.ps1
```

## Pull with readiness check

```powershell
powershell -ExecutionPolicy Bypass -File .\NewRidgeFinancial2\import-automation\Verify-HAL-Readiness.ps1 -Pull
```

## Safety boundary

The automation only copies approved export files into HAL's local document-inbox cache.
It never writes to SoftDent, QuickBooks, payers, clearinghouses, or external services.
