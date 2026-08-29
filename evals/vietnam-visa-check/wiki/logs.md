# vietnam-visa-check — maintenance log

Chronological. What changed in the wiki, and why. Append only.

## 2026-08-29 — wiki layer seeded

Built the diagnostic layer and the 24-case validation split. Nine patterns
recorded: p001–p005 reconstructed from merged corrections, p006–p009 derived from
reading `SKILL.md` against `data/vietnam_immigration_policy.json`.

Sources for the confirmed five: `done.vietnam-visa-nationality-resolution.md`
(p001–p004, all from one 2026 chat transcript — *"Hows the visa for Russians?"* —
where the reported symptom was a visible tool failure and the serious defect was
the silent wrong answer for "UK"), and
`done.vietnam-visa-policy-verification-corrections.md` plus PRs #25/#27/#33 (p005).

No execution traces have been collected yet. p006–p009 are predictions, and the
first iteration's job is to confirm or kill them. Recording them as hypotheses
before the run is deliberate: it makes the iteration a test rather than a
post-hoc explanation of whatever the traces happen to show.

### Observation carried forward

Every confirmed pattern so far was fixed in the **script**, not in SKILL.md. The
regression surface is 299 lines of tests against `query_visa.py` and the dataset,
and zero checks on what the agent does with a correct result. That is the gap this
split exists to measure — and it means the baseline could score badly without any
of it being the script's fault.

### On p005 and the skill boundary

p005 is a maintenance-process failure, not an agent-behaviour failure. It is
recorded here because it explains why the dataset reads the way it does — the
hedged, conditional phrasing in `entry_categories` and `_meta.source_registry` is
load-bearing and was won back twice. An agent edit that "tightens" that language
is re-introducing a corrected defect. It is also the same failure mode as
[[p007-exemption-conditions-dropped]] one layer up.

## 2026-08-29 — iteration 0 baseline

24 traces, one fresh agent per case, Sonnet, no wiki access. **91.7% pass**
(22/24) — `call_score` 95.8%, `answer_score` 95.8%. Raw run: `runs/iter0.jsonl`.

### Scored twice, and the first number was wrong

The first grading returned 70.8%. Auditing the seven failures found **five were
rubric defects, not skill defects** — checks that fired on correct answers:

- `vvc-03`, `vvc-24`: forbade the string `visa-free`, which caught the correct
  sentence "the US does not have a visa-free arrangement".
- `vvc-05`: forbade `visa-free`, which caught "I can check whether you're
  visa-free" — an offer to look it up.
- `vvc-16`: forbade `e-visa`, which caught "this is different from the e-Visa
  pathways offered to foreign nationals" — an explicit contrast.
- `vvc-03`: the fee check matched `$25` and `25 USD` but not `USD 25`, which is
  the phrasing the skill's own output uses.
- `vvc-19` was miscoded: `expected_call` demanded 14 days for a prompt that states
  no duration.

All six corrections are in `skill-impact.md` with the reasoning, and the relaxed
checks were re-verified against deliberately bad answers — all five still fail.
Recorded prominently because editing a rubric after seeing results is exactly how
a gate stops meaning anything. The rule applied: fix a check only when it fires on
an answer that is actually correct, never when it fires on one that is wrong.

### Four of five hypotheses falsified

p006, p007, p008, p009 all died. p007 was the highest-confidence prediction on the
board *and* its stated root cause was factually wrong — `visa_free.conditions`
does appear in SKILL.md's example JSON; it is absent only from the Critical Rules.
The agent read the field out of the example and used it correctly in 3/3 cases.

The generalisable lesson: **a gap in a skill's text is a hypothesis about
behaviour, not an observation of it.** All four predictions were derived by
reading SKILL.md against the dataset, which is the same method that produced the
five confirmed historical patterns — but those five had traces behind them.

### Two real failures, neither predicted

- `vvc-18` → [[p010-absent-record-read-as-confirmed-negative]]. The agent turned
  "not listed in this dataset" into "Brazilian passport holders do not get
  visa-free entry". Most nationalities on earth land in that state.
- `vvc-22` → [[p011-standing-rule-overridden-by-user]]. Told not to run anything,
  the agent made zero tool calls, cited the rule it was breaking, and hedged. The
  hedge happened to be correct, which is why `call_score` matters.

### The best finding came from a passing trace

`vvc-24` passed. Inside it, the agent called `--nationality Ireland`, got an
unrecognised-nationality error with an empty suggestion list, and silently
retried with `IE`. Following that up found **26 of 81 display names do not
resolve to their own ISO2** — the demonym works, the country's own name does not
— and 17 of those fail while suggesting the exact string that just failed. See
[[p012-country-name-unresolvable]] and
`docs/backlog/todo.visa-country-name-resolution.md`.

