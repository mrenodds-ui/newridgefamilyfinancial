# Install NR2 desk smoke confidence loop — every 5 minutes while logged on.
$ErrorActionPreference = 'Stop'

$RepoRoot = if ($env:NEWRIDGE_FINANCIAL_REPO) {
    $env:NEWRIDGE_FINANCIAL_REPO
} else {
    'C:\Users\mreno\newridgefamilyfinancial'
}
$TaskName = 'NR2 Desk Smoke Every 5 Min'
$Py = Join-Path $RepoRoot '.venv\Scripts\python.exe'
$Script = Join-Path $RepoRoot 'scripts\desk_ops_smoke.py'
$CurrentUser = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name

if (!(Test-Path -LiteralPath $Py)) {
    throw "Missing venv python: $Py"
}
if (!(Test-Path -LiteralPath $Script)) {
    throw "Missing script: $Script"
}

$action = New-ScheduledTaskAction `
    -Execute $Py `
    -Argument "`"$Script`" --no-http" `
    -WorkingDirectory $RepoRoot

$trigger = New-ScheduledTaskTrigger -Daily -At '6:00AM' -DaysInterval 1
$trigger.Repetition = $(New-ScheduledTaskTrigger -Once -At '6:00AM' -RepetitionInterval (New-TimeSpan -Minutes 5) -RepetitionDuration (New-TimeSpan -Days 1)).Repetition

$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -MultipleInstances IgnoreNew `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 2)

$principal = New-ScheduledTaskPrincipal -UserId $CurrentUser -LogonType Interactive -RunLevel Limited
Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Force | Out-Null

Write-Host "Installed '$TaskName' (every 5 min, --no-http) for $CurrentUser."
Write-Host "Log: $RepoRoot\app_data\nr2\ops\desk_smoke_log.jsonl"
