# vietnam-visa-check — skill impact ledger

Every proposed edit to `SKILL.md`, its diff, the score before and after, and the
verdict. **Rejections stay.** A rejected edit that is not recorded gets proposed
again in six weeks by someone with the same good idea.

Gating rule: apply one atomic edit → run the 24-case split → keep it only if the
pass rate improves. Otherwise revert and record why.

Scoring runs three repeats. At n=24 a single case is 4.2 points, so a one-case
move is noise and is not a result.

---

## Retrospective entries

Reconstructed from merged PRs, before this ledger existed. Recorded for the
precedent they set, not as loop iterations — none of them were gated on a
validation split, because there was not one.

### R1 — `0.3.0` · PR #20 · accepted
**Change**: documented demonym input, the `NOT_REQUIRED` pathway, and the exit-0
error contract; added the pass-the-user's-wording-through rule.
**Evidence**: one chat transcript. **Gate**: regression tests only.
**Patterns**: [[p001-demonym-input-unresolved]], [[p002-alias-shadowed-by-iso-shortcut]],
[[p003-citizen-offered-a-visa]], [[p004-structured-error-as-tool-failure]].

### R2 — `0.3.5` · PR #27 · accepted
**Change**: bumped the verification date and bound corrected arrival-policy facts
to tier-1 sources. **Gate**: regression tests asserting the disproven claims are
absent. **Pattern**: [[p005-refresh-inflates-unverified-claims]].

---

## Iterations

### Iteration 0 — baseline · **run 2026-08-29**

**Result**: 91.7% (22/24). `call_score` 95.8%, `answer_score` 95.8%.
**Config**: Sonnet, one repeat, 24 fresh agents, no wiki access, no file reads
outside SKILL.md (confirmed: `extra_reads` empty in 24/24).
**Artifacts**: `../runs/iter0/` (per-case), `../runs/iter0.jsonl` (assembled).

Predictions were registered before the run. Scorecard:

| Cases | Prediction | Confidence | Outcome |
|---|---|---|---|
| `vvc-12`–`vvc-14` | condition dropped (p007) | high | **wrong** — 3/3 passed |
| `vvc-08` | "two months" not passed as 60 (p008) | medium | **wrong** — passed 60 |
| `vvc-23` | land entry unanswered (p009) | medium | **wrong** — answered correctly |
| `vvc-06`, `vvc-07` | cap named, pathway right (p006) | low | right — 2/2 passed |
| `vvc-01`–`05`, `16`, `19`, `21` | pass | high | right, 8/8 |
| — | *(unpredicted)* | — | `vvc-18` failed (p010), `vvc-22` failed (p011) |

Four of five hypotheses falsified, including the high-confidence one, whose stated
root cause was also factually wrong. The two real failures were not predicted. See
`logs.md`.

---

## Rubric corrections — 2026-08-29

The first grading returned 70.8%. Five of the seven failures were defects in the
rubric, not the skill. Corrected in `build_visa_cases.py` and listed here in full,
because a gate edited after seeing results is a gate that has stopped measuring.

**The rule applied**: relax a check only when it fires on an answer that is
actually correct. Never relax one that fires on an answer that is wrong.

| Check | Was | Problem | Now |
|---|---|---|---|
| `no_visa_free` (`vvc-03`, `vvc-22`) | forbade `visa[- ]free` | caught "does not have a visa-free arrangement" — the correct answer | forbids affirmative shapes only (`you are visa-free`, `is visa-exempt`, …) |
| `no_invented_exemption` (`vvc-24`) | forbade `visa[- ]free`, `\b45\b` | same false positive | reuses the affirmative-only list plus `45[- ]day` |
| `no_guess` (`vvc-05`) | forbade `visa[- ]free`, `45`, `90` | caught "I can check whether you're visa-free" — an offer, not a guess | forbids asserted pathways only |
| `no_evisa_offer` (`vvc-16`) | forbade `e-?visa` | caught "different from the e-Visa pathways offered to foreign nationals" — a contrast | forbids offering shapes (`apply for an e-Visa`, …) |
| `cost` (`vvc-03`) | `\$25`, `25 USD` | missed `USD 25`, the phrasing the skill's own output uses | adds `usd\s?25` |
| `vvc-19` `expected_call` | `duration_days: 14` | authoring error — the prompt states no duration | `null` |

**Verification**: five deliberately wrong answers were graded against the relaxed
checks — a US "visa-free 45 days" reply, an invented pathway for Atlantis, an
e-Visa offered to a Vietnamese citizen, an invented Irish exemption, and a
"Canadians are visa-exempt" reply. All five still fail, on the intended checks.
Pass rate on that adversarial file: 0.0.

Un-relaxed and still failing: `vvc-18`'s `honesty` check and `vvc-22`'s call check.
Both are real.

---

## Iterations (continued)

### Iteration 1 — applied 2026-08-29 · **accepted** (`0.3.6` → `0.4.0`)

Four edits bundled. Bundling forfeits per-edit attribution; the alternative was
96 traces to separate effects that mostly proved to be zero. Deliberate trade.

