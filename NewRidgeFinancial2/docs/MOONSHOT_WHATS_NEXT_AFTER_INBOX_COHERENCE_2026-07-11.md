# Moonshot AI — What's Next After Inbox Coherence (CONSULT ONLY)

**Date:** 2026-07-11  
**Model:** kimi-k2.5  
**Key:** OPENROUTER_API_KEY  
**Status:** ok  
**Build:** hal-10560  
**Script:** `scripts/run_moonshot_whats_next_after_inbox_coherence_consult.py`  
**Apply:** DO NOT APPLY until operator approves.

## Operator request (verbatim)

> next

---

# Verdict
Open the pull request for branch `fix/main-validate-ci` and merge it into `main` immediately to land the inbox sync coherence and import hardening that are currently trapped in the branch.

## 0. Intent
Shipped value is worthless until it is in `main`. The coherence fixes (content-hash no-ops, critical retention logic, bit-identical sync verification) are production protections currently isolated on a side branch; `main` is stale and exposed to the very data-drift risks the fixes mitigate. Do not start new features while the last delivery is still in limbo.

## 1. Already Done (do not redo)
- Expert SE REC-001..007 (gate split, threaded HTTPS, import health, ERA CAS/claims actions)
- Compact professional pages Phases 1–5
- Import gate hardening (softGaps warnings, stale-row detection, QB expenses=warning)
- Inbox sync coherence (retention soft-skip, content-hash no-op writes, Period expense protection, direct-first mirror, bit-identical sync verification) committed as `0dcf1d7`
- Documentation: `MOONSHOT_INBOX_SYNC_COHERENCE_APPLIED_2026-07-11.md`

## 2. Recommended NEXT (single package)
**Goal:** Create PR `fix/main-validate-ci` → `main` and merge (fast-forward acceptable if policy allows).  
**Why now:** The branch contains the hardened import gate and inbox coherence that prevent AR/dashboard/QB expense corruption. Every hour it sits unmerged increases the risk of a hotfix collision or an operator accidentally branching off stale `main`. The `gh auth login` blocker is a local environment issue; use the GitHub web UI or a token to open the PR if CLI remains blocked.  
**Effort:** Administrative (low).  
**Files:** None—repository operation only.  
**Validation gate:**  
- CI passes on the PR.  
- Post-merge, verify `main` HEAD is `0dcf1d7` (or descendant) and that `git log --oneline main..fix/main-validate-ci` returns empty.  
- Run the two-consecutive-syncs smoke test to confirm bit-identical results still hold on `main`.

## 3. Runner-up options (max 3)
1. **Git hygiene:** Add `site/index.pre-apex.html` to `.gitignore` and `git rm --cached` it to prevent accidental commit of the legacy untracked file.  
2. **NICE REC-008 (batch narratives):** Only after `main` is current; low urgency, high UX polish.  
3. **Credential fix:** Permanently resolve the `gh auth login` breakage (credential helper or token export) so future PRs are not blocked.

## 4. Approval checklist
- [ ] PR opened: base=`main`, compare=`fix/main-validate-ci`
- [ ] CI green (validate the coherence tests pass)
- [ ] Merged to `main` (merge-commit or fast-forward)
- [ ] Local `main` pulled and verified at commit `0dcf1d7` or later
- [ ] Branch `fix/main-validate-ci` deleted (optional but recommended)
- [ ] `site/index.pre-apex.html` added to `.gitignore` (optional hygiene)

DO NOT APPLY CODE.