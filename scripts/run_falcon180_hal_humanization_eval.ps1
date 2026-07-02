<#
.SYNOPSIS
  Run Falcon 180B HAL humanization evaluation (pull model if needed, collect samples, judge).

.EXAMPLE
  powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_falcon180_hal_humanization_eval.ps1

.EXAMPLE
  powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_falcon180_hal_humanization_eval.ps1 -CollectSamplesOnly
#>
[CmdletBinding()]
param(
    [switch]$CollectSamplesOnly,
    [switch]$SkipPull,
    [string]$OllamaUrl = 'http://127.0.0.1:11434'
)

$ErrorActionPreference = 'Stop'
$Root = Split-Path $PSScriptRoot -Parent
Push-Location $Root

try {
    if (-not $SkipPull) {
        $tags = Invoke-RestMethod -Uri "$OllamaUrl/api/tags" -TimeoutSec 30
        $hasFalcon = @($tags.models | ForEach-Object { $_.name }) -match '^falcon:180b'
        if (-not $hasFalcon) {
            Write-Host 'Pulling falcon:180b (~101 GB). This may take a while...'
            ollama pull falcon:180b
        } else {
            Write-Host 'falcon:180b already present.'
        }
    }

    $pyArgs = @('run_falcon180_hal_humanization_eval.py', '--base-url', $OllamaUrl, '--rebuild-context')
    if ($CollectSamplesOnly) {
        $pyArgs += '--collect-samples'
    } else {
        $pyArgs += '--collect-samples'
    }

    python @pyArgs
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    Write-Host 'Done. See falcon180_hal_humanization_report.md'
} finally {
    Pop-Location
}
