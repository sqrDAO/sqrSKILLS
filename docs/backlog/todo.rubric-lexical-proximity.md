# Replace the rubric's lexical proximity heuristics with clause structure

**Deps**: web3-opportunities-eval-split

## Goal
`rubric.py` decides two things by looking at characters near a match: whether a
forbidden claim is negated, and whether an `excused_by` phrase discharges it. Both
are proximity heuristics standing in for grammar, and CodeRabbit found the seam in
each on #46. Neither is fixable alone — they are the same defect twice.

**Negation.** `negated()` takes a 40-character window and splits on `[.!?\n]`. A
colon is not a terminator, so any negation reaches across one:

    passes  Nothing prevents this: it is live-verified.
    passes  No doubt about it: it is live-verified.
    passes  Never mind that: it is live-verified.

Only the first was reported. The other two use `no` and `never`, which predate the
`nothing` added on #46 — so restricting `nothing` alone would leave four words with
the identical property, which is worse than fixing all or none.

**Excuses.** `excused_by` discharges the *whole check* when its phrase appears
anywhere in the answer. "You can legally launch a token ... (see
vietnam-crypto-radar)" excuses `v2-20/no_legal_answer` on the bare mention of the
other skill; the same shape applies to `dropped as dilutive` and `no longer
resolves`.

Sentence-scoping the excuse is NOT the fix. Measured on #46:

| split | before | sentence-scoped |
|---|---|---|
| visa iter0/1/2 | 0.9167 / 0.9583 / 1.0 | unchanged |
| web3 v1 iter0/iter1 | 0.9167 / 1.0 | 0.9167 / **0.9583** |
| web3 v2 A/B | 0.9583 / 1.0 | **0.875 / 0.9583** |

with `v2-22` a stable failure. In `v2-22` the excuse is a section heading
(`Dropped as dilutive:`) and the hits are list items under it, so a sentence
window cannot reach them. The unit is a section, not a sentence, and it differs
per check.

## Files
- `evals/scripts/rubric.py` (edited) — the scoping rewrite
- `tests/test_evals_harness.py` (edited) — the counterexamples above, plus the
  answers each split's stored runs depend on
- `evals/web3-opportunities/wiki/logs.md` (edited) — a harness round entry

## Acceptance
- [ ] All three colon counterexamples fail, and the observed "no web access, so
      nothing here is live-verified" still passes
- [ ] An excuse in one section does not discharge a hit in another; `v2-22`'s
      heading-scoped excuse still discharges the list beneath it
- [ ] The stored runs re-score at their recorded values, or every deviation is
      explained in the log as a check that was wrong before
- [ ] NOT: restrict `nothing` alone; NOT: sentence-scope excuses (measured above)
- [ ] NOT: change a case's prompts or probes — this is the apparatus, not the split

## Verify
- `python3 -m unittest discover -s tests -v` and `python3 scripts/validate_skills.py`
- `python3 evals/scripts/grade_visa.py evals/vietnam-visa-check/runs/iter{0,1,2}.jsonl`
  → `0.9167 / 0.9583 / 1.0`
- `python3 evals/scripts/grade_web3.py evals/web3-opportunities/runs/iter{0,1}.jsonl`
  → `0.9167 / 1.0`
- v2 A/B against `cases-v2.jsonl` → the values current at the time, with any
  change attributed

## Notes
This is round 6 of harness corrections. The ratio in `index.md` — corrections to
the apparatus versus edits to the skill — gets worse again, which is the honest
reading: the thing doing the measuring has been wrong more often than the thing
being measured, every round so far.

Worth deciding before starting whether a regex rubric is still the right shape.
Every round has been a proximity heuristic failing on a construction nobody
anticipated, and the fix has always been a narrower window.
