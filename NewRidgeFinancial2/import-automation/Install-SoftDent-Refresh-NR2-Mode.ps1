# Enable NR2-primary SoftDent refresh mode (skip legacy dashboard port 8787 gates).
[CmdletBinding()]
param(
    [string]$LegacyEnvPath = 'C:\New folder\.env',
    [string]$Nr2RepoRoot = 'C:\NewRidgeFamilyFinancial'
)

$ErrorActionPreference = 'Stop'

$entries = [ordered]@{
    NR2_PRIMARY = '1'
    NEWRIDGE_NR2_ROOT = $Nr2RepoRoot
}

if (!(Test-Path -LiteralPath $LegacyEnvPath)) {
    New-Item -ItemType File -Path $LegacyEnvPath -Force | Out-Null
}

$lines = @(Get-Content -LiteralPath $LegacyEnvPath -ErrorAction SilentlyContinue)
foreach ($name in $entries.Keys) {
    $value = [string]$entries[$name]
    $pattern = "^\s*$([regex]::Escape($name))\s*="
    $line = "$name=$value"
    $index = [array]::FindIndex($lines, [Predicate[string]] { param($row) $row -match $pattern })
    if ($index -ge 0) {
        $lines[$index] = $line
    } else {
        if ($lines.Count -gt 0 -and $lines[-1].Trim()) { $lines += '' }
        $lines += $line
    }
}

Set-Content -LiteralPath $LegacyEnvPath -Value $lines -Encoding UTF8
Write-Host "Updated $LegacyEnvPath with NR2_PRIMARY=1 and NEWRIDGE_NR2_ROOT=$Nr2RepoRoot" -ForegroundColor Green
Write-Host 'SoftDent 45-minute refresh will now pass when NR2 import bundle is ready (legacy dashboard API checks skipped).' -ForegroundColor Cyan
