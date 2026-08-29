# p005 — The weekly refresh inflates unverified claims

**Status**: confirmed · corrected in PRs #25, #27, #33

## Symptom
Automated refreshes wrote policy facts the sources did not support: a blanket
mandatory health declaration, a "five international airports" Pre-Arrival
Information rollout, a Timor-Leste signing date of 23 July, and a decree cited
for a claim it says nothing about (behind a URL that 404'd). Separately, refreshes
deleted existing caveats and bumped `last_verified` onto claims nobody rechecked.

## Root cause
The refresh could rewrite a fact without producing a source that survived being
followed. Freshness was treated as a date field to advance rather than a claim to
earn. Conservative language ("conditional", "optional pilot", "not yet in force")
is exactly what an unconstrained rewrite rounds off, because the crisp version
reads better.

## Fix
Three layers. A tier-1 `source_registry` in the dataset binds each corrected claim
to a primary Vietnamese government host. `PolicyFactTest` fails if a disproven
claim returns — asserting on `assertNotIn` over the whole serialized dataset, so
the claim cannot reappear anywhere in the file. And `audit_refresh.py` rolls back
a `last_verified` the refresh did not earn.

## Anti-pattern
Refreshing a fact and its freshness date in the same unreviewed step. Also:
testing that the *correct* text is present, which a rewrite can satisfy while
adding the wrong text next to it. Test that the wrong text is absent.

## Guards
`PolicyFactTest` in full — particularly
`test_health_declarations_are_conditional_not_blanket`,
`test_pre_arrival_information_is_an_optional_tan_son_nhat_pilot`,
`test_timor_leste_uses_the_primary_source_signing_date`.

## Validation cases
`vvc-19` — Timor-Leste is signed but not in force, and must never answer
visa-free. Related: [[p007-exemption-conditions-dropped]], the same
caveat-shedding failure one layer up, in the agent rather than the data.
