# ERA-835 inbox drop — NR2 first remittance smoke

**Office:** New Ridge Family Financial  
**Rule:** SoftDent READ-ONLY · empty ≠ `$0` · never invent remittance · QB post is manual only

## Drop folders (any one)

1. `C:\Users\mreno\newridgefamilyfinancial\app_data\nr2\office\era_inbox\drop`
2. `C:\SoftDentFinancialExports\era`
3. `C:\SoftDentReportExports\era`
4. Or set `NR2_ERA835_INBOX` to a custom folder

Accepted extensions: `.835` · `.edi` · `.txt` (or filename containing `era`)

## Ingest

```powershell
cd C:\Users\mreno\newridgefamilyfinancial
.\.venv\Scripts\python.exe scripts\run_era_inbox_ingest_ops.py
```

Or HAL / Apex: Refresh Inbox → `POST /api/apex/hal/era-inbox/ingest` (session mutation token).

## Validation gate

- Scan shows `fileCount ≥ 1`
- Ingest inserts rows (`rowsInserted > 0`) and writes `app_data/nr2/office/era_inbox/ingest_manifest.jsonl`
- `era_suggestions` count ≥ 1 (status `suggest_qb_manual` — operator posts in QuickBooks)
- Ops gate: `python scripts/nr2_ops_gates_checklist.py` → `era_inbox` **GREEN**

## Honesty

- **Do not** drop the test fixture `NewRidgeFinancial2/test/fixtures/synthetic.835` into the live inbox and treat it as payer money.
- Fixture path smoke is for unit tests only (`NR2_ERA835_INBOX` temp dir).
- No SoftDent write-back. No auto-post to QuickBooks.

## After first real drop

1. Ingest  
2. Review suggestions (payer / claimCount / totalPaid)  
3. Post in QuickBooks manually if correct  
4. Keep files under `era_inbox/processed` for audit
