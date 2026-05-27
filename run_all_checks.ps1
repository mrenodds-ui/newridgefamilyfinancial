# PowerShell script to run lint, typecheck, audit, and test for all major subprojects

Write-Host "=== Running checks for frontend ==="
Push-Location ./frontend
if (Test-Path package.json) {
    Write-Host "- npm install (frontend)"
    npm install
    Write-Host "- npm run lint (frontend)"
    npm run lint
    Write-Host "- npm run typecheck (frontend)"
    npm run typecheck
    Write-Host "- npm audit (frontend)"
    npm audit --audit-level=moderate
    Write-Host "- npm test (frontend)"
    npm test
}
Pop-Location

Write-Host "=== Running checks for dashboard-frontend ==="
Push-Location ./dashboard-frontend
if (Test-Path package.json) {
    Write-Host "- npm install (dashboard-frontend)"
    npm install
    Write-Host "- npm run lint (dashboard-frontend)"
    npm run lint
    Write-Host "- npm run typecheck (dashboard-frontend)"
    npm run typecheck
    Write-Host "- npm audit (dashboard-frontend)"
    npm audit --audit-level=moderate
    Write-Host "- npm test (dashboard-frontend)"
    npm test
}
Pop-Location

Write-Host "=== Running Python lint and tests ==="
# Example: run flake8 and pytest if available
if (Test-Path .\scripts) {
    if (Test-Path .\.venv-py313\Scripts\activate) {
        Write-Host "- Activating Python venv"
        . .\.venv-py313\Scripts\activate
    }
    if (Get-Command flake8 -ErrorAction SilentlyContinue) {
        Write-Host "- Running flake8 lint"
        flake8 scripts
    } else {
        Write-Host "- flake8 not found, skipping Python lint"
    }
    if (Get-Command pytest -ErrorAction SilentlyContinue) {
        Write-Host "- Running pytest"
        pytest scripts
    } else {
        Write-Host "- pytest not found, skipping Python tests"
    }
}

Write-Host "=== All checks complete ==="