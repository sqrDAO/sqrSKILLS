# web3-opportunities — log

Chronological, append only.

## 2026-08-29 — split built, not yet run

Second skill to get the loop, after `vietnam-visa-check`. Chosen because it is the
only remaining skill whose ground truth can be *generated*: an offline dataset
plus a deterministic query script, no network and no credentials. Five of the ten
skills in this repo call live APIs and cannot produce a reproducible answer key
without a fixture layer that does not exist yet; `vietnam-crypto-radar` ships
references but no script, so its truth would have to be hand-typed and would rot
against the next refresh.

24 cases, 8 probe families. Ground truth is the `count`/`ids`/`statuses` block
returned by `query_opportunities.py` itself, so a roster refresh re-derives the
answer key. Two rubric patterns (`<DATA_AS_OF>`, `<TRUTH_COUNT>`) are filled in
from that same output rather than typed, for the same reason.

Calibration before spending any run:

- A hand-written ideal answer for all 24 cases scores 24/24. This proves only
  that the rubric is satisfiable — I wrote both sides of it. Its real value is
  the other direction: a check that fails a good answer is a broken check, and
  one did (see the harness record in `index.md`).
- A deliberately wrong answer for all 24 — each committing the specific failure
  its case was built to catch — scores 0/24, and every case fails on the check
  that encodes its own probe rather than on something incidental. A case that
  cannot fail is worse than no case: it reports a success nobody observed.

Both fixtures live in the session scratchpad, not in the repo. What is worth
keeping is the numbers and the one correction they forced.

Shared grading machinery was extracted to `evals/scripts/rubric.py` at the same
time — negation-aware `forbid_all`, run-completeness refusal, the summary shape.
Those took four rounds to get right on the visa split and should exist once, not
twice. The visa split re-scores identically on all three stored iterations after
the extraction (0.9167 / 0.9583 / 1.0), including after the negation vocabulary
changed.

## 2026-08-29 — iter0, v0.2.11, 24 cases, 1 repeat

**22/24 — call 0.917, answer 0.958.** Raw first score was 18/24; four of the six
failures were defects in my own checks, fixed and logged in the harness record
before the number above was taken.

One fresh agent per case, each seeing the skill directory and nothing else, told
explicitly not to read `evals/`. Executors reported the argv they ran; the grader
normalises it by running `query_opportunities.py` and reading back the `query`
block, so the grader and the executor cannot disagree about what a flag meant.

### What the run did to the predictions

Seven of eight falsified, one confirmed in a different shape, and both real
failures unpredicted. Details in `index.md`. The pattern worth carrying forward:
the two highest-confidence predictions (p001 status labelling, p002 the dilution
gotcha) were the *most* thoroughly wrong. Agents did not merely label the
time-sensitive fields — they used the live-enrichment layer to replace the
baseline, then labelled which was which. p001's check had to be rewritten
because it punished that.

### An executor-prompt defect worth recording

The JSON shape I gave every agent used `{"argv": ["--type", "grant"]}` as its
example. That is also a plausible real call, so an agent echoing the placeholder
is indistinguishable from one reporting honestly. Three agents reported exactly
it; two quote the flag in their own answer text, so those are genuine. w3o-07 is
unresolvable from the transcript and is scored as reported. A placeholder that
doubles as a valid answer contaminates the axis it is meant to record — the next
run's prompt uses a shape no real call could take.

### The thing the split was not built to see

Most agents reached for `WebSearch`/`WebFetch`, which the skill permits and step 4
prescribes. Several answers are correct because of a live check rather than
because of the roster — w3o-11 walked a user off a closed programme using
governance-forum evidence the roster does not contain. The split measures
`SKILL.md`, but a growing share of what it scores is the enrichment layer, not
the catalog. A future iteration should carry cases that pin roster-only behaviour
so the two can be told apart.

## 2026-08-29 — iter1, v0.2.12, E1 applied, 24 cases, 1 repeat

**24/24 — call 1.0, answer 1.0.** Up from 22/24. Gate passed; E1 kept.

The number overstates it. Two cases recovered and only one is attributable to the
edit — w3o-15, the probe E1 targets, where the agent went from running nothing to
running three queries and explaining why. w3o-07 recovered because a different
agent picked `--search optimism` over `--type grant` on a case E1 says nothing
about. That is variance, and crediting it to the edit would corrupt the next
comparison. Full attribution table in `skill-impact.md`.

One harness correction this round, and it was applied to both run files before
the numbers were taken: the named-entity cases pinned a literal search string, so
`--search csx` failed a case about a16z CSX that `--search a16z` passed. Replaced
with a `returns` constraint — any query that retrieves the named entries counts.
iter0 re-scores at exactly 0.9167 under it, so the comparison stays like-for-like.

### The executor prompt

Fixed the iter0 defect: the JSON example now uses an obviously fake placeholder
rather than `--type grant`, which was also a plausible real call. Two agents this
round returned prose with no JSON wrapper at all and had to be asked again for it;
both re-emitted without redoing the work. Worth building into the next runner
rather than chasing by hand.

### Where this leaves the split

Saturated. A split at 24/24 cannot gate the next edit, and E2 is already blocked
on exactly that: it needs repeats to tell a documentation gap from a coin flip,
and there is one repeat per iteration here. Replace before editing again — see
`skill-impact.md` for what the replacement needs.
