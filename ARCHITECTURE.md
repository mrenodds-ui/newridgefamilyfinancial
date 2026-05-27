# Architecture Overview
## Structure
- `dashboard-frontend/` — React SPA frontend (all logic, parsing, and UI)
- `scripts/` — Utility and CI scripts
## Data Flow
1. Data imported from SoftDent/QuickBooks via file upload in the browser.
2. All parsing, aggregation, and analytics run in-browser. There is no backend.
3. Frontend visualizes KPIs, trends, and reports directly from imported data.
## Modernization & Scalability
- SPA logic is modular and ready for future API integration if needed.
## Security
- All logic runs in-browser; no backend secrets or server-side code.
- HTTPS/HSTS enforced in production via reverse proxy.
## CI/CD
- Lint, type-check, test, and coverage for all subprojects
- Automated deploy pipeline (see .github/workflows/)
## Containerization
- Dockerfile and docker-compose are only for the frontend SPA. No backend deployment is present.
## See also: DEPLOYMENT.md, ONBOARDING.md, SECURITY_HEADERS.md
# Architecture Overview

## Structure
- `dashboard-frontend/` — React SPA frontend (all logic, parsing, and UI)
- `scripts/` — Utility and CI scripts

## Data Flow
1. Data imported from SoftDent/QuickBooks via file upload in the browser.
2. All parsing, aggregation, and analytics run in-browser (no backend).
3. Frontend visualizes KPIs, trends, and reports directly from imported data.

## Modernization & Scalability
- SPA logic is modular and ready for future backend/API integration if needed.

## Security
- All logic runs in-browser; no backend secrets or server-side code.
- HTTPS/HSTS enforced in production via reverse proxy.

## CI/CD
- Lint, type-check, test, and coverage for all subprojects
- Automated deploy pipeline (see .github/workflows/)

## Containerization
- Dockerfile and docker-compose for local/cloud deployment

## See also: DEPLOYMENT.md, ONBOARDING.md, SECURITY_HEADERS.md
