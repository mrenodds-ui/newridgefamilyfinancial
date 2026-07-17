# Moonshot AI — NR2 Full Program Evaluation vs Cloud Dental PMS (CONSULT ONLY)

**Date:** 2026-07-17
**Model:** `kimi-k2.5`
**Key:** OPENROUTER_API_KEY
**Script:** `scripts/run_moonshot_nr2_vs_cloud_dental_pms_evaluation_consult.py`
**Audit JSON:** `C:/Users/mreno/newridgefamilyfinancial/.local_logs/moonshot_financial_eval/moonshot_nr2_vs_cloud_pms_audit_20260717T111047Z.json`
**Apply:** Consult/report only — operator must say continue / approve before any implementation.

## Operator request (verbatim)

> have moonshot ai evaluate the whole program for all issues and compare it to popular cloud based dental practice management systems and what can be done to close the gap and report

---

# Executive Verdict
NR2 is a fiduciary-grade financial overlay that successfully reconciles SoftDent AR ($52,270) with QuickBooks revenue ($78,399) via cryptographically verified money beams, but it remains operationally blocked by SoftDent’s intentional Excel extract restrictions and lacks automated ERA ingestion. The program is in Shadow pilot (Day 2 of 30) with forced safety gates preventing premature cutover, which is appropriate given the live failure of the collections morning bundle and absence of real 835 remittance files. While cloud PMS competitors offer native scheduling write-back and clinical charting, NR2’s local HAL architecture provides superior data sovereignty and honesty controls (empty≠$0) that cloud vendors cannot match; however, NR2 cannot close the clinical gap without becoming a full PMS, which is explicitly out of scope.

## 0. Operator Intent (verbatim)
> "financial/ops overlay on SoftDent+QuickBooks — not a full PMS"
> 
> **Hard Rules:**
> - SoftDent READ-ONLY no write-back
> - empty != $0
> - Output Options Excel|Print Preview only — never Printer/File
> - Excel grey = SoftDent intentional extract block (Preview optical-only)
> - PHI initials+hash
> - no third-party chat embeds

## 1. NR2 Program Identity (what it is / is not)
**Is:** A static HTML/JS optical desk served via local Python HAL (HTTPS loopback) that provides read-only financial intelligence, money beam reconciliation between SoftDent and QuickBooks, claims paid-suppress logic, and ERA inbox staging. It operates as a shadow system with cryptographic beam proofs (SHA-style hashes) ensuring data fidelity without write-back privileges.

**Is Not:** A practice management system replacement. NR2 does not write to SoftDent (no appointment booking, no clinical charting, no ledger adjustments), does not integrate imaging, and does not provide patient portals or two-way communication. It explicitly respects SoftDent’s "Excel grey" intentional extract blocks and never invents financial data (empty≠$0).

## 2. Live Issues Inventory (severity · evidence · impact)

| Severity | Issue | Evidence | Impact |
|---|---|---|---|
| **CRITICAL** | **SoftDent Excel Grey Block** | `softdentExcelGreyedLive: true`; Runbook `softdent_excel_enablement_nr2.md` exists but not executed; "Excel grey = SoftDent intentional extract block" confirmed in hard rules | Morning bundle cannot extract collections data; period close incomplete |
| **CRITICAL** | **Collections Morning Bundle Failed** | `morningBundle.failed: ["collections"]`; `okCount: 2`, `failed: 1`; status "partial" | Financial close integrity compromised; AR aging potentially stale |
| **HIGH** | **ERA 835 Pending (Empty Inbox)** | `realFileCount: 0`, `placeholderCount: 1` (README.txt only); `chipStatus: "staged"`; `gapCode: "ERA835_PENDING"` | Zero automated remittance processing; staff must manually post insurance payments to SoftDent |
| **MEDIUM** | **Trellis Benefits Awaiting** | `chipStatus: "awaiting"`; `withBenefits: 0` for all candidate dates; `trellisWithBenefitsWaitUntil: "~2026-07-20"` | Eligibility verification limited to status-only counts; no benefit detail for treatment planning |
| **LOW** | **Force Close Safety Gated** | `forceClose: false`; `forceCloseAvailable: false`; `patientAttestEligible: true` but `forceCloseLaserGated: true` | Prevents manual override of period close (correct by design, but blocks emergency close) |
| **INFO** | **Pilot Shadow Early Stage** | `shadowDaysElapsed: 2`, `shadowDaysRemaining: 28`, `shadowEligible: false` | System of record cutover impossible for minimum 28 days; attestation not yet signed |

## 3. Capability Scorecard vs Cloud PMS (table: Capability | Cloud PMS norm | NR2+SoftDent | Gap)

