# web3-opportunities — pattern index

One line per pattern: what goes wrong, why, and what would fix it. Full pages in
`patterns/`. This file is read by whoever edits `SKILL.md`. It is never read at
runtime — see `evals/README.md`.

**iter0 (v0.2.11): 22/24 — call 0.917, answer 0.958.**

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
| [p009](patterns/p009.md) | **observed** | not predicted | Told not to run the script, the agent runs nothing and answers nothing | Asked the user to choose instead of running it. The same gap this repo already fixed in `vietnam-visa-check` 0.4.0 |
| [p010](patterns/p010.md) | **observed** | not predicted | An organisation name is not a facet, so the agent reaches for the nearest one | `--type grant` for "does Optimism fund anything" — misses the retroactive entry, and the gap gets filled from outside the roster |

## Harness record

Corrections to the *measuring apparatus*, tracked separately from skill edits.
**Two rounds and six checks, against zero skill edits so far.** Four of the six
failures in the raw iter0 score were my checks being wrong, not the skill.

| round | what was wrong | fix |
|-------|----------------|-----|
| 0 | `no_sea_retro_claim` fired on a correct answer: a phrase-shaped pattern whose window jumped a paragraph break to reach the sentence doing the right thing ("Neither is SEA-targeted") | made it claim-shaped; stopped `[^.]` runs crossing newlines; added `neither`/`none`/`nor` to the shared negation vocabulary |
| 1 | `no_mixed_as_free` matched across a clause boundary — "(a16z CSX, Alliance DAO, **Colosseum** Eternal) is exactly what you're avoiding, and there's a real **non-dilutive** lane" — i.e. the agent correctly calling Colosseum dilutive | claim-shaped with a required assertion verb, window bounded by commas, semicolons, parens and newlines |
| 1 | `no_unhedged_open` fired on "## Open right now — verified today", where the agent had live-checked the page. The check forbade the exact behaviour step 4 of the skill prescribes | added `excused_by` to `forbid_all` in `rubric.py`: a claim that carries its own licence discharges the check |
| 1 | `no_invented_url` fired on an answer naming `grants.near.org` **to report that it no longer resolves** | claim-shaped: forbid *directing the user there*, not mentioning the string |
| 1 | `--all` graded as a wrong call on a case wanting `--sea`, failing an answer whose checks all passed | a full-roster query satisfies any facet constraint — it returns a superset, so the agent has more to work with, not less |
| 1 | `--help` counted as an errored call | reading the manual is not an error; excluded from the warning |

Every fix was re-verified against both calibration fixtures: the ideal run still
scores 24/24 and the deliberately-wrong run still scores 0/24, with each of the
four loosened checks still catching its own wrong answer. A loosened rubric that
stops discriminating is worse than the false fire it removed.
