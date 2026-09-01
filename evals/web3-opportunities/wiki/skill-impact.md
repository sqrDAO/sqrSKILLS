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

## E2 after the v2 baseline — still withheld, and now for a different reason

v2 ran at two repeats on 2026-08-29 (`runs/v2-iter0-a.jsonl`, `runs/v2-iter0-b.jsonl`):
**23/24 and 24/24, mean 0.979, call 1.0 in both, `stable_failures: []`.**

E2 was blocked on not having repeats. It now has them, and the answer is that
there is nothing to gate. E2 targets `v2`'s organisation-name-is-not-a-facet
pattern (p010); the call score is **1.0 across all 48 case-runs**, so the
behaviour E2 would document did not fail once. An edit cannot earn its keep
against a score with no room above it.

**E2 stays unapplied.** Not because it is wrong — because there is no longer any
measurement that could tell.

## The v2 split is saturated on its first baseline

The same retirement condition as v1 and as `vietnam-visa-check`, reached in one
run instead of two. The single failure (`v2-02`) is in `unstable_cases`: it
failed in repeat A and passed in repeat B, and by this split's own rule such a
case must never be credited or debited to an edit.

That is now three splits in a row that saturate. The honest read is that the
thing being measured has stopped being the binding constraint: across 48
case-runs the agents ran the right queries every time, labelled baseline data,
live-verified when it mattered, refused a false premise, declined an
out-of-scope legal question, and reported catalog gaps unprompted. The failures
this round were all in the *rubric*.

Two consequences for whoever picks this up:

1. **Do not build v3 the same way.** A fourth split of hand-written probes over
   the same catalog will saturate too. What repeatedly *did* surface real
   defects is the data, not the instructions — v2's agents independently found a
   stale `sui.io/grants` 404, a dead `grants.gitcoin.co`, an expired
   `opgrants.io` registration, a closed Polkadot Open Source Developer Grants
   bounty still cited as live, and a missing Superteam India. A split that
   grades *roster freshness* would have failed today.
2. **The one open judgement call is `v2-02`**, and it is a question about the
   skill's intent rather than the harness: with the web off and no Bitcoin entry,
   is naming OpenSats/Spiral/Btrust from memory — explicitly labelled as
   out-of-catalog, with no amounts, dates or status, and told to verify — a
   violation of "never invent programs", or the best available answer? Left
   failing pending a decision, rather than excused into a pass.
