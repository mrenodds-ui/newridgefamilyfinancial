# Install HAL Trellis dental eligibility report pull - Mon-Thu 1:00 AM interactive.
# SoftDent money pulls at 9:00 PM; APScheduler builds next-day worklist ~10:00 PM;
# this task pulls/verifies today's chairs at 1:00 AM (--same-day --verify).
# Playwright needs a logged-on desktop (same pattern as SoftDent GUI pull).
$ErrorActionPreference = 'Stop'

$RepoRoot = if ($env:NEWRIDGE_FINANCIAL_REPO) {
    $env:NEWRIDGE_FINANCIAL_REPO
} else {
    'C:\Users\mreno\newridgefamilyfinancial'
}
$TaskName = 'NR2 Trellis Nightly Insurance Verify 1AM Mon-Thu'
$LegacyTaskName = 'NR2 Trellis Nightly Insurance Verify 10PM Mon-Thu'
$Py = Join-Path $RepoRoot '.venv\Scripts\python.exe'
$Script = Join-Path $RepoRoot 'scripts\run_trellis_nightly_verify.py'
$CurrentUser = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name

if (!(Test-Path -LiteralPath $Py)) {
    throw "Missing venv python: $Py"
}
if (!(Test-Path -LiteralPath $Script)) {
    throw "Missing script: $Script"
}
$EnvLocal = Join-Path $RepoRoot '.env.vyne.local'
if (!(Test-Path -LiteralPath $EnvLocal)) {
    Write-Warning "Missing .env.vyne.local - create VYNE_AUTOMATION_USERNAME / PASSWORD (Wichita) before first run."
}

# Remove legacy 10:10 PM task if present
Unregister-ScheduledTask -TaskName $LegacyTaskName -Confirm:$false -ErrorAction SilentlyContinue

$action = New-ScheduledTaskAction `
    -Execute $Py `
    -Argument "`"$Script`" --force --verify --same-day" `
    -WorkingDirectory $RepoRoot

$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday,Tuesday,Wednesday,Thursday -At '1:00AM'

$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -WakeToRun `
    -RestartCount 1 `
    -RestartInterval (New-TimeSpan -Minutes 15) `
    -MultipleInstances IgnoreNew `
    -ExecutionTimeLimit (New-TimeSpan -Hours 3)

$principal = New-ScheduledTaskPrincipal -UserId $CurrentUser -LogonType Interactive -RunLevel Limited
Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Force | Out-Null

Write-Host "Installed '$TaskName' (Interactive / Mon-Thu 1:00 AM) for $CurrentUser."
Write-Host "Uses --same-day so 1 AM pull targets today's Mon-Thu chairs (worklist may be built night-before)."
Write-Host "Requirement: user logged on; SoftDent SQLite + Sensei Reference + .env.vyne.local (Wichita)."
