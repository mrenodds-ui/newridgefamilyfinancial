[CmdletBinding()]
param(
    [switch]$Pull,
    [switch]$Quiet
)

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$repoRoot = Split-Path -Parent $projectRoot
$qbImportDir = Join-Path $repoRoot "app_data\nr2\document_inbox\quickbooks"
$sdImportDir = Join-Path $repoRoot "app_data\nr2\document_inbox\softdent"

function Write-Step {
    param([string]$Message, [string]$Color = "Cyan")
    if (-not $Quiet) { Write-Host $Message -ForegroundColor $Color }
}

Write-Step "NewRidgeFinancial 2.0 - Accounting month-end checklist (staff)"
Write-Step "============================================================" "DarkGray"
Write-Host ""

Write-Step "Phase A - SoftDent exports (run in SoftDent before NR2 refresh)" "Yellow"
Write-Host "  1. Run a FINAL daysheet for each day in the current month."
Write-Host "  2. Reports > Practice Management > Collection Reports > Reconciliation Report"
Write-Host "     for the prior month; confirm totals match bank deposits."
Write-Host "  3. Confirm softdent_dashboard_data.json includes current + prior month with collections populated."
Write-Host "  4. Confirm softdent_ar_aging.csv is present and current."
Write-Host ""

Write-Step "Phase A - QuickBooks exports" "Yellow"
Write-Host "  1. Confirm monthly P&L / revenue / expense CSVs are current in:"
Write-Host "     $qbImportDir"
Write-Host "  2. Optional A/R cross-check: export QuickBooks A/R aging to:"
Write-Host "     $(Join-Path $qbImportDir 'quickbooks_ar.csv')"
Write-Host "     (columns: Bucket, Balance)"
Write-Host "  3. Compare SoftDent COLLECTIONS to QuickBooks revenue/deposits - not production to revenue."
Write-Host ""

if ($Pull) {
    Write-Step "Refreshing NR2 import cache..." "Green"
    Push-Location $projectRoot
    try {
        $env:NR2_HAL_FULL_PULL = "1"
        python -c "from practice_source_access import pull_all_practice_sources; pull_all_practice_sources(full=True, scan_resources=False)"
        python sync_document_sources.py
    } finally {
        Pop-Location
    }
}

Write-Step "Phase A - NR2 verification" "Yellow"
Push-Location $projectRoot
try {
    node test_import_loader_accounting.mjs
    if ($LASTEXITCODE -ne 0) { throw "test_import_loader_accounting.mjs failed" }

    $verifyScript = Join-Path $projectRoot "import-automation\_accounting_check_snapshot.mjs"
    node $verifyScript
    if ($LASTEXITCODE -ne 0) { throw "accounting snapshot verification failed" }

    Write-Step ""
    Write-Step "Ask HAL in the desktop app:" "Green"
    Write-Host '  - "Show accounting reconciliation checklist"'
    Write-Host '  - "Work document workbook"'
    Write-Host '  - "Check data quality before recommendations"'
} finally {
    Pop-Location
}

Write-Step ""
Write-Step "Checklist script complete." "Green"
