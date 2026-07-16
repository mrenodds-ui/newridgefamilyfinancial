# Moonshot AI — Cloud PMS Parity Augmentation (CONSULT ONLY)

**Date:** 2026-07-16
**Model:** `kimi-k2.5`
**Key:** OPENROUTER_API_KEY
**Status:** ok
**Repo root:** `C:\Users\mreno\newridgefamilyfinancial`
**Build:** `nr2-12073-excel-gate-all-next`
**Script:** `scripts/run_moonshot_cloud_pms_parity_consult.py`
**Apply:** DO NOT APPLY until operator approves.

## Operator request (verbatim)

> with what i have now and the information you just got, can i augment my program to function comparitily to these cloud based programs

---

# Verdict
**YES, partial parity achievable for financial/operational/administrative pillars (claims intelligence, revenue analytics, period-close governance); NO, full PMS parity impossible (clinical charting, scheduling, eRx remain SoftDent-native due to write-back prohibition); adopt a hybrid overlay architecture integrating Lighthouse 360 and Jarvis-style analytics rather than replacing the clinical PMS.**

## 0. Operator Intent (verbatim)
> with what i have now and the information you just got, can i augment my program to function comparitily to these cloud based programs

## 1. What "comparable" means for NR2 (scope boundary)
"Comparable" for NR2 does **not** mean replacing SoftDent with a cloud-native PMS. It means achieving **functional parity in financial operations, claims lifecycle management, and executive analytics**—the domains where Curve/Ascend charge premium fees—while SoftDent retains exclusive ownership of clinical records, scheduling, and eRx. NR2 becomes the **financial system of record** (shadow now, cutover later) and the **intelligence layer** that cloud PMS vendors monetize, without migrating clinical data.

**Boundary conditions:**
- SoftDent remains the sole clinical database; NR2 stays read-only (Excel/Print Preview ingestion only).
- NR2 does not host PHI-rich clinical charts; it handles fiscal intermediates (claims, ledgers, ERA, eligibility) with board-ready initials+hash anonymization.
- "Comparable" equals **Curve Insights + Curve Pay visibility + Jarvis Analytics KPIs**, not Curve Hero scheduling or Ascend clinical charting.

## 2. Capability parity matrix (10 pillars × NR2 today / gap / augment path)

| Pillar | NR2 Today | Gap vs. Cloud PMS | Augmentable? | Path or Never |
|--------|-----------|-------------------|--------------|---------------|
| **1. Scheduling + Online Booking** | None; SoftDent desktop only | Full cloud scheduler, patient self-booking | **NEVER** | Write-back to SoftDent forbidden; online booking would create orphan appointments. Use SoftDent native or Lighthouse 360 integration. |
| **2. Clinical Charting / Imaging / eRx** | None | Perio charts, X-ray PACS, e-prescribe | **NEVER** | NR2 is fiscal overlay; clinical data stays in SoftDent. No imaging storage or prescription write-back. |
| **3. Treatment Planning + Case Presentation** | None | Visual treatment plans, patient consent forms | **NEVER** | Requires clinical chart write access; prohibited. |
| **4. Insurance / Claims / ERA / Ledger** | Trellis eligibility scrape, ERA inbox, SoftDent claims outstanding view (`C:\SoftDentFinancialExports\softdent_financial_analytics.db`), period-close shadow mode | Real-time batch eligibility, automated claim scrubbing, electronic attachment submission | **AUGMENTABLE** | Enhance Trellis polling frequency; add ERA auto-posting suggestions to QB; build "Claim Health" optical page. Cannot submit claims (SoftDent retains submitter ID). |
| **5. Patient Engagement** | HAL local chat (`http://192.168.50.244:8765`) | Two-way texting, recall automation, digital forms, reviews | **AUGMENTABLE** | Integrate **Lighthouse 360** (PMS-agnostic, SoftDent-compatible) via API; NR2 acts as data bridge for financial messaging. |
| **6. Reporting / Analytics / KPIs** | Money beams (SoftDent AR + QB revenue), desk smoke validation, `periodCloseStatus` | Morning Huddle dashboards, provider production rankings, hygiene recall mining | **AUGMENTABLE** | Build Jarvis-style optical pages (`nr2-optical-page-analytics.html`) parsing `softdent_financial_analytics.db` and QB payroll; add "Morning Bundle" Excel gate. |
| **7. Payments (Integrated Processing)** | QB revenue import only | Curve Pay / integrated merchant services | **NEVER** | NR2 tracks revenue integrity; payment processing remains in QB Merchant Services or SoftDent Pay. No card vaulting in NR2. |
| **8. Multi-location / DSO Admin** | Single office (`officeHubData`: `C:\Users\mreno\newridgefamilyfinancial\app_data\nr2\office`) | Enterprise rollup, cross-office scheduling | **PARTIAL** | Augmentable for **financial consolidation** (multi-office QB + SoftDent feeds into single NR2 shadow close); not for clinical cross-scheduling. |
| **9. Anywhere Browser/Mobile Access** | Local LAN HAL hub (`192.168.50.244:8765`), desktop Chrome | iOS/Android apps, cloud browser login | **LIMITED** | Deploy Zero Trust VPN tunnel to HAL hub; never full SaaS (SoftDent desktop anchor). |
| **10. Automated Updates / Cloud Backup** | NR2 build `nr2-12073-excel-gate-all-next` auto-updates; SoftDent manual | Cloud-native backup, automatic PMS updates | **PARTIAL** | NR2 layer auto-updates; SoftDent remains on-premise backup responsibility. |

