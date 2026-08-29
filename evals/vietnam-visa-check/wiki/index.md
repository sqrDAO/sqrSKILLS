# vietnam-visa-check — pattern index

Diagnostic layer for the skill. **Not shipped, and not read at runtime.** The
executing agent sees `vietnam-visa-check/SKILL.md` and nothing here — that
separation is the point (see `../../README.md`).

Each entry names the problem, the root cause, and the fix specifically enough to
judge relevance without opening the page.

**Current**: `0.4.0`, 2026-08-29. Full 24-case run: **24/24**, `call` and
`answer` both 1.0 (`runs/iter2.jsonl`). Baseline `0.3.6` was 22/23 on the
comparable subset.

**The split is saturated and cannot gate the next edit.** A 100% means this one
has done its job, not that the skill is finished — see `logs.md` for what a
replacement needs.

Of nine seeded patterns, four were falsified outright, one (p010) had invented
evidence but a valid rule, one (p013) is real with no measurable effect, and one
(p012) was found inside a *passing* trace and is the most serious defect of the
set.

| # | Pattern | Status | Root cause → fix |
|---|---------|--------|------------------|
| [p001](patterns/p001-demonym-input-unresolved.md) | Users type demonyms ("Russians"); the resolver knew only names and ISO2 | fixed 0.3.0 · **anti-pattern recurring** | No demonym layer → `_DEMONYMS`, plural retry, qualifier stripping. 5/24 traces still rewrite the user's wording before calling |
| [p002](patterns/p002-alias-shadowed-by-iso-shortcut.md) | "UK" silently answered EVISA instead of VISA_FREE | fixed 0.3.0 | An ISO2 shortcut ran before the alias index → alias lookup moved ahead of it |
| [p003](patterns/p003-citizen-offered-a-visa.md) | Vietnamese nationals got `EVISA` plus a "no visa needed" note | fixed 0.3.0 | Note added without changing the fields → `NOT_REQUIRED` short-circuit, nulled options |
| [p004](patterns/p004-structured-error-as-tool-failure.md) | Unrecognised nationality rendered as a raw failure bubble | fixed 0.3.0 | `sys.exit(1)` on user input → exit 0 with `{error, hint, suggestions}` |
| [p005](patterns/p005-refresh-inflates-unverified-claims.md) | Weekly refreshes restored disproven claims and deleted caveats | corrected #25, #27, #33 | Facts rewritten without a source gate → tier-1 registry, absence-asserting tests |
| [p010](patterns/p010-absent-record-read-as-confirmed-negative.md) | "Not in this dataset" vs "does not have visa-free access" | **fixed 0.4.0** · evidence was wrong | The cited trace used Brazil, which *is* a confirmed negative. Rule valid, case rebuilt on Portugal → both edits retained |
| [p011](patterns/p011-standing-rule-overridden-by-user.md) | User said "don't run anything"; agent made zero tool calls | **fixed 0.4.0** | "ALWAYS run the script" stated no precedence against a user instruction → the lookup is not waivable. `call_score` → 100% |
| [p012](patterns/p012-country-name-unresolvable.md) | `Ireland` fails; `Irish` works. 26 of 81 display names unresolvable | **fixed 0.4.0** | `_COUNTRY_NAMES` fed output but never the index → folded in; 26 → 0 unresolvable, 17 → 0 self-echoing suggestions |
| [p013](patterns/p013-documented-output-schema-lags-the-script.md) | The script returns 5–8 fields the Output section never lists | documented in 0.4.0 · no measurable effect | Fields added to the script, not the docs → now listed; no case moved either way |
| [p006](patterns/p006-exemption-shorter-than-the-trip.md) | A populated `visa_free` that does not cover the trip | **falsified** | Predicted skim error; 4/4 passed. The generated note already explains the shortfall |
| [p007](patterns/p007-exemption-conditions-dropped.md) | Tourism-only and per-year caps dropped from the answer | **falsified** | Predicted with high confidence; 3/3 passed. Root cause was also factually wrong |
| [p008](patterns/p008-duration-not-extracted.md) | "two months" never reaches `--duration_days` | **falsified** | 2/2 passed; every prompt with a stated duration passed the right integer |
| [p009](patterns/p009-dataset-facts-with-no-route.md) | Land entry and FAQ answers unreachable from the documented interface | **falsified** | `evisa_option` already carries the answer; 0/24 traces read any other file |

## Where the evidence comes from

- `docs/backlog/done.vietnam-visa-nationality-resolution.md` — p001–p004
- `docs/backlog/done.vietnam-visa-policy-verification-corrections.md` — p005
- `runs/iter0.jsonl` — p006–p013
- `tests/test_vietnam_visa_check.py` — the regression surface for p001–p005

## Reading the falsifications

Four of nine seeded patterns died on contact with the first run, including the one
held with the highest confidence. That is the loop working, not failing — each was
a plausible gap read off the skill text, and reading a gap is not the same as
observing a failure.

Two further corrections came later and are worth more than the score:

- **p010's evidence was invented.** The trace cited Brazil, which is on the
  explicit-negative list, so the agent's "confident negative" was a direct quote.
  A pattern page can be right about the mechanism and still rest on a trace that
  shows nothing. It took writing a *second* case to find out.
- **The most serious defect (p012) came out of a trace that passed.** Nothing in
  the rubric was looking for it; it was visible only because run files record tool
  calls and because a passing case was read rather than skipped.

Net: of the two "real failures" reported after iteration 0, one was real. Of the
three defects actually fixed, two (p011, p012) were never predicted.
