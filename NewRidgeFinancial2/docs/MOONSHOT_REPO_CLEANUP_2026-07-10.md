# Moonshot AI — Repo Cleanup: Files to Get Rid Of

**Date:** 2026-07-10  
**Model:** kimi-k2.5  
**Key:** OPENROUTER_API_KEY  
**Endpoint:** https://api.moonshot.ai/v1/chat/completions  
**Status:** ok  
**Script:** `scripts/run_moonshot_repo_cleanup_consult.py`

---

# Verdict
The repository contains approximately **6.1 GB** of data, with the live NR2 runtime (`NewRidgeFinancial2/` + `app_data/`) accounting for **3.7 GB**. The remaining **2.4 GB** is legacy debris, recreatable virtual environments, and local evaluation artifacts that can be safely archived or deleted. The `app_data/` folder holds live SQLite state and document inbox cache—**do not touch without backup**. Everything else in the root is superseded by the Bottle-based NR2 stack.

## 1. Immediate SAFE DELETE (do today)
- **`dist/`** — Legacy React/Vite build output (superseded by NR2/site/) — **191.0 MB**
- **`node_modules/`** — Legacy frontend npm dependencies — **39.6 MB**
- **`.tmp/`** — Runtime temp debris — **2.2 MB**
- **`.pytest_cache/`** — Python test cache — **0.6 MB**
- **`__pycache__/`** — Bytecode cache — **negligible**
- **`_softdent_reset_20260618_104345/`** — Empty reset scratch folder — **0 MB**
- **Root eval artifacts** (all `235b_eval_*.txt`, `235b_ctx_*.txt`, `235b_*.raw.json`, `235b_*.md`, `hal_120b_*.txt`, `hal_120b_*.json`, `hal_120b_*.md`, `hal_235b_raw.json`, `hal_diag_*`, `hal_fix_*`, `hal_lmstudio_*`, `hal_llama33_*`, `hal_second_opinion_ui_results.txt`, `falcon180_hal_*`, `gemma2_hal_program_*`, `eval_section*.raw.json`, `eval_section*_report.md`, `run_120b_program_eval.py`, `run_235b_eval_section.py`, `run_dual_model_eval_section.py`, `run_falcon180_hal_humanization_eval.py`, `run_gemma2_hal_program_eval.py`, `run_llama33_accounting_eval.py`, `FINAL_RELEASE_READINESS_REPORT.md`, `MULTI_MODEL_PIPELINE_REPORT.md`, `BROAD_PAGE_WORK_UNCOMMITTED_SAFETY_PATCH_README.md`, `hal_100_hightech_widgets_report.md`) — Local-only eval debris (gitignored, never commit) — **~5 MB**

## 2. ARCHIVE (move off hot path, keep 30–90 days)
Move to `_archive/2025-01-13/` or external drive:
- **`_legacy/`** — Frozen previous FastAPI app (reference only per README) — **554.2 MB**
- **`frontend/`** — Legacy React/Vite source (reference only per README) — **428.4 MB**
- **`.venv/`** — Python virtual environment (recreatable via `requirements.txt`) — **1063.3 MB**
- **`app/`** — Orphaned root FastAPI backend (distinct from `_legacy/app/`; superseded by NR2) — **3.5 MB**
- **`AI_Workspace/`** — Local AI workspace (gitignored) — **64.2 MB**
- **`DataAnalysisExpert/`** — Local analysis workspace (gitignored) — **18.2 MB**
- **`local-llm-benchmark/`** — Unused benchmark suite — **53.2 MB**
- **`.local_logs/`** — Session logs — **9.7 MB**
- **`hal_local.sqlite3`** — Old local HAL vector DB state (gitignored) — **5.1 MB**
- **`hal_chroma/`** — Chroma vector store debris — **4.4 MB**
- **`local_ai_finance/`** — Local runtime data (gitignored) — **0.4 MB**
- **`local_accounting_inbox/`** — Empty local inbox (gitignored) — **0 MB**
- **`_seeded_backup_20260618_103017/`** — Old seeded backup — **0 MB**
- **`evals/`** — Legacy eval directory — **0.1 MB**
- **`scripts/run_moonshot_*.py`** — One-shot AI consult scripts (21 files) — **negligible**

