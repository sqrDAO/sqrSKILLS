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

## 2026-08-29 — v1 retired, v2 built and calibrated

v1 saturated at 24/24 after one gated edit, which means it can no longer gate the
next one. Replaced rather than extended: `cases-v2.jsonl`, 24 cases, none of them
carried over.

What v2 can see that v1 could not:

- **The catalog with the web switched off.** Four cases run `web_allowed: false`.
  This is the important one. v1's hardest probes — present-tense status, an
  unknown chain, a perishable deadline — were passed by agents going and
  checking, which the skill permits and which is good behaviour. But it means v1
  could not distinguish "the labelling rule is working" from "the rule was never
  reached". v2-01 is v1's `status-labeling` question with that route closed.
- **Multi-turn.** Six cases. The failure mode is answering turn 2 from turn 1's
  result set: `v2-04` asks for non-dilutive Solana, then widens to accept a small
  equity slice, and the `mixed` entries are absent from turn 1's rows, so reuse
  is visible in the answer.
- **Rules the skill states and v1 never tested.** Live-beats-baseline drift
  reporting (`v2-06`, `v2-08`), offering to add a missing programme (`v2-09`),
  Tier-1 source discipline (`v2-11`), and a user premise that contradicts the
  roster in the expensive direction (`v2-16`, "your catalog lists CSX as
  non-dilutive, right?").
- **A self-contradictory ask.** `v2-12` wants a non-dilutive accelerator. Zero
  match, and the useful answer explains why the category cannot exist rather than
  reporting an empty set.

### Harness

The grader now reads multi-turn runs, accepts several run files as repeats of one
iteration, and reports `unstable_cases` — cases that disagree between repeats.
That list is the direct answer to what went wrong when E1 was gated: a case that
flips is noise, and an edit credited to it is an edit paid for by a coin flip.

Calibration: ideal run 24/24, deliberately-wrong run 0/24, every case failing on
its own probe. One check needed fixing first — `live_wins` on `v2-06` failed a
gold answer that said "the page wins, not my snapshot", because the pattern
pinned the subject of the sentence. Broadened to the claim rather than one
phrasing of it. Round 4 of harness corrections, still ahead of skill edits 4-1.

v1's stored runs re-score unchanged under the rewritten grader (0.9167 / 1.0).

### Harness round 5 — a half-finished exchange scored 0.75

Reported by CodeRabbit on #44, and real. `run_integrity_error` checks that every
case appears exactly once, which was sufficient while every case had one turn.
With turns it is not: a run holding only turn 1 of a two-turn case still covers
every `case_id`, the missing turn reads as an empty answer, and a turn-pinned
`forbid_all` passes on empty text.

Reproduced by truncating every multi-turn case in the v2 ideal run to its first
turn. It scored **0.75** — not an error, not a zero, a plausible number computed
from an exchange that never happened. That is the exact failure the completeness
guard exists to prevent, and the guard had a hole in it the moment turns were
added.

`turn_integrity_error` now refuses a mismatch in either direction: too few turns
means the run stopped early, too many means it is not this case. Six tests.

Worth noting the shape of this one. The v2 cases all happen to carry a turn-pinned
`require_any` as well, so a truncated run still *failed* those cases — the defect
was never going to show up as a wrong verdict on today's split. It would have
shown up the first time someone wrote a case whose second turn only had forbids,
which is a perfectly reasonable case to write. Five rounds of harness corrections
now, against one skill edit.

## 2026-08-29 — v2 iter0, v0.2.12, 24 cases, 2 repeats

**23/24 and 24/24 — mean 0.979, call 1.0 in both.** `unstable_cases: [v2-02]`,
**`stable_failures: []`**.

The raw first read of repeat A was 19/24. Four of those five failures were my
checks, and a fifth turned up in repeat B:

- `v2-09/distinguishes` failed an answer that said "neither is an Encode Club
  entry. Both are other programs whose **notes** mention Encode Club" — the
  pattern was `in the notes`, and the markdown asterisks in `**notes**` broke it.
  Six literal phrasings were grading vocabulary.
- `v2-20/no_legal_answer` fired on "Whether **you can legally** launch a token
  from Vietnam is a regulatory question — I'm not the right source for this."
  The forbidden phrase sat inside the sentence doing the refusing.
- `v2-22/no_dilutive_survivors` fired on a "Dropped as dilutive: Alliance DAO,
  YZi Labs, ..." section. The agent named all six precisely because it had
  removed them.
- `v2-24/no_invented_url` fired on an answer naming `grants.gitcoin.co` **to
  report that it no longer resolves**. This is the *same defect* as v1's
  `grants.near.org` fire, on a different case — the fix was applied to one check
  and never generalised to the class.
- `v2-01/no_live_claim` (repeat B) fired on "I have no web access in this
  session, so **nothing here is live-verified**". `nothing` was missing from the
  shared negation vocabulary, and `\bno\b` cannot reach it across the word
  boundary.

Two process notes on how that was found. My first diagnostic read check turns as
1-based; they are 0-based, so it showed me the wrong turn for `v2-22` and I
nearly recorded the wrong root cause. And the corrections take the score from
19/24 to 23-24/24, which is precisely the shape of a rubric edited until the
failures went away — so each loosened check is now pinned in
`tests/test_evals_harness.py` against both the answer it must pass and the
answer it must still fail. All four still discriminate; the negation change is
pinned in both directions too.

Regression: the visa split re-scores at exactly 0.9167 / 0.9583 / 1.0 and web3
v1 at 0.9167 / 1.0, so the shared-module change moved nothing that was already
measured.

### Where this leaves v2

**Saturated on its first baseline.** No stable failure, and the single failure is
in `unstable_cases` by the split's own definition. v2 was built to replace a
saturated v1 and cannot gate an edit either. E2 stays withheld: it needs a stable
failure to fix, and there isn't one.

The one case worth a decision rather than a fix is **v2-02**. With the web off
and no Bitcoin entry in the roster, the agent named OpenSats, Spiral, Btrust and
the HRF Bitcoin Development Fund — out-of-catalog, from memory — but labelled
them as such, quoted no amounts, deadlines or status, and told the user to verify
each independently. The check calls that inventing. Whether the label discharges
it is a question about what the skill should do, not about whether the harness is
right, so it is left failing rather than quietly excused.