| Capability | Cloud PMS Norm (Dentrix Ascend/Curve/Denticon) | NR2+SoftDent Reality | Gap |
|---|---|---|---|
| **Scheduling** | Real-time online booking, multi-location capacity, automated reminders, write-back to main schedule | Optical read-only view; 93% appointment time coverage detected; Mon-Thu slot visibility; **no write-back** | **HIGH** |
| **Clinical/Charting** | Full EHR (perio charting, e-prescribe, treatment plans, progress notes) | `nr2_clinical_bridge.py` provides read-only data pull only; no charting UI | **HIGH** |
| **Imaging** | Integrated DICOM/PACS (Dexis, Sidexis, etc.) | Not addressed; no imaging modules in inventory | **HIGH** |
| **Billing/Claims/ERA** | Electronic claims submission, auto-posting ERA (835), real-time eligibility, payment processing | Claims tracking active ($52,270 AR beam); paid-suppress logic prevents false positives; **ERA inbox empty** (no 835s); eligibility status-only (0 benefit details) | **MEDIUM** |
| **Patient Engagement** | Two-way texting, portal access, digital forms, review generation | `nr2_consent_executor.py`, `nr2_narratives.py` for content; **no chat embeds** (per hard rules); no portal | **MEDIUM** |
| **Reporting/Analytics** | Standard dashboards, drill-down AR, production analysis | Money beams verified (SoftDent/QB hash match); `nr2_analytics.py`; Excel grey blocking some extracts | **LOW** (financially ahead) |
| **Multi-Location** | Native entity management, inter-office scheduling, consolidated reporting | Single location architecture evident; no multi-tenant logic detected | **MEDIUM** |
| **Mobile** | Native iOS/Android apps with full functionality | Responsive HTML/JS optical desk; local HTTPS loopback; no native app | **MEDIUM** |
| **Integrations** | Open APIs, marketplace apps (Weave, Dental Intel, Pearl AI) | QB live sync (working); SoftDent read-only; Trellis pending; **no third-party chat embeds** | **MEDIUM** |
| **Security/Compliance** | Cloud SOC 2 Type II, vendor-managed encryption, BAA with vendor | Local HAL (`nr2_tls.py`, `nr2_db_crypto.py`, `nr2_rbac.py`); operator-controlled keys; audit logs; **operator assumes all infrastructure risk** | **LOW** (different risk model) |
| **AI Assistance** | Integrated AI (Pearl for radiology, Dental Intel for analytics) | No AI modules detected; basic statistical analytics only | **HIGH** |

## 4. Where NR2 Is Ahead
- **Fiduciary Honesty:** Strict empty≠$0 enforcement prevents phantom revenue recognition; no invented 835 remittances or fake benefits data.
- **Beam Proof Integrity:** Cryptographic beam hashes (`beamHash: "d6a2ff0bf114dfe4"`) provide non-repudiable reconciliation between SoftDent and QuickBooks that cloud PMS often lack.
- **Local Data Sovereignty:** All PHI remains on-prem; no cloud vendor BAA required for core financial data; immune to cloud outages.
- **Paid Suppress Accuracy:** `nr2_claims_paid_suppress.py` prevents staff from accidentally working paid claims (4 staff-hidden claims detected), reducing compliance risk.
- **Read-Only Safety:** Impossible to corrupt SoftDent source data through NR2; cloud PMS migrations often risk data corruption during sync.
- **QB Integration Depth:** Live revenue beam ($78,399) suggests tighter QuickBooks integration than most cloud PMS offer (which often require manual journal entries).

## 5. Close-the-Gap Roadmap (P0/P1/P2 · effort · owner: Cursor vs Operator vs Vendor)

### P0 — Critical Path (Block Production)
| Package | Effort | Owner | Details |
|---|---|---|---|
| **A. SoftDent Excel Enablement** | 2h attended | **Operator** | Execute `softdent_excel_enablement_nr2.md` runbook to resolve grey block; required for collections bundle |
| **B. Collections Bundle Fix** | 4h dev | **Cursor** | Debug morning bundle failure; likely dependency on Excel enablement or path resolution in `nr2_softdent_daily.py` |
| **C. ERA 835 Drop Process** | 1h setup | **Operator** | Establish payer EDI drop process; place real 835 files in `C:\...\era_inbox\drop` (currently only README.txt) |

### P1 — High Value (Next 30 Days)
| Package | Effort | Owner | Details |
|---|---|---|---|
| **D. Trellis Benefits Activation** | Wait | **Vendor (Trellis)** | Awaiting ClearCoverage scrape (~2026-07-20); verify `withBenefits` counts populate |
| **E. Shadow Period Completion** | 30 days | **Operator** | Continue shadow operation; daily desk smoke verification; no cutover until Day 30 |
| **F. Supervised Period Prep** | 8h dev | **Cursor** | Build supervised mode workflows for Day 30-60 (attested human oversight) |

### P2 — Enhancement (Days 60-90)
| Package | Effort | Owner | Details |
|---|---|---|---|
| **G. Analytics Optical Pages** | 16h dev | **Cursor** | Expand `nr2-optical-page-analytics.html` with drill-down capabilities (respecting read-only) |
| **H. QB Payroll Inbox** | 4h setup | **Operator** | Implement `qb_ap_payroll_inbox_drop_nr2.md` for automated payroll imports |

