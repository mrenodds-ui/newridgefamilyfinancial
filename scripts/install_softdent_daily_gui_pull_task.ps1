# Install SoftDent daily GUI master pull — 9:00 PM interactive desktop only.
# pywinauto cannot reliably drive SoftDent from Session 0 / S4U headless.
# SoftDent before Trellis (~10:10 PM). Night-before for next business day money beams.
$ErrorActionPreference = 'Stop'

$ProjectRoot = if ($env:NEWRIDGE_PROJECT_ROOT) { $env:NEWRIDGE_PROJECT_ROOT } else { 'C:\New folder' }
$RepoRoot = if ($env:NEWRIDGE_FINANCIAL_REPO) { $env:NEWRIDGE_FINANCIAL_REPO } else { 'C:\NewRidgeFamilyFinancial' }
$TaskName = 'New Ridge SoftDent Daily GUI Pull 9PM'
$LegacyTaskName = 'New Ridge SoftDent Daily GUI Pull 5PM'
$Script = Join-Path $ProjectRoot 'ops\softdent\automation\run_softdent_daily_gui_pull.ps1'
$CurrentUser = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name

if (!(Test-Path -LiteralPath $Script)) {
    throw "Missing script: $Script"
}
if (!(Test-Path -LiteralPath (Join-Path $RepoRoot 'scripts\run_softdent_daily_master_pull.py'))) {
    throw "Missing repo master pull: $RepoRoot\scripts\run_softdent_daily_master_pull.py"
}

Unregister-ScheduledTask -TaskName $LegacyTaskName -Confirm:$false -ErrorAction SilentlyContinue | Out-Null

$action = New-ScheduledTaskAction `
    -Execute 'powershell.exe' `
    -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$Script`"" `
    -WorkingDirectory $RepoRoot

$trigger = New-ScheduledTaskTrigger -Daily -At '9:00 PM'

$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -WakeToRun `
    -RestartCount 1 `
    -RestartInterval (New-TimeSpan -Minutes 10) `
    -MultipleInstances IgnoreNew `
    -ExecutionTimeLimit (New-TimeSpan -Hours 2)

# Interactive only — SoftDent GUI automation requires a logged-on desktop session.
$principal = New-ScheduledTaskPrincipal -UserId $CurrentUser -LogonType Interactive -RunLevel Limited
Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Force | Out-Null

Write-Host "Installed '$TaskName' (Interactive / 9:00 PM) for $CurrentUser."
Write-Host "Retired legacy task '$LegacyTaskName' when present."
Write-Host "Requirement: SoftDent workstation user must be logged on at 9 PM."
Write-Host "Post-pull: TXN claims rebuild + payer attribution via run_softdent_daily_master_pull.py."
Write-Host "AM ingest task stays separate (5:15 AM) - do not merge GUI pull into Session-0 jobs."
