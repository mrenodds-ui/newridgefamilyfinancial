# Install Trellis withBenefits AM proof - Mon-Thu 7:15 AM interactive.
# Runs after 1:00 AM Trellis --same-day --verify; logs to .local_logs/moonshot_financial_eval.
$ErrorActionPreference = 'Stop'

$RepoRoot = if ($env:NEWRIDGE_FINANCIAL_REPO) {
    $env:NEWRIDGE_FINANCIAL_REPO
} else {
    'C:\Users\mreno\newridgefamilyfinancial'
}
$TaskName = 'NR2 Trellis AM withBenefits Proof 715AM Mon-Thu'
$Py = Join-Path $RepoRoot '.venv\Scripts\python.exe'
$Script = Join-Path $RepoRoot 'scripts\prove_trellis_withbenefits_am.py'
$CurrentUser = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name

if (!(Test-Path -LiteralPath $Py)) {
    throw "Missing venv python: $Py"
}
if (!(Test-Path -LiteralPath $Script)) {
    throw "Missing script: $Script"
}

$action = New-ScheduledTaskAction `
    -Execute $Py `
    -Argument "`"$Script`"" `
    -WorkingDirectory $RepoRoot

$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday,Tuesday,Wednesday,Thursday -At '7:15AM'

$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -MultipleInstances IgnoreNew `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 15)

$principal = New-ScheduledTaskPrincipal -UserId $CurrentUser -LogonType Interactive -RunLevel Limited
Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Force | Out-Null

Write-Host "Installed '$TaskName' (Interactive / Mon-Thu 7:15 AM) for $CurrentUser."
Write-Host "Exit 0 when withBenefits > 0; exit 2 when still status-only (honest until scrape lands)."
Write-Host "Pair with Trellis report pull: scripts/install_trellis_nightly_verify_task.ps1 (1:00 AM)."
