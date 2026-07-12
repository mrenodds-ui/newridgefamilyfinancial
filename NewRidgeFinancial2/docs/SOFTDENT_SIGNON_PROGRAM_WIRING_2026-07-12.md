# SoftDent GUI Sign On — program wiring (no secrets in git)

**Date:** 2026-07-12  
**Build:** hal-10566+  

## How the program knows SoftDent Sign On

| Location | Purpose |
|----------|---------|
| `SOFTDENT_SIGNON_USER` / `SOFTDENT_SIGNON_PASSWORD` | Canonical env keys (User scope + process) |
| `C:\New folder\.env` | SoftDent ops / scheduled refresh (Load-NewRidgeDotEnv.ps1) |
| `NewRidgeFinancial2/.env` | NR2 local (gitignored) |
| `NewRidgeFinancial2/softdent_signon.py` | Resolver + optional pywinauto Sign On / Change Login assist |
| `refresh_softdent_period_imports` | Reports sign-on status (never echoes password) |

## SoftDent Sign On identity

- **User:** `Dr` (SoftDent Sign On / Change Login)  
- **Password:** stored only in local env / `.env` — **not** in git, HAL memory, or docs  

## Usage

```text
python NewRidgeFinancial2/softdent_signon.py
```

Or ask HAL / Refresh SoftDent period — step `softdent_signon` confirms `passwordConfigured` + assist result.

## Security

- Do not commit `.env`  
- Do not paste the password into Moonshot docs or HAL memory  
- Rotate if this value was shared in chat logs
