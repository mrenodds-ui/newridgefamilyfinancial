<#
.SYNOPSIS
  Build HAL humanization context bundle for Falcon 180B evaluation.

.DESCRIPTION
  Writes falcon180_hal_humanization_context.txt at repo root with:
  - HAL model config, Modelfiles, runtime prompt builders
  - Eval tone spec (qwen_second_opinion_system.txt)
  - hal-manager cognitive pathways
  - Optional: subject model sample responses JSON if present

.EXAMPLE
  powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\build_falcon180_hal_humanization_context.ps1
#>
[CmdletBinding()]
param(
    [int]$MaxChars = 52000,
    [string]$SamplesFile = 'falcon180_hal_subject_samples.json'
)

$ErrorActionPreference = 'Stop'
$Root = Split-Path $PSScriptRoot -Parent
$Nr2 = Join-Path $Root 'NewRidgeFinancial2'
$OutFile = Join-Path $Root 'falcon180_hal_humanization_context.txt'

function Limit-TextLength {
    param([string]$Text, [int]$Limit)
    if ($Text.Length -le $Limit) { return $Text }
    $half = [Math]::Floor($Limit / 2)
    return (
        $Text.Substring(0, $half) +
        "`n`n...[truncated at $Limit chars]...`n`n" +
        $Text.Substring($Text.Length - $half)
    )
}

function Get-FullFileText {
    param([string]$RelPath, [int]$MaxFileChars = 12000)
    $path = Join-Path $Root $RelPath
    if (-not (Test-Path $path)) { return '' }
    $text = Get-Content -Path $path -Raw -Encoding UTF8
    if ($text.Length -gt $MaxFileChars) {
        $text = Limit-TextLength -Text $text -Limit $MaxFileChars
    }
    return "=== $RelPath ===`n$text`n"
}

function Get-LineRangeText {
    param([string]$RelPath, [int]$StartLine, [int]$EndLine)
    $path = Join-Path $Root $RelPath
    if (-not (Test-Path $path)) { return '' }
    $lines = Get-Content -Path $path -Encoding UTF8
    $start = [Math]::Max(1, $StartLine)
    $end = [Math]::Min($lines.Count, $EndLine)
    if ($end -lt $start) { return '' }
    $snippet = ($lines[($start - 1)..($end - 1)] -join "`n")
    return "=== $RelPath (lines $start-$end) ===`n$snippet`n"
}

$sb = [System.Text.StringBuilder]::new()
[void]$sb.AppendLine('HAL HUMANIZATION REVIEW CONTEXT — NewRidgeFinancial 2.0')
[void]$sb.AppendLine("Generated (local): $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')")
[void]$sb.AppendLine('')
[void]$sb.AppendLine('SCOPE: Evaluate HAL AI tone/persona - subject models hal-chat:8b + hal-helper:14b, runtime prompts in hal-core.js and hal-agent.js.')
[void]$sb.AppendLine('')

$chunk = Get-FullFileText -RelPath 'NewRidgeFinancial2/site/data/hal-models.json' -MaxFileChars 6000
[void]$sb.AppendLine($chunk)
$chunk = Get-FullFileText -RelPath 'NewRidgeFinancial2/model-automation/Modelfile.hal-chat-8b' -MaxFileChars 4000
[void]$sb.AppendLine($chunk)
$chunk = Get-FullFileText -RelPath 'NewRidgeFinancial2/model-automation/Modelfile.hal-helper-14b' -MaxFileChars 4000
[void]$sb.AppendLine($chunk)
$chunk = Get-FullFileText -RelPath 'evals/prompts/qwen_second_opinion_system.txt' -MaxFileChars 8000
[void]$sb.AppendLine($chunk)
$chunk = Get-FullFileText -RelPath 'evals/hal_humanization_ab_prompts.json' -MaxFileChars 6000
[void]$sb.AppendLine($chunk)
$chunk = Get-FullFileText -RelPath 'evals/prompts/judge_rubric.md' -MaxFileChars 2000
[void]$sb.AppendLine($chunk)

$mgrPath = Join-Path $Nr2 'site/data/hal-manager.json'
if (Test-Path $mgrPath) {
    $mgr = Get-Content -Path $mgrPath -Raw -Encoding UTF8 | ConvertFrom-Json
    [void]$sb.AppendLine('=== hal-manager.json (cognitivePathways + status) ===')
    if ($mgr.cognitivePathways) {
        [void]$sb.AppendLine(($mgr.cognitivePathways | ConvertTo-Json -Depth 6))
    }
    if ($mgr.status) {
        [void]$sb.AppendLine(($mgr.status | ConvertTo-Json -Depth 4))
    }
    [void]$sb.AppendLine('')
}

$chunk = Get-LineRangeText -RelPath 'NewRidgeFinancial2/site/hal-core.js' -StartLine 567 -EndLine 685
[void]$sb.AppendLine($chunk)
$chunk = Get-LineRangeText -RelPath 'NewRidgeFinancial2/site/hal-agent.js' -StartLine 518 -EndLine 580
[void]$sb.AppendLine($chunk)
$chunk = Get-LineRangeText -RelPath 'NewRidgeFinancial2/site/hal-core.js' -StartLine 673 -EndLine 685
[void]$sb.AppendLine($chunk)

$samplesPath = Join-Path $Root $SamplesFile
if (Test-Path $samplesPath) {
    [void]$sb.AppendLine('=== SUBJECT MODEL SAMPLE RESPONSES (hal-chat:8b) ===')
    [void]$sb.AppendLine((Get-Content -Path $samplesPath -Raw -Encoding UTF8))
    [void]$sb.AppendLine('')
} else {
    [void]$sb.AppendLine('=== SUBJECT MODEL SAMPLE RESPONSES ===')
    [void]$sb.AppendLine('(Not yet collected — run run_falcon180_hal_humanization_eval.py --collect-samples first)')
    [void]$sb.AppendLine('')
}

$text = Limit-TextLength -Text $sb.ToString() -Limit $MaxChars
Set-Content -Path $OutFile -Value $text -Encoding UTF8
Write-Host "Wrote $OutFile ($($text.Length) chars)"
