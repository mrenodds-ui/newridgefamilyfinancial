# SoftDent GUI Sign On — program + HAL wiring (no secrets in git)

**Date:** 2026-07-12  

## SoftDent data-access doctrine (whole program)

1. **Prefer the database lane** — SoftDent ODBC / Sensei DataSync / `sd_*` SQLite when the needed rows are there.  
2. **If the database cannot reach it** — the **only** path is SoftDent **Sign On** (env credentials) **and use the SoftDent UI** (click **Excel** then **Enter**), then place the file for NR2 ingest/Sync.  
3. **Never** invent dollars, SoftDent write-back, or a fictional vendor CLI for those reports.

Constant: `SOFTDENT_DATA_ACCESS_DOCTRINE` in `softdent_signon.py` (also on HAL status / Sign On API).

## Master report list (program knowledge)

| Artifact | Role |
|----------|------|
| `NewRidgeFinancial2/softdent_master_reports.json` | Canonical list of what NR2 needs + DB vs GUI |
| `NewRidgeFinancial2/softdent_master_reports.py` | `verify_master_reports()` + HAL summary |
| `NewRidgeFinancial2/softdent_gui_menu_map.json` | SoftDent UI menu paths / Excel stems for GUI pulls |
| `scripts/run_softdent_daily_master_pull.py` | Master GUI orchestrator; `--verify-only` audits the list |

### Master reports

| Id | Preferred | When DB cannot supply |
|----|-----------|------------------------|
| `sd_odbc_core` | Database (`sd_*`) | Sensei/ODBC extract first |
| `register` | GUI | Sign On → Registers → Period → Excel → Enter |
| `collections` | GUI | Sign On → Collection Reports → Summary → Excel |
| `transactions` | GUI (DB assist) | Sign On → Trans for a Period → Excel |
| `daysheet` | GUI | Sign On → Daysheet → Excel |
| `aging` | GUI (DB assist) | Sign On → Account Aging → Excel |
| `writeoff_totals` | GUI (DB assist) | Sign On → Writeoff Totals → Excel |

Verify:

```text
python -m softdent_master_reports --start 2026-07-01 --end 2026-07-12
python scripts/run_softdent_daily_master_pull.py --verify-only --start 2026-07-01 --end 2026-07-12
```

## How Sign On credentials are known

SoftDent GUI Sign On credentials are **only** in environment variables:

| Key | Purpose |
|-----|---------|
| `SOFTDENT_SIGNON_USER` | SoftDent Sign On user id (typically `COMPUTE`) |
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

- **User:** `COMPUTE` (SoftDent Sign On / Change Login)  
- **Password:** stored only in local env / `.env` — **not** in git, HAL replies, or docs  

## HAL surfaces

| Surface | Behavior |
|---------|----------|
| Local policy | Sign On password / “data not in database” → env keys + UI-only doctrine (never prints password) |
| LLM context | `compile_softdent_signon_guidance` injects Sign On + data-access rule |
| HAL status | `softdentSignOn` + `dataAccessDoctrine` + `masterReports` on `/api/apex/hal/status` |
| API | `GET /api/apex/hal/softdent-signon` |
| HAL tool | `softdent_signon_status` in `hal-agent.js` |
| Export playbook | DB first; else Sign On + UI export |
| Services | `fetchSoftdentSignOnStatus` in `site/services.js` |

## Ask HAL

- How does SoftDent Sign On work?
- Where is the SoftDent Sign On password?
- How do I get SoftDent data that cannot be reached by the database?
- What SoftDent reports does the master program need?
- SoftDent login credentials

## Usage

```text
python NewRidgeFinancial2/softdent_signon.py
python -m softdent_master_reports --require-inbox --start 2026-07-01 --end 2026-07-12
python scripts/run_softdent_safe_period_export.py --start 2026-07-01 --end 2026-07-12
```

Or ask HAL / Refresh SoftDent period — step `softdent_signon` confirms `passwordConfigured` + assist result.

## Security

- Do not commit `.env`  
- Do not paste the password into Moonshot docs or chat  
- HAL must not echo the password value  
- Rotate if this value was shared in chat logs  
- Sign-on assist uses `force_change_login=False` by default (no Change Login spam when already signed in)
