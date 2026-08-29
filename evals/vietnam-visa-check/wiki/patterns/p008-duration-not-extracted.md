# p008 — Duration never extracted from the user's prose

**Status**: hypothesis · no trace yet

## Predicted symptom
"I'm German and I'm staying about two months" is answered from a 30-day default:
`VISA_FREE`. The right answer at 60 days is `EVISA`. Nothing in the exchange looks
wrong — the script ran, the data was current, the answer was confident.

## Root cause
SKILL.md documents the parameter as:

> `--duration_days` (optional, default 30): Intended length of stay in calendar days.

"Optional, default 30" reads as *safe to omit*. There is no instruction to derive
it from what the user said, and no warning that the default silently answers a
different question than the one asked. Every exemption in the dataset is a
duration cap, so this parameter decides the pathway more often than the
nationality does.

## Predicted root-cause-level fix
Reclassify it: required whenever the user states or implies a length of stay, with
the natural-language forms spelled out ("two months" → 60, "six weeks" → 42,
"a fortnight" → 14). Say plainly that omitting it answers a 30-day question.

## Anti-pattern to record if confirmed
Treating a defaulted parameter as optional when the default is a substantive
answer rather than a neutral one. A default that changes the result is not a
default, it is an assumption.

## Validation cases
`vvc-08` (two months → 60 → `EVISA`), `vvc-11` (six weeks → 42 → `VISA_FREE`).
The pair matters: a rule that just says "assume long stays" passes one and fails
the other. The grader checks the argument, not only the answer.

---

## Iteration 0 result — **falsified**

`vvc-08` ("about two months" → `--duration_days 60` → `EVISA`) and `vvc-11`
("roughly six weeks" → `--duration_days 42` → `VISA_FREE`): **2/2 passed**, both
with the correct integer.

Across all 24 traces, every prompt that stated or implied a duration got that
duration passed — `vvc-15` sent 120 for "4 months", `vvc-18` sent 21 for "3
weeks", `vvc-03` sent 14 for "2 weeks". The default was used only where the user
gave no duration at all, which is correct behaviour.

The premise — that "optional, default 30" reads as safe to omit — was not borne
out. **Not a pattern.**

One live risk survives, unmeasured: `vvc-19` passed no duration where the prompt
stated none, and the case originally *required* 14 days. That was an authoring
error in the split, not agent behaviour — see `../skill-impact.md`.
