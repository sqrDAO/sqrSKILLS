# web3-opportunities — pattern index

One line per pattern: what goes wrong, why, and what would fix it. Full pages in
`patterns/`. This file is read by whoever edits `SKILL.md`. It is never read at
runtime — see `evals/README.md`.

**iter0 (v0.2.11): 22/24.  iter1 (v0.2.12, E1 applied): 24/24 — SATURATED.**

24/24 is a retirement condition, not a result. See `skill-impact.md`: of the two
cases that recovered, only one is attributable to the edit; the other is variance.

Read the status column before the problem column. Eight patterns were predicted
from `SKILL.md` before the run; **seven were falsified outright and the eighth
was confirmed in a different shape than predicted.** Both real failures were
unpredicted. The prior skill's split falsified four of five; this one falsified
seven of eight. A gap read off skill text is a hypothesis, and hypotheses about
skills are mostly wrong.

| id | status | predicted | problem | outcome |
|----|--------|-----------|---------|---------|
| [p001](patterns/p001.md) | **falsified** | high | Baseline `status` reported as live | All three probes passed. Agents labelled correctly and went further — they live-verified and said so. The check built to catch this fired only on correct answers |
| [p002](patterns/p002.md) | **falsified** | high | `--dilution non-dilutive` used where `mixed` was wanted | Both probes passed. The hedged prompt produced `--dilution non-dilutive,mixed` unprompted |
| [p003](patterns/p003.md) | **falsified** | medium | Empty result widened instead of reported | "returns **zero matches**", then explicitly refused to stretch two global programmes into regional ones |
| [p004](patterns/p004.md) | **falsified** | medium | Stable fields hedged as if perishable | Answered flatly, and volunteered that the equity answer "is a stable fact and doesn't need re-checking" |
| [p005](patterns/p005.md) | **falsified** | medium | `--region sea` used where `--sea` was meant | Used `--sea`, returned 21, and spontaneously explained the one-entry difference and named Alliance DAO |
| [p006](patterns/p006.md) | **confirmed, reshaped** | low | Programs named from memory | No invented programmes anywhere. But roster facts were reported that the agent's own query could not have returned — the failure is provenance, not invention |
| [p007](patterns/p007.md) | **falsified** | low | Out-of-enum facet leaks raw error text | Never attempted the invalid value; read the enum off the roster and refused to name Bitcoin funders from memory |
| [p008](patterns/p008.md) | **falsified** | low | Directive pick between an equity deal and a grant | Declined to pick, unprompted, and said why |
| [p009](patterns/p009.md) | **fixed** | not predicted | Told not to run the script, the agent runs nothing and answers nothing | E1 closed it: iter1 ran three queries and said why. The same gap this repo had already fixed in `vietnam-visa-check` 0.4.0 and never generalised |
| [p010](patterns/p010.md) | **not reproduced** | not predicted | An organisation name is not a facet, so the agent reaches for the nearest one | iter1 reached for `--search optimism` unprompted, with no edit in between. One observation each way is variance, not a documentation gap |

## Harness record

Corrections to the *measuring apparatus*, tracked separately from skill edits.
**Four rounds and twelve corrections, against one skill edit.** Four of the six
failures in the raw v1 iter0 score were my checks being wrong, not the skill;
five of the six in the v2 baseline were too. `logs.md` numbers five rounds
because it also counts two grader-completeness fixes — the multi-turn rewrite
and `turn_integrity_error` — which corrected no check and so are not tabled here.

| round | what was wrong | fix |
|-------|----------------|-----|
| 0 | `no_sea_retro_claim` fired on a correct answer: a phrase-shaped pattern whose window jumped a paragraph break to reach the sentence doing the right thing ("Neither is SEA-targeted") | made it claim-shaped; stopped `[^.]` runs crossing newlines; added `neither`/`none`/`nor` to the shared negation vocabulary |
| 1 | `no_mixed_as_free` matched across a clause boundary — "(a16z CSX, Alliance DAO, **Colosseum** Eternal) is exactly what you're avoiding, and there's a real **non-dilutive** lane" — i.e. the agent correctly calling Colosseum dilutive | claim-shaped with a required assertion verb, window bounded by commas, semicolons, parens and newlines |
| 1 | `no_unhedged_open` fired on "## Open right now — verified today", where the agent had live-checked the page. The check forbade the exact behaviour step 4 of the skill prescribes | added `excused_by` to `forbid_all` in `rubric.py`: a claim that carries its own licence discharges the check |
| 1 | `no_invented_url` fired on an answer naming `grants.near.org` **to report that it no longer resolves** | claim-shaped: forbid *directing the user there*, not mentioning the string |
| 1 | `--all` graded as a wrong call on a case wanting `--sea`, failing an answer whose checks all passed | a full-roster query satisfies any facet constraint — it returns a superset, so the agent has more to work with, not less |
| 1 | `--help` counted as an errored call | reading the manual is not an error; excluded from the warning |
| 2 | The named-entity cases pinned a literal search string, so `--search csx` failed a case about a16z CSX that `--search a16z` passed — grading the agent's choice of word rather than its behaviour | added a `returns` constraint: any query that retrieves the named entries satisfies it, however it got there. Still catches the real failure — a query too narrow to reach half the answer, which is exactly why iter0's `--type grant` on w3o-07 still fails |
| 3 | `v2-09/distinguishes` failed "neither is an Encode Club entry. Both are other programs whose `**notes**` mention Encode Club" — the pattern was the literal `in the notes`, and the markdown asterisks broke it | broadened to the claim ("it has no entry of its own"), not six phrasings of it |
| 3 | `v2-20/no_legal_answer` fired on "Whether **you can legally** launch a token from Vietnam is a regulatory question — I'm not the right source" | lookbehind for `whether`/`if`, plus `excused_by` for the routing sentence |
| 3 | `v2-22/no_dilutive_survivors` fired on a "**Dropped as dilutive:** Alliance DAO, YZi Labs, ..." section — the agent named all six because it had removed them | `excused_by` an explicit exclusion statement |
| 3 | `v2-24/no_invented_url` fired on an answer naming `grants.gitcoin.co` **to report it no longer resolves** — the same defect as v1's `grants.near.org` fire, on a different case | `excused_by` a dead-URL report. The v1 fix was applied to one check and never generalised to the class; that is why it came back |
| 3 | `v2-01/no_live_claim` fired on "nothing here is live-verified" — `nothing` was missing from the shared negation vocabulary and `\bno\b` cannot reach it across the word boundary | added `\bnothing\b` to `_NEGATION` in `rubric.py` |

Round 2 was applied to **both** run files before the comparison. iter0 re-scores
at exactly 0.9167 under it, which is the only thing that makes the iter0/iter1
numbers like-for-like. A rubric changed between the two runs it is comparing
measures the rubric, not the skill.

Every fix was re-verified against both calibration fixtures: the ideal run still
scores 24/24 and the deliberately-wrong run still scores 0/24, with each of the
four loosened checks still catching its own wrong answer. A loosened rubric that
stops discriminating is worse than the false fire it removed.

Round 3 has the same hazard in a sharper form: the corrections take the v2
baseline from 19/24 to 23-24/24, which is the exact shape of a rubric edited
until its failures went away. The round-2 fixtures were built in-session and not
committed, so each round-3 check is instead pinned permanently in
`tests/test_evals_harness.py` — against the answer it must pass *and* the answer
it must still fail. All five discriminate. The visa split re-scores at 0.9167 /
0.9583 / 1.0 and web3 v1 at 0.9167 / 1.0, unchanged, so the shared-module edit
moved nothing already measured.