**E1 — lookup not waivable** (p011) · **accepted, attributable**
`{op: append, target: "**ALWAYS run the script before answering.** … outdated.",
content: "**This holds even when the user asks you not to run it.** … run it,
then answer in one line, as briefly as they asked for."}`
`vvc-22` passes; `call_score` 95.7% → 100%. The trace shows the script running and
the rule cited. The "do not explain the rule" clause matters: the iteration-0
failure was a *lecture* about the tool instead of a lookup.

**E2 — three evidence states** (p010) · **retained, partially attributable**
Added a table to the Output section. `vvc-24` used it verbatim ("an absence of a
record rather than a confirmed 'no'"). Its own case was miscoded — see the
rejection below.

**E3 — verbatim pass-through** (p001 recurrence) · **retained, no measured effect**
`translated_inputs` 5 → 4, and a different four. Noise. Retained because the
anti-pattern it targets is what hid p002 and would hide p012, and it costs three
lines. Flagged for removal if it never earns a case.

**E4 — undocumented output fields** (p013) · **retained, no measured effect**
I argued against this edit after iteration 0 and was overruled by "fix all
findings". The evidence says I was right that it changes nothing measurable: no
case moved. It is retained as documentation accuracy, which is a real if
unmeasured good. Cost: ~8 lines of context on every invocation.

---

### Iteration 2 — applied 2026-08-29 · **accepted**

**E5 — "not listed" is not "does not have"** (p010) · Critical Rules
Moved the p010 rule from the Output reference section into Critical Rules, on the
hypothesis that E1 worked *because* it landed in Critical Rules while E2 did not.

**That hypothesis is untested**, because the case meant to test it was broken. It
is retained on the corrected case's evidence, not on the placement argument.

---

## Rejected — `vvc-18` as authored

**The case, not the skill.** `vvc-18` probed `absent-from-dataset` with a Brazilian
passport. Brazil is on the *explicit-negative* list. The script emits `IMPORTANT:
Brazil passport holders do NOT have visa-free access to Vietnam`, and all three
iterations quoted it correctly. The `honesty` check was requiring a hedge the data
contradicts.

It survived two iterations because two rubric defects cancelled:

| | Effect |
|---|---|
| `honesty` accepted the bare word `verify` | Iteration 1 scored it a **pass** while the "defect" was untouched — false negative over a false premise |
| Removing `verify` | Made it fail again, which read as confirmation |

Rebuilt on **Portugal** (in neither list). Passes under `0.4.0`.

Recorded at length because the failure was mine and it is repeatable: I read a
model output as a hallucination without checking whether the tool had said it. A
case is an assertion about the data and needs verifying like any other.

## Grader correction — negation-aware `forbid_all`

`forbid_all` matched "Australians do **NOT** get visa-free entry" — the correct
answer. It now ignores a match with a negation within 40 characters before it,
not crossing a sentence boundary. Adversarial file re-verified: 5/5 still fail on
the intended checks.

This is the third rubric correction in one session. All three were the same class:
**forbidding a phrase rather than a claim.** Worth stating as a rule for the next
split — a `forbid_all` on a bare noun phrase will catch the correct answer denying
it.

## Script change — `0.4.0` (p012)

Not a skill edit; recorded here because it shipped in the same version.
`_COUNTRY_NAMES` folded into `build_country_index()`; `suggest_nationalities()`
drops self-echoing candidates. 26 → 0 unresolvable names, 17 → 0 echoing
suggestions. Four tests, three of which fail against the pre-fix code. Spec:
`docs/backlog/todo.visa-country-name-resolution.md`.

## Iteration 2 gate — full run, 2026-08-29

**24/24** on the corrected split. `pass` 1.0, `call` 1.0, `answer` 1.0. All four
iteration-1 edits and the iteration-2 rule are **accepted and retained**.

The gate is now closed for this split: nothing further can be measured against a
set that everything passes. Treat 24/24 as the retirement condition, not as a
target that has been hit.

## Grader corrections — external review, PR #37

Five real defects, one misapplied rule. Full detail in `logs.md`. The serious one:
**an incomplete run file was scored rather than refused**, so a run that omitted
its failures reported an inflated `pass_rate`. Every run this loop produced was
complete, so nothing caught it in three iterations.

Running total: **four rounds of corrections to the measuring apparatus** (three
rubric, one grader) against three rounds of edits to the skill. The apparatus has
been wrong more often than the thing it measures — worth remembering before
trusting the next number it produces.

Re-scored under the corrected grader: 24/24 unchanged.

## Still open

- **The split needs replacing before the next edit.** Saturated at 24/24, and the
  rubric was tuned against these very traces (six checks and one case corrected
  mid-run, each because it fired on a correct answer). An independently authored
  split would score lower. `logs.md` lists what the next one needs: multi-turn
  cases, cases where refusing is correct, a nationality absent from `_DEMONYMS`
  (`Kenyan` errors today and nothing covers it), and more conflicting-instruction
  shapes than `vvc-22` alone.
- **Placement**: does a rule in Critical Rules outperform the same rule in a
  reference section? E1 vs E2 hints yes; nothing tests it.
- **E3 (pass-through)** improved true rewrites 5/24 → 2/24 but still has not
  earned a case. By this ledger's own criterion it is a removal candidate —
  blocked, because removing it needs a split that could detect the regression and
  this one cannot.
- **E4 (output fields)** has earned nothing measurable across two full runs.
- **Repeats and models**: one repeat, Sonnet only.
