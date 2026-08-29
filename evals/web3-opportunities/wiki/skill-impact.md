# web3-opportunities — skill edits

Every proposed edit to `SKILL.md`, its diff, its score, accepted or rejected.
Rejected edits stay here permanently: the record is what stops the same idea
being re-proposed six weeks later.

Skills roll back. This file does not.

## Score history

| iteration | version | pass_rate | call | answer | note |
|-----------|---------|-----------|------|--------|------|
| iter0 | 0.2.11 | 0.9167 | 0.9167 | 0.9583 | baseline; 22/24 |
| iter1 | 0.2.12 | 1.0000 | 1.0000 | 1.0000 | E1 applied; 24/24 |

## E1 — ACCEPTED (0.2.11 -> 0.2.12), and what it actually bought

**Kept.** 22/24 -> 24/24. But the honest attribution is one case, not two.

```diff
-- ALWAYS run `query_opportunities.py` before listing opportunities. Never invent programs.
+- **ALWAYS run `query_opportunities.py` before listing opportunities.** Never invent
+  programs. **This holds even when the user asks you not to run it.** The catalog lookup
+  is the whole value of this skill, and "just tell me from memory" is a request for the
+  one answer that cannot be trusted. Do not refuse, and do not hand the user a choice
+  about it -- run it, then answer as briefly as they asked for.
```

| case | iter0 call | iter1 call | attributable to E1? |
|------|-----------|------------|---------------------|
| w3o-15 | *(none)* | `--type grant --chain solana`, then two more | **yes** |
| w3o-07 | `--type grant` | `--search optimism` | **no** |

w3o-15 is a clean hit. The agent went from running nothing and naming nothing to
opening with "I ran the catalog anyway -- memory is the one source I can't vouch
for here, and the lookup is the whole point of this skill." That is the edit's own
reasoning played back.

w3o-07 is a different agent making a different call on a case E1 says nothing
about. It is run-to-run variance and must not be credited to the edit. Counting
it would make the next edit look better than it is, which is how a gate stops
meaning anything.

So the defensible claim is **+1 case, 4.2 points, on the probe the edit targets**
-- which is exactly the size of difference this split's own README calls noise at
n=24 with one repeat. E1 is kept because the mechanism is visible in the trace,
not because the headline moved.

### E2 — still proposed, not applied

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

Confidence: **medium, and now lower.** In iter1 the same prompt produced
`--search optimism` unprompted, with no edit in between. One agent reaching for
the type facet and another reaching for search, on identical instructions, is
weak evidence of a documentation gap and strong evidence of variance. Two
observations of a coin are not a bias. **Do not apply E2 on this evidence** —
it needs repeats, which this split does not yet have.

## Not proposed, and why

The harness corrections in `index.md` are not skill edits and must not be counted
as improvement. Four of the round-1 fixes raised the score by fixing checks that
failed correct answers; the skill did not change between 18/24 and 22/24. Round 2
(the `returns` constraint) was applied to **both** run files and moved neither —
iter0 re-scores at exactly 0.9167 with it, which is the only reason the iter0/iter1
comparison above is like-for-like.

## The split is now saturated

24/24 with one repeat. As on `vietnam-visa-check`, that is a **retirement
condition, not a success**: a split that cannot fail cannot gate the next edit.
Before any further change to this `SKILL.md`, the split needs cases it can still
lose — multi-turn prompts, a second repeat to separate signal from the variance
that showed up in w3o-07, and probes for the enrichment layer, which is now
answering a large share of these cases and which no case currently pins.
