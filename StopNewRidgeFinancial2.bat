@echo off
setlocal
set "ROOT_DIR=%~dp0"

powershell -NoProfile -Command "$port = 1966; $conns = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue; foreach ($c in $conns) { Write-Host ('Stopping NewRidgeFinancial 2.0 on port {0} (PID {1})...' -f $port, $c.OwningProcess); Stop-Process -Id $c.OwningProcess -Force -ErrorAction SilentlyContinue }; if (-not $conns) { Write-Host 'No listener on port 1966.' }"
