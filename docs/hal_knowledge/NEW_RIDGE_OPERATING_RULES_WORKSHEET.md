# New Ridge operating rules — HAL fill-in worksheet

Fill the blanks below, then teach HAL either by:

1. Saying in Ask HAL: `Remember this: …` (one fact per message), or  
2. Editing `scripts/seed_practice_learned_memories.py` and running:

```powershell
cd C:\NewRidgeFamilyFinancial
.\.venv\Scripts\python.exe scripts\seed_practice_learned_memories.py
```

**Do not put here:** passwords, clearinghouse keys, NPI/TIN secrets, patient names, or member IDs.

Scaffold memories already seeded (medium/low confidence) tell HAL to ask Steve rather than invent dollars until you fill these in.

**Already live (no fill-in needed for these):** fee CDT lookup (`fee_schedule.json`), SoftDent InsCo + Insurance.xlsx payer phones, claim↔payer join, daily briefing claim-lane counts from imports.

---

## 1. Write-offs & adjustments

| Field | Your answer |
| --- | --- |
| Dual-approval required above ($) | ________ |
| Who approves below threshold | ________ |
| Who approves above threshold | ________ |
| SoftDent adjustment codes used (CO-45, courtesy, etc.) | ________ |
| Never write off without… | ________ |

**Remember template:**  
`Remember this: At New Ridge, write-offs over $____ need approval from ____. Below that, ____ may approve. Staff post in SoftDent; HAL only drafts review notes.`

---

## 2. Broken / missed appointments

| Field | Your answer |
| --- | --- |
| Fee amount ($) | ________ or none |
| Applies to (hygiene / doctor / both) | ________ |
| Grace / cancel-by rule | ________ |
| Repeat no-show rule | ________ |

**Remember template:**  
`Remember this: New Ridge broken-appointment policy: ____. Front desk logs in SoftDent; do not auto-charge without this policy.`

---

## 3. Payment plans

| Field | Your answer |
| --- | --- |
| Minimum down payment | ________ |
| Maximum term (months) | ________ |
| Who may approve | ________ |
| SoftDent / finance tool used | ________ |

**Remember template:**  
`Remember this: New Ridge payment plans require ____ down, max ____ months, approved by ____. SoftDent ledger is source of truth.`

---

## 4. QuickBooks chart of accounts (real books)

NR2’s planning COA (1010 Cash, 2200 Accrued Expenses, …) is **not** your live QB chart. Paste the mappings you care about:

| SoftDent / ops concept | QuickBooks account name | QB # (if any) |
| --- | --- | --- |
| Clinical production / fees | ________ | ________ |
| Insurance payments / deposits | ________ | ________ |
| Patient payments | ________ | ________ |
| Lab expense | ________ | ________ |
| Dental supplies | ________ | ________ |
| Payroll / officer wages | ________ | ________ |
| Rent / occupancy | ________ | ________ |

**Remember template:**  
`Remember this: New Ridge QuickBooks maps SoftDent production to ____ and collections/deposits to ____. Use import account names; do not invent planning COA numbers as live books.`

---

## 5. Fee schedules (top payers)

Where do contracted fees live? (folder, spreadsheet, SoftDent fee table)

`________`

| Payer | Notes / where to look | Optional: sample allowed (D0120 / D1110 / D2740) |
| --- | --- | --- |
| Delta Dental | ________ | ________ |
| Cigna | ________ | ________ |
| MetLife | ________ | ________ |
| Guardian | ________ | ________ |
| BCBS Kansas | ________ | ________ |
| KanCare / MCO | ________ | ________ |

**Status:** Live CDT lookup is in `NewRidgeFinancial2/data/fee_schedule.json` (Ask HAL: `lookup_fee_schedule`).  
Fill the table only if you want extra notes beyond the spreadsheet export.

**Remember template:**  
`Remember this: For allowed amounts, use HAL fee schedule lookup (fee_schedule.json). Escalate to Steve only when the CDT or carrier column is missing.`

---

## 6. Staff roster (roles only — no personal phones required)

| Role | Name |
| --- | --- |
| Office manager | Steve *(already seeded)* |
| Owner / dentist | Dr. Michael Reno *(already seeded)* |
| Billing lead | ________ |
| Hygiene lead | ________ |
| Front desk lead(s) | ________ |
| Primary lab contact | ________ |

**Remember template:**  
`Remember this: At New Ridge, ____ handles billing coordination; ____ leads hygiene; front desk leads are ____.`

---

## 7. Goals (optional)

| Goal | Target |
| --- | --- |
| Monthly production ($) | ________ |
| Collection % | ________ |
| Hygiene / recall goal | ________ |
| Case acceptance % | ________ |

**Remember template:**  
`Remember this: New Ridge monthly production goal is $____ and collection target is ____%. Use SoftDent imports for actuals.`

---

## 8. Month-end extras (optional)

Anything beyond the standard checklist (daysheet → imports → EOB → A/R 90+ → denials → QB P&L → Taxes/CPA flags)?

`________`

---

## After you fill

1. Teach HAL with `Remember this:` lines, **or** update seed + re-run the script.  
2. Spot-check in Ask HAL:  
   - “What is our write-off approval rule?”  
   - “Where do fee schedules live?”  
   - “Who handles billing vs Steve?”  
3. Re-run MemoAI index if you only edited JSONL by hand:

```powershell
.\.venv\Scripts\python.exe scripts\sync_hal_memo_index.py
```
