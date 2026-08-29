# p006 — A populated `visa_free` that does not cover the trip

**Status**: hypothesis · no trace yet

## Predicted symptom
The agent reads `visa_free` as a yes/no field, sees it populated, and answers
"you're visa-free" for a trip the exemption does not cover.

## Where it bites
| Nationality | Exemption | 30-day trip |
|---|---|---|
| Philippines | 21 days | `EVISA` |
| Seychelles | 14 days | `EVISA` |
| Germany | 45 days | `VISA_FREE` — but `EVISA` at 60 |
| Thailand | 30 days | `VISA_FREE` — but `EVISA` at 31 |

## Root cause
`main()` returns a populated `visa_free` block *and* `recommended_pathway: EVISA`
when the trip exceeds the cap. That is correct and deliberate — the traveller
should know the exemption exists — but SKILL.md never states that the two fields
can disagree, or that `recommended_pathway` wins. The Critical Rules say the
script is the source of truth; they do not say which field is.

## Predicted root-cause-level fix
State the precedence explicitly in SKILL.md: `recommended_pathway` is the answer;
`visa_free` is context. Name the `EVISA`-with-populated-`visa_free` shape as the
case to watch, and require the answer to say *why* the exemption falls short.

## Anti-pattern to record if confirmed
Reading a structured result for the field that is easiest to skim rather than the
field that carries the decision. Compare [[p003-citizen-offered-a-visa]], where
the same skim-the-wrong-field error was fixed on the producing side.

## Validation cases
`vvc-06`, `vvc-07`, `vvc-08`, `vvc-10` — each requires the answer to name the cap
that was exceeded, not merely land on `EVISA`.

---

## Iteration 0 result — **falsified**

`vvc-06` (PH/21 vs 30 days), `vvc-07` (SC/14 vs 30), `vvc-08` (DE/45 vs 60),
`vvc-10` (TH/30 vs 31): **4/4 passed.** Every trace routed to `EVISA` and named
the cap that was exceeded.

The prediction was low-confidence and the reason it gave was the right one: the
generated note already spells out the shortfall in prose ("… are normally exempt
for up to 21 days, but your trip (30 days) exceeds that limit"). The agent does
not need a precedence rule between `visa_free` and `recommended_pathway`, because
it is not reading the fields — it is reading the sentence.

**Not a pattern.** Retained as a record of a prediction that did not survive, and
as the reason the note text is load-bearing: shorten that note and these four
cases become the failure this page predicted.
