# SoftDent Full Product Knowledge (encoded for NR2/HAL)

**Date:** 2026-07-13  
**Goal:** Learn SoftDent as a **whole product** (not just period-close pulls) and make the **program** answer from that knowledge.

---

## What was learned

Source of truth: Carestream **SoftDent Online Help OH_DE1010** decompiled from this PC:

`C:\SoftDent\WinHelp\SoftDent_OnlineHelp_OH_DE1010.chm`

| Surface | Encoded |
|---------|---------|
| Help TOC | **2040** topics (full `.hhc` tree) |
| Reports menu | **13 categories**, **167** named reports with descriptions (Accounting, PM, Patient, Account, Recall/Appt, Provider, Insurance, Trojan, ADA/Tx/Diag, Rx/Labs, Report Manager, Audit Trail, User-Selected) |
| Product modules | Scheduling, Patients/Accounts, Transactions/Codes, Insurance/eClaims/ERA, Accounting, Practice Management analytics, Charting/Tx Planning, Imaging, Rx/Labs, Security/Utilities, Sensei integrations |
| Roles / workflows | Front Desk, Hygienist, Dental Assistant, Treatment Coordinator, Office Manager (from Help TOC) |
| Keystrokes | F1 Help, F3 Account, F4 Provider, F5 Patient, F8 ADA, F10 menus |
| Office doctrine | Launch `.lnk -sus`, Sign On COMPUTE, Excel/Preview only, period $ vs ops lane |
| Electronic Services | Separate `ECSHELP.hlp` topics (claim validation, payer lists) |

**Honesty:** Full Help topic *prose* for every TOC entry is **referenced** (name + `.htm` / Carestream URL), not copy-pasted verbatim into git. Rebuild anytime from the local CHM extract.

---

## How the PROGRAM knows it

| Artifact | Role |
|----------|------|
| `softdent_product_kb.json` | Machine KB (~676 KB) |
| `softdent_product_kb.py` | `load_*`, `lookup_report`, `lookup_help_topics`, HAL formatter |
| `scripts/build_softdent_product_kb.py` | Rebuild from Help extract |
| HAL local policy | `policy:softdent-product-kb` |
| LLM inject | `compile_softdent_signon_guidance` when product questions hit |
| API | `GET /api/apex/hal/softdent-kb?q=Account+Aging` |

Automation catalogs stay separate and authoritative for pulls:

- `softdent_gui_menu_map.json`
- `softdent_master_reports.json`

**Full product ≠ full automation.** NR2 still only GUI-pulls the money/ops subset; the KB teaches what SoftDent *is* and which Help report exists when staff ask.

---

## Rebuild

```text
hh -decompile C:\SoftDentReportExports\softdent_help_extract C:\SoftDent\WinHelp\SoftDent_OnlineHelp_OH_DE1010.chm
python NewRidgeFinancial2\scripts\build_softdent_product_kb.py
python -m unittest NewRidgeFinancial2.test_softdent_product_kb -v
```

---

## Ask HAL examples

- “Describe the SoftDent product Help catalog”
- “What SoftDent Practice Management reports exist?”
- “SoftDent charting / treatment plan in the full product”
- API: `/api/apex/hal/softdent-kb?q=unsubmitted+claims`
