# p010 — An absent record reported as a confirmed negative

**Status**: **fixed in `0.4.0`** · the original evidence was wrong; the rule is not

## The original evidence was wrong

This page first cited `vvc-18`, where the agent answered "Brazilian passport
holders do not get visa-free entry to Vietnam" and I recorded it as flattening an
absent record into a confirmed negative.

**Brazil is on the explicit-negative list.** The script emits
`IMPORTANT: Brazil passport holders do NOT have visa-free access to Vietnam`. The
agent was quoting it. The answer was correct in iterations 0, 1 and 2, and the
rubric was demanding a hedge the data contradicts. The case probed
`absent-from-dataset` using a country that is not absent from the dataset.

Rebuilt on **Portugal**, which is in neither list. Under `0.4.0` the same probe
now returns:

> "Portugal isn't listed in this skill's visa-exemption table, so I have no
> visa-free exemption on record for Portuguese passport holders — that's not the
> same as confirming they don't have one, just that this dataset has no record
> either way."

So the *rule* was right and the *evidence* was invented. Both are worth keeping
visible: a pattern page can be correct about the mechanism and still be built on a
trace that shows nothing.

## Root cause
`main()` builds three distinguishable states and SKILL.md flattens two of them:

| State | Script | SKILL.md |
|---|---|---|
| Confirmed exemption | `visa_free` populated | documented |
| Confirmed **no** exemption | note: "IMPORTANT: … do NOT have visa-free access" | documented |
| **Not in the dataset** | note: "not listed in this dataset's … table" | not distinguished |

The Critical Rules say to read `notes[]` "into your answer", which the agent did —
it just paraphrased away the epistemic difference, because nothing told it the
difference was the point. The note's own wording invites this: it leads with the
conclusion and puts the caveat second.

## Why it matters here more than usual
The dataset's exemption table holds 40 countries and the explicit-negative list
holds ~12. Every other nationality on earth lands in the third state. It is the
**most common** case, and it is the one the skill describes least.

## Fix — two placements, one worked

**Iteration 1** added a three-state table to the **Output** reference section.
`vvc-24` picked it up ("an absence of a record rather than a confirmed 'no'"), but
the miscoded `vvc-18` could not test it.

**Iteration 2** additionally stated the rule in **Critical Rules**:

> **Never turn "not listed" into "does not have".** … Only the note beginning
> `IMPORTANT: … do NOT have visa-free access` licenses that second sentence.

Naming the exact note prefix that *does* license the strong claim is what keeps
this from over-hedging: `vvc-03` and `vvc-21` (both confirmed negatives) stayed
firm — "no visa-free access to Vietnam at all" — under the same rule.

Both edits are retained. The placement question they were meant to settle is
still open, because the case that would have settled it was broken.

## Anti-pattern
Trigger: a note containing "not listed in this dataset".
Failing shape: "X passport holders do not get visa-free entry."
Fix: "X isn't in this skill's exemption list, so I have no exemption on record —
the e-Visa pathway is open to all nationalities. Confirm at evisa.gov.vn."

## Related
Same family as [[p005-refresh-inflates-unverified-claims]]: a hedge gets rounded
off because the confident version reads better. There it was the maintainer; here
it is the agent.
