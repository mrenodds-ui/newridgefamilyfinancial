# SoftDent agent stop — LIFTED

**Date:** 2026-07-16  
**Operator:** REOPEN SOFTDENT  

## Action

- Removed `.cursor/rules/softdent-agent-stop-now.mdc` (hard stop cancelled).
- SoftDent desktop process was already running (`SDWIN`) at lift time.
- Agents may again run SoftDent GUI / Excel or Print Preview pulls / `morning_bundle_attended.py` per SoftDent desktop hard rules.

## Still in force

- SoftDent **READ-ONLY** (no write-back)
- Output Options: **Excel** or **Print Preview** only — never Printer, never File
- empty ≠ $0 · board PHI initials+hash
- Launch via **CS SoftDent Software.lnk** (`-sus`) when a fresh launch is needed
