# Remaining skills review — 11 September 2026

Baseline: `4d1bbb6` on main. Scope: the three Telegram skills, nearby search,
Luma, and business-model-to-market. These are the six without the recent
substantive reviews recorded for the other skills. No installable skill changed.

## Recommended order

| Priority | Skill | Main finding | Audit |
|---|---|---|---|
| P1 | telegram-group-summary | A supposedly passive read changes the update subscription; its primary reader skips transcript files | [Audit](telegram-group-summary.md) |
| P1 | nearby-places-search | A London lookup returns Hanoi coordinates from an unrelated memory section | [Audit](nearby-places-search.md) |
| P2 | telegram-send | Formatting rewrites literal code; successful sends do not return JSON | [Audit](telegram-send.md) |
| P2 | business-model-to-market | Missing scores become zero; explicit false answers become TBD | [Audit](business-model-to-market.md) |
| P2 | list-telegram-chats | Nanobot update timestamps are read under the wrong key | [Audit](list-telegram-chats.md) |
| P2 | luma-calendar | Transport failures escape the JSON interface; current API contract needs reconciliation | [Audit](luma-calendar.md) |

P1 means fix soon because the normal workflow can produce materially wrong
results or affect the running bot. P2 means a concrete correctness/integration
defect. P3 means a lower-impact improvement. API migration proposals and prompt
behavior hypotheses are explicitly separated from reproduced bugs in each audit.

## Method and limits

Read every substantive file in the six skill packages: prompts, Python helpers,
seven GTM references, JSON example, workbook cell contents/formulas, and DOCX
template text. Ignore filesystem AppleDouble `._*` sidecars. Use the same six
skill-evolution dimensions, scored 0–5 (higher is better), with code or prompt
locations supporting every row. These are editorial audit scores, not measured
agent success rates. Routing comments compare the stated task boundaries; no
retrieval/triggering experiment was run.

[probe.py](probe.py) invokes actual helpers with temporary state, dummy
credentials, fixed time, and mocked network calls. [evidence.json](evidence.json)
records the observed behavior. It is review evidence, not a prompt validation
split. No real bot, calendar, guest, private history, or Places account was used.

```bash
python3 docs/reviews/2026-09-11-remaining-skills/probe.py
# Include the optional documented workbook dependency from an isolated install:
python3 docs/reviews/2026-09-11-remaining-skills/probe.py --dependency-dir /tmp/sqrskills-review-deps
```

Without openpyxl, the probe explicitly skips workbook execution. This review
used openpyxl 3.1.5 installed under `/tmp`; all four workbook modes generated and
reopened successfully (11, 1, 1, and 2 sheets). Formula expressions and cell
values were inspected. No Excel/LibreOffice recalculation or visual rendering
was performed. No speculative prompt edits or new evaluation campaign was run.

## Checks

- Repository validator: passed, 13 skills.
- Unit tests: all 192 passed with network access. The initial sandbox run had
  one DNS error in `AnchorTargetSafetyTests.test_public_url_is_allowed`; it was
  environmental, and the unrestricted rerun passed. The existing suite has no
  dedicated behavioral tests for these six skills.
- `check_unanchored.py --since origin/main`: passed, zero new unanchored instruments.
- Cited policy datasets were not modified; a full dataset anchor sweep was not needed.
- Script probes reproduced the findings; positive controls include JSON history,
  basic bold conversion, and the four workbook generation modes.

The confirmed script defects are being addressed under the separate
`todo.remaining-skills-fixes.md` spec. The audit files and `evidence.json` remain
the pre-fix baseline record; the probe script is updated alongside the fixes so
it can verify the corrected behavior. Prompt improvements remain labelled
UNGATED unless a permitted measurement supports them.