### C. External Waits (Outside NR2 Control)
- **Trellis Nightly Scrape:** Activation estimated 2026-07-20; benefits data unavailable until then.
- **Carestream Sensei Migration Path:** Evaluate if/when to migrate from on-prem SoftDent to Sensei Cloud (would change NR2 integration pattern).
- **Payer EDI Enrollment:** Real-time ERA 835 availability depends on individual payer EDI agreements.

### D. Explicitly OUT OF SCOPE
- Replacing SoftDent clinical charting, imaging, or perio modules.
- Any write-back to SoftDent database (appointments, ledgers, clinical notes).
- Developing native mobile applications (iOS/Android).
- Integrating third-party chat widgets or patient portals.
- Becoming a full PMS; NR2 remains an overlay only.

## 6. What NOT To Do (anti-patterns)
- **Do not** enable SoftDent write-back capabilities to "fix" the scheduling gap; this violates the read-only safety model and risks data corruption.
- **Do not** invent or simulate 835 ERA data to populate the inbox; the empty≠$0 honesty principle is fiduciary critical.
- **Do not** force-close the period (`forceClose: true`) while `collections` bundle is failing; this destroys audit integrity.
- **Do not** skip the 30-day shadow minimum; current Day 2 status means cutover is prohibited regardless of business pressure.
- **Do not** install cloud-based chat widgets (Intercom, Drift, etc.) to fill the patient engagement gap; violates "no third-party chat embeds" hard rule.
- **Do not** attempt to bypass Excel grey blocks via screen-scraping or Print Preview OCR; use the attended runbook only.

## 7. 90-Day Recommended Sequence

**Days 1-30: Stabilization & Shadow**
- Day 1-3: Operator executes Excel enablement runbook; Cursor fixes collections bundle logic.
- Day 4-7: Operator establishes ERA 835 drop process with top 5 payers.
- Day 8-30: Continuous shadow operation; daily desk smoke logs reviewed; Trellis benefits activate (Day ~3-6 of this period).
- Gate: Collections bundle 100% success for 5 consecutive business days.

**Days 31-60: Supervised & ERA Maturation**
- Day 31: Enter Supervised mode (if shadow attestation signed); system suggests actions but operator confirms all posts.
- Day 31-45: Process live ERA 835s through NR2 inbox; verify auto-posting logic to QuickBooks (not SoftDent).
- Day 46-60: Refine analytics optical pages; train staff on money beam verification workflows.
- Gate: >95% of insurance remittances processed via ERA inbox; zero hash mismatches.

**Days 61-90: Cutover Evaluation**
- Day 61: Evaluate System of Record cutover eligibility (`shadowEligible: true` + `supervisedDaysElapsed: 30`).
- Day 61-75: Parallel operation stress test; volume testing with full schedule.
- Day 76-90: Board review of cutover attestation; decision to maintain overlay vs. migrate to Sensei Cloud.
- Gate: Board sign-off on `cutoverAttested` with named signatory.

## 8. Acceptance Gates for "gap closing"
- **Financial Integrity:** 30 consecutive days of MATCH beam proofs between SoftDent and QB; zero forced closes.
- **Collections Reliability:** Morning bundle reports (aging, register, collections) 100% automated extraction success for 10 consecutive business days.
- **ERA Maturity:** >95% of monthly insurance payments ingested as real 835 files (not manual entry); <24hr lag from receipt to NR2 visibility.
- **Trellis Activation:** Eligibility reports showing `withBenefits > 0` for >80% of scheduled patients.
- **Shadow Duration:** Minimum 30 days shadow + 30 days supervised completed (Day 60 minimum).
- **Security Audit:** Local HAL penetration test completed; RBAC roles verified; TLS 1.3 confirmed (`nr2_tls.py`).

## 9. Approval Checklist
- [ ] Board acknowledges NR2 is **overlay only** and does not replace SoftDent clinical or scheduling write-back.
- [ ] Operator has executed `softdent_excel_enablement_nr2.md` and confirmed Excel Output Options are no longer greyed.
- [ ] Collections morning bundle demonstrates 100% success rate (verified in `deskSmoke.checks`).
- [ ] ERA inbox process established with written procedure for dropping payer 835 files.
- [ ] Cyber insurance policy updated to cover "on-prem financial overlay software" (NR2).
- [ ] HIPAA risk assessment completed for local Python HAL and SQLite backup locations.
- [ ] Trellis integration tested and `withBenefits` counts verified as non-zero.
- [ ] Shadow period attestation signed by practice owner (named signatory in `attestationSignedBy`).
- [ ] Force Close safety gate acknowledged as permanent feature (not temporary bug).
- [ ] 90-day sequence approved with Go/No-Go decision scheduled for Day 60.
