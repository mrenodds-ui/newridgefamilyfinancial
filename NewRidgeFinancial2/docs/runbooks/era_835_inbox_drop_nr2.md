# ERA-835 inbox drop — NR2 first remittance smoke

**Office:** New Ridge Family Financial  
**Rule:** SoftDent READ-ONLY · empty ≠ `$0` · never invent remittance · QB post is manual only  
**PMS eval P0-C:** Establish a repeatable payer EDI drop → NR2 ingest → QB-manual suggest path (do not wait on SoftDent Excel).

## Drop folders (any one)

1. `C:\Users\mreno\newridgefamilyfinancial\app_data\nr2\office\era_inbox\drop` ← **preferred live inbox**
2. `C:\SoftDentFinancialExports\era`
3. `C:\SoftDentReportExports\era`
4. Or set `NR2_ERA835_INBOX` to a custom folder

Accepted extensions: `.835` · `.edi` · `.txt` (or filename containing `era`)

## Operator setup (top payers — first real drops)

1. Identify the practice’s top remittance sources (typically the largest commercial + Medicaid/Medicare EDI payers that already send ERA/835).
2. For each source, confirm where the 835 lands today (payer portal download, clearinghouse mailbox, email attachment).
3. Copy **only real payer files** into the preferred drop folder above (do not rename away from `.835` / `.edi` if possible).
4. Prefer one payer’s first file as smoke, then expand to top 5 once GREEN.

## Ingest

```powershell
cd C:\Users\mreno\newridgefamilyfinancial
.\.venv\Scripts\python.exe scripts\run_era_inbox_ingest_ops.py
```

Or HAL / Apex: Refresh Inbox → `POST /api/apex/hal/era-inbox/ingest` (session mutation token).

## Validation gate

- Scan shows `fileCount ≥ 1` and `realFileCount ≥ 1` (README / placeholder alone stays **YELLOW** · empty ≠ `$0`)
- Ingest inserts rows (`rowsInserted > 0`) and writes `app_data/nr2/office/era_inbox/ingest_manifest.jsonl`
- `era_suggestions` count ≥ 1 (status `suggest_qb_manual` — operator posts in QuickBooks)
- Ops gate: `python scripts/nr2_ops_gates_checklist.py` → `era_inbox` **GREEN**
- SoftDent write-back remains **off**; NR2 does not auto-post to SoftDent

## Honesty

- **Do not** drop the test fixture `NewRidgeFinancial2/test/fixtures/synthetic.835` into the live inbox and treat it as payer money.
- Fixture path smoke is for unit tests only (`NR2_ERA835_INBOX` temp dir).
- No SoftDent write-back. No auto-post to QuickBooks.
- README.txt / placeholder in `drop` is **not** remittance (chip must keep Empty ≠ `$0`).

## After first real drop

1. Ingest  
2. Review suggestions (payer / claimCount / totalPaid)  
3. Post in QuickBooks manually if correct  
4. Keep files under `era_inbox/processed` for audit  
5. Tell Cursor: **ERA 835 dropped — verify GREEN** if ops gate should be re-checked

## Parallel to SoftDent Excel hold

ERA ingest does **not** require SoftDent Excel. While Excel is grey (see `softdent_excel_grey_hold_protocol_nr2.md`), ERA remains the independent remittance lane.