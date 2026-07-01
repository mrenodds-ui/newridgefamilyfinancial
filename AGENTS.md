# AGENTS.md

## Cursor Cloud specific instructions

### Current repository state (important)

This repository currently contains **only documentation, configuration, and a root
`package.json`**. There is **no application source code committed**. In particular, the
directories and entrypoints referenced throughout the docs do **not** exist on disk:

- No `frontend/`, `dashboard-frontend/`, `dashboard-backend/`, `app/`, or `scripts/` directories.
- No `index.js` (despite `package.json` `"main": "index.js"`).
- No `Dockerfile` / `docker-compose.yml`, and no `.github/workflows/`.
- No `requirements.txt` / `pyproject.toml` (the README's FastAPI/Python backend is not present).
- No `*.ts` / `*.tsx` / `*.js` / `*.py` / `*.html` source files are tracked in git.

The markdown docs (`README.md`, `ARCHITECTURE.md`, `ONBOARDING.md`, `DEPLOYMENT.md`, etc.)
describe several intended-but-unbuilt products (a React/Vite SPA, a Node/Express backend,
and a Python/FastAPI backend). Treat these as **aspirational/planning docs**, not as an
accurate description of what is runnable today. Many docs are duplicated/merged and
contradict each other.

### What CAN be set up / run

- Toolchain present: Node.js 22, npm 10, Python 3.12.
- `npm install` (root) works cleanly and installs the Express/CSV/cron toolchain
  (`express`, `cors`, `csv-parser`, `node-cron`, `papaparse`, `ts-node-dev`).
- There are **no** runnable npm scripts: `npm test` only echoes an error and exits 1,
  and there is no `dev`/`start`/`build`/`lint` script.
- Helper scripts (`RestartDashboard.bat`, `run_all_checks.ps1`, `hal_evaluate_all.ps1`)
  are Windows PowerShell/batch and reference the missing `frontend/`/`scripts/` dirs, so
  they cannot run here as-is.

### Practical guidance

- Do not expect to `npm run dev` / build / serve anything until application source code
  is actually added to the repo.
- Once real source is added (e.g. a `frontend/` Vite app or a Node entrypoint), update
  this file and the startup instructions accordingly.