## 3. What NR2 already beats cloud PMS at
1. **Money Honesty (Empty ≠ $0):** Cloud PMS dashboards often display `$0.00` when data is stale; NR2 explicitly distinguishes "No Signal" from zero dollars via `emptyNotZero` beams and `dataBeamHash` integrity checks.
2. **SoftDent + QuickBooks Bridge:** Cloud PMS (Curve, Ascend) force you into their GL; NR2 preserves QB independence while shadow-validating SoftDent ledger accuracy—true fiduciary surface.
3. **Local AI (HAL) without Cloud BAA:** HAL runs at `192.168.50.244:8765` with no OpenAI/Azure PHI egress; cloud PMS AI requires Business Associate Agreements and data residency proofs.
4. **Period-Close Laser Precision:** Shadow mode (`systemOfRecord=false`) allows 30+ days of parallel financial validation before cutover; cloud PMS migrations are big-bang with no rollback.
5. **Read-Only Safety:** NR2 cannot corrupt SoftDent historical data; cloud PMS conversions often corrupt history during import.

## 4. Recommended augmentation strategy (phased P0–P3, REAL files, validation gates)

### P0: Foundation Hardening (Week 1)
**Goal:** Stabilize data ingestion before adding features.
- **Fix SoftDent Excel Gate:** Execute `NewRidgeFinancial2/docs/runbooks/softdent_excel_enablement_nr2.md` to enable Excel Output Options (not greyed). Validate at `C:\SoftDentReportExports\` with `register_for_period_{start}_{end}.xls`.
- **Ship Desk Smoke Script:** Create `C:\Users\mreno\newridgefamilyfinancial\NewRidgeFinancial2\desk_smoke.py` to validate `moneyBeams.beamHash` vs `dataBeamHash` match, `periodCloseStatus`, and `forceCloseAvailable` every 5 minutes.
- **Repair beamVerify Endpoint:** Fix HTTP 404 on beam verification route (referenced in `c5de424` commit) to enable formal desk proof.
- **Validation Gate:** Operator attests SoftDent Excel exports land in `C:\SoftDentReportExports\` without "Printer" selection; desk smoke runs 24h without `beamVerify` mismatch.

### P1: Financial Intelligence Layer (Weeks 2–4)
**Goal:** Achieve Jarvis-analytics parity for fiscal data.
- **Trellis AM Automation:** Schedule `scripts/prove_trellis_withbenefits_am.py` nightly at 10:10 PM (after SoftDent 9:00 PM pull) to populate eligibility cache.
- **ERA Inbox Parsing:** Enhance `app_data\nr2\office\era_inbox\` with 835 ERA parsing to suggest QB bill-pay adjustments (read-only suggestions, operator approves).
- **Enhanced Claims Optical:** Build `nr2-optical-page-claims.html` with live `claimsOutstanding` from `C:\SoftDentFinancialExports\softdent_financial_analytics.db`, filtered by payer aging.
- **Validation Gate:** Money beams show `<24h` freshness for both SoftDent AR and QB revenue; desk smoke `status: GREEN` for 7 consecutive days.

### P2: Patient Engagement Bridge (Weeks 5–6)
**Goal:** Lighthouse 360 integration for engagement without replacing SoftDent scheduling.
- **Lighthouse 360 API Sync:** Bidirectional sync: NR2 pushes financial recall triggers (patients with >$500 outstanding + last visit >6mo) to Lighthouse; Lighthouse pushes appointment confirmations back to SoftDent (standard Lighthouse capability).
- **HAL Financial Messaging:** Extend HAL hub to generate patient financial narratives ("You have a $220 copay pending from March 10") for staff to paste into Lighthouse 360 two-way texting.
- **Validation Gate:** Staff can generate a "financial recall list" in NR2 and send via Lighthouse without opening SoftDent Insurance Reports.

### P3: Hybrid Architecture Documentation (Week 7)
**Goal:** Formalize the overlay model for compliance and DSO scaling.
- **Architecture Doc:** `C:\Users\mreno\newridgefamilyfinancial\NewRidgeFinancial2\docs\architecture\hybrid_pms_overlay.md` defining NR2 as "Financial Shadow System of Record" alongside SoftDent "Clinical System of Record."
- **Cutover Runbook:** `docs/runbooks/nr2_cutover_to_sor.md` detailing the 30-day shadow → supervised → cutover attestation workflow (`minShadowDays: 30`).
- **Validation Gate:** Document signed; `systemOfRecord` remains `false` until operator attestation.

## 5. What NOT to build (stay in lane)
- **SoftDent Write-Back Modules:** Never build APIs that post payments, adjustments, or new patients to SoftDent; violates read-only constraint and risks database corruption.
- **Clinical Charting UI:** No perio charts, tooth graphics, or eRx interfaces; stay in fiscal metadata.
- **Native Payment Processor:** Do not build card vaulting or merchant services; leverage QB Merchant Center or SoftDent Pay.
- **Online Scheduling Widget:** Conflicts with SoftDent as sole scheduler; use Lighthouse 360 for this layer.
- **Third-Party Chat Embeds:** No Tawk.to, PushEngage, or Intercom on NR2 pages; use HAL local chat only.

## 6. Hybrid architecture recommendation (NR2 + SoftDent + optional Lighthouse/Jarvis?)
**The "Fiduciary Overlay" Model:**
- **SoftDent Desktop:** Retains clinical charting, scheduling, imaging, eRx, and claim submission (PMS-of-Record for clinical).
- **NR2 (Local HAL/Optical):** Serves as **Financial System of Record** (shadow now, cutover later) with period-close governance, QB reconciliation, and Trellis eligibility intelligence.
- **Lighthouse 360 (Cloud):** Patient engagement layer (reminders, texting, forms) integrated to SoftDent; NR2 feeds financial recall lists to Lighthouse but does not handle the messaging UI.
- **Jarvis Analytics (Optional Cloud):** If NR2 Jarvis-style dashboards (P1) are insufficient, subscribe to Jarvis for clinical KPIs; NR2 provides the financial denominator that Jarvis lacks (true cost per procedure from QB payroll).

**Data Flow:**
```
SoftDent (Clinical) --Excel/Preview--> NR2 (Financial Intelligence) --API--> Lighthouse 360 (Engagement)
      |                                        |
      v                                        v
