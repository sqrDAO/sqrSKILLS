# p002 — Alias shadowed by the ISO2 shortcut

**Status**: confirmed · fixed in `0.3.0` (PR #20)

## Symptom
`--nationality UK` returned `EVISA`. A British traveller was told to buy a USD 25
e-Visa they do not need — confidently, silently, with no error anywhere.

## Root cause
A "looks like an ISO2 code" shortcut accepted 1–3 letters and ran *before* the
alias index. `UK` was taken as the literal code `UK`, which matches no dataset
entry, so the exemption lookup missed and the generic e-Visa fallback answered.
`USA` did the same and rendered as the country name "Usa". `XYZ` reached `EVISA`
with no error at all.

## Why it is the dangerous class
p001 was loud: the user saw a failure and asked again. This was quiet. The output
was well-formed, plausible, and wrong. The backlog spec says it directly — *"Defect
3, not the reported symptom, is the real risk."*

## Fix
The alias/demonym index is consulted first; the bare-code path accepts exactly two
alpha characters and nothing else. An unmatched two-letter code now carries an
explicit note that nothing in the dataset matched, so the e-Visa answer is not
mistaken for a positive result.

## Anti-pattern
Any resolution order where a permissive syntactic guess outranks an exact table
lookup. Order tables before heuristics.

## Guards
`ResolutionTest::test_aliases_beat_the_iso_code_shortcut`,
`CommandLineTest::test_uk_is_visa_free`, `test_unknown_code_carries_an_explicit_note`.

## Validation cases
`vvc-02`, `vvc-18`.