## 3. KEEP (required for live NR2)
- **`NewRidgeFinancial2/`** — Live Bottle app + site/ runtime — **251.8 MB**
- **`app_data/`** — **LIVE** SQLite state + document inbox cache (3465.4 MB). **Do not delete without full backup.** This is the production data store.
- **`scripts/`** — Ops scripts (`start_program.ps1`, `start_workstation.ps1`, `hal_evaluate_all.ps1`, `run_all_checks.ps1`, `Close-Legacy-Dependabot-PRs.ps1`, etc.) — **~1.2 MB** (minus moonshot files)
- **`docs/`** — Canonical documentation — **8.2 MB**
- **Root launchers:** `StartProgram.bat`, `StartWorkstation.bat`, `StartNewRidgeFinancial2.bat`, `StopProgram.bat`, `StopNewRidgeFinancial2.bat`, `StopDashboard.bat`, `RefreshDesktopShortcuts.bat`, `RefreshWorkstationShortcut.bat`, `BuildWorkstationPackage.bat`
- **Root config:** `.env.example`, `requirements.txt`, `README.md`, `ARCHITECTURE.md`, `CHANGELOG.md`, `CONTRIBUTING.md`, `SECURITY_HEADERS.md`, `CODEOWNERS`, `.gitignore`, `.trufflehogignore`, `cspell.json`, `cspell-project-terms.txt`, `Dockerfile.sandbox`, `.devcontainer/`
- **`.vscode/`** — Editor settings — **0.1 MB**
- **`assets/`** — Runtime assets — **0.1 MB**

## 4. INVESTIGATE before touching
- **`app/`** — Verify no active import references this root FastAPI backend. If confirmed unused (likely), archive it.
- **`hal_local.sqlite3`** — Confirm NR2 is not using this for HAL vector storage before archiving (likely superseded by in-memory or other stores).

## 5. Root clutter file groups (eval reports, 235b/120b/falcon dumps)
Delete all files matching these patterns in the repo root:
- `235b_*.txt`, `235b_*.json`, `235b_*.md`, `235b_ctx_*.txt`
- `hal_120b_*.txt`, `hal_120b_*.json`, `hal_120b_*.md` (exclude `hal_evaluate_all.ps1`)
- `hal_235b_raw.json`, `hal_diag_*`, `hal_fix_plan*.md`, `hal_fix_prompt*.txt`, `hal_lmstudio_*`
- `hal_llama33_*.txt`, `hal_llama33_*.json`, `hal_llama33_*.md`
- `falcon180_hal_*.txt`, `falcon180_hal_*.json`, `falcon180_hal_*.md`, `falcon180_hal_*.json`
- `gemma2_hal_program_*.json`, `gemma2_hal_program_*.md`, `gemma2_hal_program_context.txt`
- `eval_section*.raw.json`, `eval_section*_report.md`, `eval_section*_70b.raw.json`
- `run_*_eval.py` (exclude `run_all_checks.ps1`)
- `FINAL_RELEASE_READINESS_REPORT.md`, `MULTI_MODEL_PIPELINE_REPORT.md`, `BROAD_PAGE_WORK_UNCOMMITTED_SAFETY_PATCH_README.md`, `hal_100_hightech_widgets_report.md`, `hal_second_opinion_ui_results.txt`

## 6. Duplicate / dead stacks (frontend/, app/, dist/, AI_Workspace/, etc.)
- **`frontend/`** — Dead React/Vite stack (superseded by `NewRidgeFinancial2/site/`)
- **`app/`** — Orphaned FastAPI backend (superseded by `NewRidgeFinancial2/browser_app.py`)
- **`_legacy/`** — Explicitly frozen reference snapshot (FastAPI + old frontend-src)
- **`dist/`** — Build artifact of dead frontend stack
- **`AI_Workspace/`** — Local experiment workspace (not part of live app)
- **`DataAnalysisExpert/`** — Local analysis workspace (not part of live app)
- **`local-llm-benchmark/`** — Unused benchmark harness

## 7. scripts/ Moonshot consult hygiene
**Archive (move to `scripts/_archive/moonshot/`):**
All one-shot consult scripts:
- `run_moonshot_all_pages_hightech_relayout_consult.py`
- `run_moonshot_comprehensive_consult.py`
- `run_moonshot_elite_remaining_batches.py`
- `run_moonshot_elite_to_live_schema.py`
- `run_moonshot_full_program_mockup_audit.py`
- `run_moonshot_gpu_model_consult.py`
- `run_moonshot_hal_page_design.py`
- `run_moonshot_hightech_elite_pages.py`
- `run_moonshot_hightech_visual_consult.py`
- `run_moonshot_issues_4_6.py`
- `run_moonshot_issues_4_6_part3.py`
- `run_moonshot_mock_only_schema_consult.py`
- `run_moonshot_mockup_fix_comparison.py`
- `run_moonshot_mockup_no_overlay_consult.py`
- `run_moonshot_mockup_widget_eval.py`
- `run_moonshot_plan_compare.py`
- `run_moonshot_plan_comparison.py`
- `run_moonshot_repo_cleanup_consult.py` (keep until this cleanup is done, then archive)
- `run_moonshot_softdent_extract_analysis.py`
- `run_moonshot_system_hal_redesign_consult.py`
- `run_moonshot_workstation_plan_comparison.py`
- `run_moonshot_workstation_sidenotes_consult.py`

