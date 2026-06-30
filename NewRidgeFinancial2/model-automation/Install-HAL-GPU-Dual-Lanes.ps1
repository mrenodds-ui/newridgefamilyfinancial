<#
.SYNOPSIS
  Build and pin HAL dual GPU lanes: hal-chat:8b + hal-helper:14b on 16 GB VRAM.

.DESCRIPTION
  Pulls deepseek-r1:8b and queen3:14b, creates capped-context HAL tags, and pins both
  resident. Use -IncludeReasoning to also warm mistral-small3.1:24b-fast (swaps VRAM).
#>
[CmdletBinding()]
param(
    [string]$OllamaHost = "http://127.0.0.1:11434",
    [string]$ChatTag = "hal-chat:8b",
    [string]$HelperTag = "hal-helper:14b",
    [string]$ReasoningTag = "mistral-small3.1:24b-fast",
    [switch]$IncludeReasoning,
    [string]$OllamaExe = "C:\Users\mreno\AppData\Local\Programs\Ollama\ollama.exe"
)

$ErrorActionPreference = "Stop"
$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptRoot
$warmScript = Join-Path $scriptRoot "Keep-HAL-Models-Warm.ps1"

$ollama = if (Test-Path $OllamaExe) { $OllamaExe } else { "ollama" }

function Ensure-BaseModel {
    param([string]$Tag)
    $listed = & $ollama list 2>$null | Select-String -Pattern "^\s*$([regex]::Escape($Tag))\s"
    if ($listed) {
        Write-Host "$Tag already installed - skipping pull." -ForegroundColor DarkGray
        return
    }
    Write-Host "Pulling $Tag ..." -ForegroundColor Cyan
    & $ollama pull $Tag
    if ($LASTEXITCODE -ne 0) { throw "ollama pull $Tag failed with exit code $LASTEXITCODE" }
}

function New-HalTag {
    param(
        [string]$Tag,
        [string]$Modelfile
    )
    if (-not (Test-Path $Modelfile)) {
        throw "Modelfile not found: $Modelfile"
    }
    Write-Host "Creating $Tag from $Modelfile ..." -ForegroundColor Cyan
    & $ollama create $Tag -f $Modelfile
    if ($LASTEXITCODE -ne 0) { throw "ollama create $Tag failed with exit code $LASTEXITCODE" }
}

Ensure-BaseModel "deepseek-r1:8b"
Ensure-BaseModel "queen3:14b"
New-HalTag -Tag $ChatTag -Modelfile (Join-Path $scriptRoot "Modelfile.hal-chat-8b")
New-HalTag -Tag $HelperTag -Modelfile (Join-Path $scriptRoot "Modelfile.hal-helper-14b")

Write-Host "Pinning GPU resident models ..." -ForegroundColor Green
if ($IncludeReasoning) {
    & $warmScript -Models @($ChatTag, $HelperTag) -IncludeReasoningLanes
} else {
    & $warmScript -Models @($ChatTag, $HelperTag)
}
if ($LASTEXITCODE -ne 0) { throw "Keep-HAL-Models-Warm failed with exit code $LASTEXITCODE" }

Write-Host "`nLoaded models:" -ForegroundColor Green
& $ollama ps

Write-Host "`nHAL GPU layout:" -ForegroundColor Yellow
Write-Host "  Chat (GPU):         $ChatTag (from deepseek-r1:8b, num_ctx 3072)"
Write-Host "  Helper (GPU):       $HelperTag (from queen3:14b, num_ctx 2048)"
Write-Host "  Reasoning (demand): $ReasoningTag (load for plans/accounting review)"
Write-Host "Update complete. Restart the desktop app if it is already open." -ForegroundColor Green
