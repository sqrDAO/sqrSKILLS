# p007 — Exemption conditions dropped from the answer

**Status**: hypothesis · no trace yet · **strongest candidate for iteration 1**

## Predicted symptom
A Polish traveller flying in for business meetings is told "visa-free, 45 days".
The exemption is tourism-only. The answer is confidently wrong in the one
direction that strands someone at a border.

## Root cause
SKILL.md's Critical Rules say:

> **Read the `notes[]` array into your answer.** It carries the caveats that make
> the pathway correct.

That is true and it is not enough. The caveats that make the pathway correct are
split across two places, and the rule reaches only one of them:

- `notes[]` — expiry warning, "not in this dataset", passport validity, freshness
- `visa_free.conditions` — **tourism purpose only** (PL, CZ, CH),
  **30 days per entry, 90 days per calendar year** (BY)

`conditions` is never mentioned in SKILL.md. Nothing tells the agent it exists, so
nothing tells the agent it is load-bearing.

## Predicted root-cause-level fix
Extend the rule to name `visa_free.conditions` alongside `notes[]`, and say what
it does: it narrows the exemption to a purpose or a quota, so a `VISA_FREE`
pathway with a non-null `conditions` is conditional, not unconditional.

## Anti-pattern to record if confirmed
Trigger: `recommended_pathway: VISA_FREE` with a non-null `visa_free.conditions`.
Failing shape: report the pathway and the day count, drop the condition.
Fix: state the condition in the same sentence as the pathway, and check it against
the trip the user described.

## Validation cases
`vvc-12` (tourism-only vs. a stated business trip), `vvc-13` (tourism-only plus a
2028 expiry), `vvc-14` (90-days-per-year cap against 70 days already used).

---

## Iteration 0 result — **falsified**, and the root cause was wrong

`vvc-12` (Polish business trip), `vvc-13` (Swiss, expiry), `vvc-14` (Belarus,
90-day annual cap): **3/3 passed.** The `vvc-12` trace surfaced the tourism-only
condition unprompted and offered the e-Visa as the unambiguous business route.
`vvc-14` applied the annual cap to the 70 days the user said they had used and
concluded the exemption could not cover 30 more.

The root cause above is factually wrong. It claims `conditions` is "never
mentioned in SKILL.md". It is — the Output section's example JSON shows
`"conditions": "Extended until 2028 per March 2025 announcement"` inside the
`visa_free` block. It is absent from the *Critical Rules*, not from the document.
The agent read the field out of the example schema and used it.

This was the highest-confidence prediction on the board and it was the most wrong.
Worth keeping visible: the gap was real and documented accurately, and it still
produced no failures. A gap in a skill is a hypothesis about behaviour, not an
observation of it.

**Superseded by** [[p013-documented-output-schema-lags-the-script]], which is the
version of this idea that survived contact with the traces.
