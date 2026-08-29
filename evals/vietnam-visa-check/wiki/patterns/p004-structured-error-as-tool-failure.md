# p004 — Structured error rendered as a tool failure

**Status**: confirmed · fixed in `0.3.0` (PR #20)

## Symptom
Unrecognised nationality input exited 1. The harness rendered that as a failed
tool call in the user's chat — a red bubble instead of a question.

## Root cause
Exit status was being used to signal *user input was unusable*, but the caller is
an agent that already had well-formed JSON on stdout. Non-zero exit is a channel
reserved for "the tool itself broke", and the harness treats it that way.

## Fix
Unresolved input prints `{error, hint, suggestions}` and exits **0**.
`suggestions` comes from `difflib.get_close_matches` and is never auto-accepted.
Exit 1 survives only for an unreadable data file — an install fault, not input.

## Anti-pattern (agent side)
Two of them, both now forbidden in SKILL.md: showing the raw `error` string to the
user, and picking a country when `suggestions` is empty. A near-miss gets
confirmed with the user; an empty list gets a question, not a guess.

## Rule now in SKILL.md
> Never present the raw error text to the user, and never guess a country from an
> empty suggestion list.

## Guards
`test_unrecognised_input_exits_zero_with_structured_error`,
`test_unrecognised_input_offers_suggestions`,
`test_suggestions_offered_for_near_misses`.

## Validation cases
`vvc-04` (near miss — must ask, must not answer as Russia),
`vvc-05` (no suggestions — must ask, must not invent a pathway).
