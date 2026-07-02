# Falcon 180B HAL Humanization — Triage

**Date:** 2026-07-02  
**Judge:** `falcon:180b` (101 GB, CPU/RAM lane)  
**Subject:** `hal-chat:8b` (DeepSeek-R1 8B + HAL Modelfile)  
**Report:** `falcon180_hal_humanization_report.md`  
**Samples:** `falcon180_hal_subject_samples.json`

## Verdict

Falcon's judge pass completed but returned a **generic** review (misread the task as end-user chatbot personalization). **Actionable signal came from the subject samples + existing `qwen_second_opinion_system.txt` rubric**, not from Falcon's prose.

## Sample failures (pre-fix)

| Prompt | Issue |
|--------|-------|
| `ops-brief` | Dashboard recap tone; markdown `**` artifact |
| `softdent-risk` | Missing insurance + A/R lead; bullet list; "If you need further analysis" closing |
| `quickbooks-guardrail` | "Would you like me to:" bullets; missing explicit read-only first sentence |
| `claims-followup` | Unrequested numbered steps |
| `owner-tone` | Three paragraphs + numbered steps instead of two steady operator paragraphs |

## Root cause

Production HAL used **minimal Modelfile SYSTEM prompts** and **`hal-core.js` buildSystemPrompt** without the human voice rules already written in `evals/prompts/qwen_second_opinion_system.txt` (eval-only until this pass).

## Fixes applied

1. **`hal-core.js`** — `humanVoicePromptLines()` with teammate tone + scenario rules (QB guardrail, collections/A/R+insurance, denied claims, operating picture).
2. **`hal-agent.js`** — agent policy reinforces plain paragraphs, no chatbot closings.
3. **`Modelfile.hal-chat-8b`** / **`Modelfile.hal-helper-14b`** — teammate voice + key scenario hints.
4. **Recreated** `hal-chat:8b` and `hal-helper:14b` via `ollama create`.
5. **Eval pipeline** — `run_falcon180_hal_humanization_eval.py`, context builder, Falcon profile in `local_model_profiles.json`.

## Re-run eval

```powershell
python run_falcon180_hal_humanization_eval.py --collect-samples --rebuild-context
python run_falcon180_hal_humanization_eval.py --rebuild-context
```

Or: `scripts/run_falcon180_hal_humanization_eval.ps1`

## Operator spot-check

Try in HAL chat:

1. "Give me the current HAL operating picture for today in two short paragraphs."
2. "SoftDent collections are trailing production. What should I look at first?"
3. "Can you post this QuickBooks adjustment for me right now?"
4. "Talk to me like a steady operator… what matters most this morning?"

Expect: two short paragraphs where asked, no bullet lists, no "let me know", QB refusals lead with read-only.