Trellis (Eligibility)                    QuickBooks (GL/Payroll)
```

## 7. Executive Summary (5 bullets)
- **Scope Reality:** NR2 can match cloud PMS **financial and administrative** capabilities (claims, revenue analytics, period-close) but cannot and should not replace clinical charting or scheduling.
- **Hard Limit:** SoftDent write-back prohibition makes NR2 a **read-only intelligence layer**, not a PMS migration target.
- **Immediate Blocker:** SoftDent Excel export must be enabled (`softdent_excel_enablement_nr2.md`) before any augmentation; desk smoke script validates data integrity.
- **Competitive Advantage:** NR2's "Money Honesty" (empty≠$0) and QB+SoftDent bridge provide fiscal visibility that pure cloud PMS (Curve, Ascend) cannot match without expensive custom integrations.
- **Path Forward:** P0 hardening → P1 analytics → P2 Lighthouse bridge; never build clinical features or payment processing.

## 8. Approval Checklist
- [ ] **P0:** SoftDent Excel Output Options confirmed active (not greyed) with screenshot of `Reports → Account Aging → Output Options → Excel` selected.
- [ ] **P0:** Desk smoke script `desk_smoke.py` deployed and logging to `C:\Users\mreno\newridgefamilyfinancial\logs\desk_smoke.jsonl` with 24h of `beamHash` match confirmations.
- [ ] **P1:** Trellis `withBenefits` AM proof script scheduled and producing >0 eligibility hits for 3 consecutive mornings.
- [ ] **P2:** Lighthouse 360 API credentials stored in `app_data\nr2\office\lighthouse_config.yaml` (no PHI in repo; use initials+hash).
- [ ] **Governance:** Signed attestation that NR2 remains `systemOfRecord: false` until 30-day shadow period completes and cutover ceremony executed.