**Keep in `scripts/`:**
- `start_program.ps1`, `start_workstation.ps1`, `start_nr2_browser.ps1` (if present)
- `hal_evaluate_all.ps1`, `run_all_checks.ps1`
- `Close-Legacy-Dependabot-PRs.ps1`
- `Verify-HAL-Readiness.ps1`, `Sync-HAL-Imports.ps1`, `Sync-HAL-Document-Sources.ps1` (import automation)

## 8. Operator cleanup commands (PowerShell)
Run from repo root (`C:\NewRidgeFamilyFinancial`). **Backup `app_data/` first.**

```powershell
# Setup archive folder
$date = Get-Date -Format "yyyy-MM-dd"
$archive = "C:\NewRidgeFamilyFinancial\_archive\$date"
$root = "C:\NewRidgeFamilyFinancial"
New-Item -ItemType Directory -Path $archive -Force

# 1. Archive legacy stacks (large, recreatable)
Move-Item "$root\_legacy" "$archive\"
Move-Item "$root\frontend" "$archive\"
Move-Item "$root\app" "$archive\"  # Confirm unused first (see INVESTIGATE)
Move-Item "$root\.venv" "$archive\"

# 2. Archive workspaces and local data
Move-Item "$root\AI_Workspace" "$archive\"
Move-Item "$root\DataAnalysisExpert" "$archive\"
Move-Item "$root\local-llm-benchmark" "$archive\"
Move-Item "$root\.local_logs" "$archive\"
Move-Item "$root\hal_local.sqlite3" "$archive\"
Move-Item "$root\hal_chroma" "$archive\"
Move-Item "$root\local_ai_finance" "$archive\"
Move-Item "$root\local_accounting_inbox" "$archive\"
Move-Item "$root\_seeded_backup_20260618_103017" "$archive\"

# 3. Archive moonshot consults
New-Item -ItemType Directory -Path "$archive\moonshot_consults" -Force
Get-ChildItem "$root\scripts" -File | Where-Object { $_.Name -match '^run_moonshot_' } | Move-Item -Destination "$archive\moonshot_consults\"

# 4. Archive root eval debris by pattern
New-Item -ItemType Directory -Path "$archive\root_eval_artifacts" -Force
$patterns = @('235b_*', 'hal_120b_*', 'hal_235b_*', 'hal_diag_*', 'hal_fix_*', 'hal_llama33_*', 'hal_lmstudio_*', 'hal_second_opinion_*', 'falcon180_hal_*', 'gemma2_hal_program_*', 'eval_section*', 'run_*_eval.py', 'FINAL_RELEASE_READINESS_REPORT.md', 'MULTI_MODEL_PIPELINE_REPORT.md', 'BROAD_PAGE_WORK_UNCOMMITTED_SAFETY_PATCH_README.md', 'hal_100_hightech_widgets_report.md')
Get-ChildItem "$root" -File | Where-Object { 
    $f = $_.Name
    foreach ($p in $patterns) { if ($f -like $p) { return $true } }
    return $false
} | Move-Item -Destination "$archive\root_eval_artifacts\"

# 5. Safe delete build artifacts and caches
Remove-Item "$root\dist" -Recurse -Force
Remove-Item "$root\node_modules" -Recurse -Force
Remove-Item "$root\.tmp" -Recurse -Force
Remove-Item "$root\.pytest_cache" -Recurse -Force
Remove-Item "$root\__pycache__" -Recurse -Force
Remove-Item "$root\_softdent_reset_20260618_104345" -Recurse -Force

Write-Host "Cleanup complete. Archived items are in $archive"
```

## 9. Expected disk savings summary
| Action | Target | Size |
|--------|--------|------|
| **SAFE DELETE** | Build artifacts, caches, root eval debris | **~240 MB** |
| **ARCHIVE** | Legacy stacks, .venv, workspaces, local DBs | **~2.14 GB** |
| **KEEP** | Live NR2 runtime + app_data (production) | **~3.73 GB** |
| **Total Declutter** | Working set reduction | **~2.4 GB** |

## 10. Do-not-touch list
- **`app_data/`** (3.5 GB live cache) — Contains production SQLite DBs and document inbox. Backup before any operations.
- **`NewRidgeFinancial2/`** (252 MB) — Live application runtime (Bottle + site/).
- **`.env`** (if present, not shown in inventory but implied) — Secrets and local config.
- **Root batch launchers** (`StartProgram.bat`, `StartWorkstation.bat`, `StopProgram.bat`, etc.) — Required to run the live app.
- **`scripts/start_*.ps1`** — Required startup scripts.
- **`docs/`** — Canonical project documentation.