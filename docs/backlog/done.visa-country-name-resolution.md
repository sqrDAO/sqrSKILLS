# Vietnam visa country-name resolution

**Deps**: vietnam-visa-nationality-resolution

## Goal
Make `vietnam-visa-check` resolve a country's own name wherever it resolves that
country's demonym. `--nationality Ireland` currently errors with an empty
suggestion list while `--nationality Irish` answers correctly. Surfaced by an
eval trace (`evals/vietnam-visa-check/runs/iter0.jsonl`, `vvc-24`), where the
agent recovered only by retrying with the ISO code `IE`.

## Defects
1. `build_country_index()` indexes dataset ISO2 codes, dataset country names,
   `_ALIASES` and `_DEMONYMS`. `_COUNTRY_NAMES` is built separately by
   `build_display_names()` and feeds output only — it never enters the index.
   **26 of 81 display names do not resolve to their own ISO2**: Argentina,
   Austria, Bangladesh, Colombia, Cyprus, Egypt, Estonia, Greece, Iceland, Iran,
   Ireland, Israel, Latvia, Lithuania, Malta, Nepal, Nigeria, Pakistan, Peru,
   Portugal, Qatar, Saudi Arabia, Serbia, Sri Lanka, Turkey, Ukraine.
2. `suggest_nationalities()` draws candidates from the display-name table, so 17
   of the 26 fail and then suggest the exact string that just failed —
   `Argentina` → `suggestions: ["Argentina"]`. SKILL.md tells the agent to ask the
   user to confirm a suggestion, so the user confirms the word they already typed
   and it fails again.
3. The other 9 return no suggestions, and SKILL.md then sends the agent to ask for
   "the country name or ISO alpha-2 code" — which the user has already given.
4. `test_every_dataset_country_has_a_demonym` walks the two dataset sections only.
   The 26 affected countries are exactly those outside the dataset, so no existing
   test reaches them.

## Files
- `vietnam-visa-check/scripts/query_visa.py` (edited) — index `_COUNTRY_NAMES`
- `vietnam-visa-check/SKILL.md` (edited) — bump patch version
- `tests/test_vietnam_visa_check.py` (edited) — round-trip invariant
- `docs/backlog/PRIORITY.md` (edited) — queue entry
- `docs/backlog/todo.visa-country-name-resolution.md` (new) — this spec

## Design
In `build_country_index()`, add `_COUNTRY_NAMES` values as keys mapping to their
ISO2, inserted **before** the `_ALIASES`/`_DEMONYMS` pass so those keep winning on
conflict and the p002 ordering guarantee is untouched. Dataset names continue to
take precedence over the bundled table for any country present in both, so the
dataset stays the source of truth for display and for lookup.

Add the invariant as a test rather than a fixed list, so a country added to
`_DEMONYMS` later cannot reintroduce the gap: for every `iso2 → name` in
`build_display_names()`, `resolve_nationality(name, index) == iso2`.

Defect 2 needs no separate fix — once names resolve, they stop reaching the
suggestion path. Add one regression case asserting that no suggestion list
contains the input that produced it, so the self-referential shape cannot return.

## Acceptance
- [x] `Ireland`, `Argentina`, `Portugal`, `Ukraine`, `Turkey` each resolve to
      their ISO2 and return a pathway
- [x] Every name in `build_display_names()` resolves to its own ISO2
- [x] No suggestion list contains the exact input that produced it
- [x] `Irish`, `Russians`, `UK`, `USA`, `VN`, `TL` are unchanged
- [x] Aliases and demonyms still beat dataset names on conflict
- [x] `vietnam-visa-check` version bumped from `0.3.6`
- [x] NOT: a bundled full ISO 3166 table, silently auto-accepted fuzzy matches,
      or a non-stdlib dependency

## Verify
- `python3 vietnam-visa-check/scripts/query_visa.py --nationality Ireland` → `IE`
- `python3 scripts/validate_skills.py` → `"ok": true`
- `python3 -m unittest discover -s tests -v` → all tests pass
- `python3 evals/scripts/build_visa_cases.py --check` → `"ok": true`

## Notes
Implemented 2026-08-29; `vietnam-visa-check` bumped to `0.4.0`. Verified by
temporarily reverting the fix: 3 of the 4 new tests fail against the old code.
Completion approved by the user on 29 August 2026 after verifying #36 and merging #37-#39.

Defect 2 is the user-visible one: an error that suggests its own input is worse
than an error with no suggestions, because SKILL.md's contract sends the agent
into a loop. Same class as the p002 shortcut — a resolution table that exists but
is not consulted on the path users actually take.