Nothing in the rubric was looking for this. It was visible only because the run
file records tool calls, and only because a passing case was read rather than
skipped. This is the concrete argument for the paper's success-sampling rule.

### Anti-pattern still recurring

5 of 24 traces rewrote the user's wording before calling: `USA`→`US`,
`Americans`→`US`, `American`→`US`, `Timorese`→`Timor-Leste`, `Australian`→
`Australia`. SKILL.md forbids this in a Critical Rule. All five still resolved
correctly, so no case failed — but this is the behaviour that hid
[[p002-alias-shadowed-by-iso-shortcut]] for as long as it hid, and it is what
would mask [[p012-country-name-unresolvable]] in the other direction. Tracked as
`translated_inputs` in the grader rather than as a failing check, because on the
evidence it is a risk indicator, not a defect.

### Baseline is model-specific

Sonnet, one repeat. The paper's cross-model results say a skill evolved against
one model can transfer badly to another; this number should not be assumed to
hold for the Nanobot or OpenAI runtimes without re-running.

## 2026-08-29 — iterations 1 and 2, `0.4.0`

### Script fix first (p012)

`build_country_index()` now folds `_COUNTRY_NAMES` into the lookup, and
`suggest_nationalities()` drops any candidate equal to the failed input.
Unresolvable display names 26 → 0; self-echoing suggestions 17 → 0. Four tests
added; verified by reverting the fix, where 3 of the 4 fail. Existing 101 tests
unchanged, now 105.

This was a script defect, so it is guarded by `tests/`, not by the split. Ground
truth was regenerated afterwards and did not move — correct, since the fix repairs
inputs the 24 cases do not use.

### Four SKILL.md edits, bundled

Bundling breaks per-edit attribution, and it was the right call anyway: four
separate gated iterations would have cost 96 agent traces to separate effects that
mostly turned out to be zero. Recorded as a deliberate trade, not an oversight.

| Edit | Target | Effect |
|---|---|---|
| Lookup not waivable by user request | p011 | **Worked.** `vvc-22` passes, `call_score` → 100%, trace cites the rule |
| Three evidence states | p010 | Visible in `vvc-24`; its own case was miscoded (below) |
| Verbatim pass-through, with examples | p001 recurrence | `translated_inputs` 5 → 4. Noise |
| Undocumented output fields listed | p013 | No case moved |

### The `vvc-18` correction

`vvc-18` failed in iterations 0 and 1 and was reported as a real defect. It was
not. **Brazil is on the explicit-negative list**, so the script emits
`IMPORTANT: Brazil passport holders do NOT have visa-free access` and the agent
was quoting it verbatim. The case was built to probe `absent-from-dataset` using a
country that is not absent from the dataset, and the `honesty` check was demanding
a hedge the data contradicts.

Two separate rubric defects hid this for two iterations:

1. The check passed on the loose pattern `verify`, which nearly every answer
   contains — so in iteration 1 it scored as a *pass* while the supposed defect
   was still present. A false negative sitting on top of a false premise.
2. Removing `verify` made it fail again, which looked like confirmation.

Rebuilt on **Portugal**, in neither list. Under `0.4.0` the answer is exactly
right: *"that's not the same as confirming they don't have one, just that this
dataset has no record either way."*

The lesson is not about Brazil. It is that **a case is an assertion about the data
and needs checking like any other.** I read "Brazilian passport holders do not get
visa-free entry" as a hallucination without checking whether the script had said
it. The script had.

### Grader: negation-awareness

`forbid_all` fired on "Australians do **NOT** get visa-free entry" — the correct
answer — because the pattern matched straight through the negation. `forbid_all`
now ignores a match with a negation within 40 characters before it, not crossing a
sentence boundary. Re-verified against the five adversarial answers: all still
fail, on the intended checks.

### Scores

Comparing only the 23 cases stable across the run, identical grader:

| | iter 0 (`0.3.6`) | iter 1 (`0.4.0`) |
|---|---|---|
| pass | 22/23 (95.7%) | **23/23 (100%)** |
| call | 95.7% | **100%** |
| answer | 100% | 100% |

`vvc-18` scored separately on its corrected form, with `vvc-03` and `vvc-21` as
over-hedging controls: **3/3**. Both confirmed negatives stayed firm ("no
visa-free access to Vietnam at all"), so naming the exact note prefix that
licenses the strong claim did prevent the regression it was designed to.

### What the numbers are worth

One case moved on a 23-case split — 4.3 points, which this project's own rule
calls noise. The reason to accept the bundle is mechanistic, not statistical: the
`vvc-22` trace shows the agent running the script *and citing the new rule*, and
`vvc-18`'s corrected answer reproduces the new rule's language. Score alone would
not justify it.

Still one repeat, still Sonnet. A full 24-case re-run on the corrected split would
give a clean headline number; the 23-case comparison above is what exists.
