# Legacy program (reference only)

This folder is a frozen snapshot of the previous New Ridge Family Financial
program, kept **for reference only**. Nothing here is imported, built, or run by
the current application.

The active app is now a fresh mission-control mockup frontend served by a
minimal FastAPI static server. See the repo root `app/` and `frontend/`.

## Contents

- `app/` — the full previous FastAPI backend (auth, routes, HAL, insurance
  narratives, QuickBooks/SoftDent services, evaluation harness, and backend
  tests). Preserved so business logic and API contracts can be re-wired later.
- `frontend-src/` — the previous frontend source: original pages, dashboard and
  HAL widgets, hooks, IndexedDB/browser persistence, service-worker/offline
  code, MSW mocks, Storybook stories, Playwright e2e specs, and unit tests.

## Why it was archived

The UI was rebuilt from approved mission-control mockups. The old screens kept
"bleeding through" during the transition, so the previous implementation was
moved out of the active source tree entirely and replaced with the mockup
pages. The API client/types scaffolding was kept in the live `frontend/src/api`
so real data can be wired into the new pages later.

## Re-using this code

Treat these files as a read-only reference. If you need a piece of old logic,
copy it forward into the active tree and adapt it to the new structure rather
than importing directly from `_legacy/`.
