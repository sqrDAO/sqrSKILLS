# p001 — Demonym input unresolved

**Status**: confirmed · fixed in `0.3.0` (PR #20)

## Symptom
"Hows the visa for Russians?" produced a raw `run … query_visa.py failed` bubble
in the user's own conversation. No answer, visible tool failure.

## Root cause
`resolve_nationality()` matched three things: ISO2 codes, dataset country names,
and 17 aliases. Users do not type any of those. They type what they call
themselves — a demonym, usually plural, often with a qualifier
("Russian citizens", "German passport holders").

## Fix
Four-step resolution, first match wins: normalize (casefold, strip punctuation,
drop leading `the`, drop trailing qualifiers) → exact lookup against
names + ISO2 + `_ALIASES` + `_DEMONYMS` → retry with trailing `s` stripped →
accept a bare two-letter code. Plural country names (`Laos`, `Philippines`)
resolve at step 2, before the depluralizer can damage them.

## Anti-pattern
The agent "helpfully" maps the user's word to a country name before calling:
`Russians` → `--nationality Russia`. This masks resolver gaps — the failure moves
from a visible error to a silent dependency on the agent guessing right, which is
exactly how [[p002-alias-shadowed-by-iso-shortcut]] stayed invisible.

## Rule now in SKILL.md
> Pass the user's own wording through directly; do not translate it to a country
> name yourself.

## Guards
`tests/test_vietnam_visa_check.py::ResolutionTest::test_demonym_forms`,
`test_multiple_demonyms_per_country`, `test_every_dataset_country_has_a_demonym`.

## Validation cases
`vvc-01`, `vvc-02`. The grader reports `translated_inputs` separately so the
anti-pattern shows up even when the answer happens to be right.
