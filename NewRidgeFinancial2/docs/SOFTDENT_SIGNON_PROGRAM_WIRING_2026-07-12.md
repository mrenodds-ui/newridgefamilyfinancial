# SoftDent GUI Sign On — program + HAL wiring (no secrets in git)

**Date:** 2026-07-12  

## SoftDent data-access doctrine (whole program)

1. **Prefer the database lane** — SoftDent ODBC / Sensei DataSync / `sd_*` SQLite when the needed rows are there.  
2. **If the database cannot reach it** — the **only** path is SoftDent **Sign On** (env credentials) **and use the SoftDent UI** (Reports / Accounting → export Register, Collections, daysheet, etc.), then place the file for NR2 ingest/Sync.  
3. **Never** invent dollars, SoftDent write-back, or a fictional vendor CLI for those reports.

Constant: `SOFTDENT_DATA_ACCESS_DOCTRINE` in `softdent_signon.py` (also on HAL status / Sign On API).

## How Sign On credentials are known

SoftDent GUI Sign On credentials are **only** in environment variables:

| Key | Purpose |
|-----|---------|
| `SOFTDENT_SIGNON_USER` | SoftDent Sign On user id (typically `Dr`) |
| `SOFTDENT_SIGNON_PASSWORD` | SoftDent Sign On password |
| `SOFTDENT_GUI_USER` / `SOFTDENT_GUI_PASSWORD` | Aliases |

Loaded from process/User env and local gitignored `.env` (`C:\New folder\.env`, `NewRidgeFinancial2\.env`).

| Location | Purpose |
|----------|---------|
| `NewRidgeFinancial2/softdent_signon.py` | Resolver + UI assist + data-access doctrine |
| `NewRidgeFinancial2/softdent_odbc_extract.py` | Database / ODBC extract lane (preferred when reachable) |
| `NewRidgeFinancial2/softdent_gui_export.py` | UI export helpers for DB-unreachable reports |
| `scripts/run_softdent_safe_period_export.py` | Safe orchestrator (no password in stdout) |
| `refresh_softdent_period_imports` | Step `softdent_signon` (never echoes password) |

## SoftDent Sign On identity

- **User:** `Dr` (SoftDent Sign On / Change Login)  
- **Password:** stored only in local env / `.env` — **not** in git, HAL replies, or docs  

## HAL surfaces

| Surface | Behavior |
|---------|----------|
| Local policy | Sign On password / “data not in database” → env keys + UI-only doctrine (never prints password) |
| LLM context | `compile_softdent_signon_guidance` injects Sign On + data-access rule |
| HAL status | `softdentSignOn` + `dataAccessDoctrine` on `/api/apex/hal/status` |
| API | `GET /api/apex/hal/softdent-signon` |
| HAL tool | `softdent_signon_status` in `hal-agent.js` |
| Export playbook | DB first; else Sign On + UI export |
| Services | `fetchSoftdentSignOnStatus` in `site/services.js` |

## Ask HAL

- How does SoftDent Sign On work?
- Where is the SoftDent Sign On password?
- How do I get SoftDent data that cannot be reached by the database?
- SoftDent login credentials

## Usage

```text
python NewRidgeFinancial2/softdent_signon.py
python scripts/run_softdent_safe_period_export.py --start 2026-07-01 --end 2026-07-12
```

Or ask HAL / Refresh SoftDent period — step `softdent_signon` confirms `passwordConfigured` + assist result.

## Security

- Do not commit `.env`  
- Do not paste the password into Moonshot docs or chat  
- HAL must not echo the password value  
- Rotate if this value was shared in chat logs  
- Sign-on assist uses `force_change_login=False` by default (no Change Login spam when already signed in)
