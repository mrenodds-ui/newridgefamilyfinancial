@echo off
REM Shortcut to rebuild and restart the New Ridge Family Financial SPA
cd /d %~dp0
npm run build --prefix frontend
npm run dev --prefix frontend
pause