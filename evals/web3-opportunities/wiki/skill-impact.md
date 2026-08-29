# web3-opportunities — skill edits

Every proposed edit to `SKILL.md`, its diff, its score, accepted or rejected.
Rejected edits stay here permanently: the record is what stops the same idea
being re-proposed six weeks later.

Skills roll back. This file does not.

## Score history

| iteration | version | pass_rate | call | answer | note |
|-----------|---------|-----------|------|--------|------|
| iter0 | 0.2.11 | 0.9167 | 0.9167 | 0.9583 | baseline; 22/24 |

## Proposed, not yet applied

Neither has been written into `SKILL.md`. An edit that has not been gated on a
re-run is a guess, and this split has just finished demonstrating that guesses
about this skill are wrong seven times in eight. Both are queued behind a run.

### E1 — the standing rule holds when the user waives it (p009)

`w3o-15` told the agent not to run scripts. It ran nothing, named nothing, and
asked the user to choose between two ways of getting the answer. The Critical
Rule says "ALWAYS run `query_opportunities.py` before listing opportunities" but
never says it outranks the user's instruction, so the agent read it as a default
rather than a rule.

This exact gap was found and closed in `vietnam-visa-check` 0.4.0, whose rule now
reads "**This holds even when the user asks you not to run it.**" The fix was
never generalised to the other script-backed skill. Proposed edit is the same
sentence, plus the instruction to keep the answer as short as the user asked for.

Confidence this is real: **high** — it is observed, not predicted, and the same
defect has already been confirmed and fixed once in this repo.

### E2 — an organisation name is not a facet (p010)

`w3o-07` asked "does Optimism fund anything?" and the agent ran `--type grant`,
which cannot return `optimism-retro-funding`. The `--search` example is in the
Usage block, but the core method says "query the roster **with the user's
facets**", and an organisation name is not one of the six facets. Proposed edit
adds a line to the core method: when the user names a programme or organisation
rather than a facet, `--search` is the query.

Confidence: **medium**. The answer was still right, because the agent filled the
gap from a live lookup — so the user-visible cost is provenance, not correctness,
and it is possible no edit is warranted at all.

## Not proposed, and why

The six harness corrections in `index.md` are not skill edits and must not be
counted as improvement. Four of them raised the score by fixing checks that
failed correct answers. The skill did not change between 18/24 and 22/24.
