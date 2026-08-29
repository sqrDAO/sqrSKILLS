# p003 — A citizen offered a visa for their own country

**Status**: confirmed · fixed in `0.3.0` (PR #20, raised in review)

## Symptom
`--nationality VN` returned `recommended_pathway: EVISA` with a populated
`evisa_option`, next to a note saying Vietnamese citizens need no visa. The
record contradicted itself.

## Root cause
The first fix added a *note*. Notes are prose; the pathway fields are what a
caller reads. Any consumer that keys off `recommended_pathway` — including an
agent skimming for the headline — gets the wrong answer while the correction sits
one field away, unread.

## Fix
`VN` short-circuits ahead of all pathway logic *and* ahead of the
`--phu_quoc_only` branch, returning `NOT_REQUIRED` with `visa_free` and
`evisa_option` both null. The structured fields carry the answer; the note only
explains it.

## Anti-pattern
Correcting a structured output by appending prose to it. If the fields are wrong,
fix the fields. A note beside a wrong field is a comment, not a fix.

## Guards
`CommandLineTest::test_vietnamese_nationals_need_no_visa`,
`test_vietnamese_nationals_short_circuit_every_flag`.

## Validation cases
`vvc-16`, which fails if the answer mentions an e-Visa at all.
