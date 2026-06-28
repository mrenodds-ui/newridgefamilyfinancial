<#
.SYNOPSIS
  Retired launcher for the legacy New Ridge Family Financial program.

.DESCRIPTION
  The legacy program has been archived. Mockup pages are now served only by
  NewRidgeFinancial 2.0 on port 8096.

  Run scripts\start_program_2.ps1 or StartNewRidgeFinancial2.bat instead.
#>
[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$Root = Split-Path $PSScriptRoot -Parent

Write-Host "The legacy New Ridge Family Financial launcher is retired." -ForegroundColor Yellow
Write-Host ""
Write-Host "Mockup pages are now a separate program:" -ForegroundColor Cyan
Write-Host "  NewRidgeFinancial 2.0" -ForegroundColor Green
Write-Host "  Start: $Root\StartNewRidgeFinancial2.bat"
Write-Host "  URL:   http://127.0.0.1:8096/app"
Write-Host ""
Write-Host "Legacy code remains in _legacy/ for reference only."
exit 1
