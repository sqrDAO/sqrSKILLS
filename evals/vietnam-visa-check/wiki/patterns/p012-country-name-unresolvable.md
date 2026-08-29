# p012 — The country name fails where the demonym works

**Status**: confirmed · surfaced by iteration 0, `vvc-24` · **fixed in `0.4.0`**

## Symptom
`--nationality Ireland` returns an unrecognised-nationality error with an **empty**
suggestion list. `--nationality Irish` resolves to `IE` and answers correctly.
The demonym works; the country's own name does not.

In `vvc-24` the agent recovered by retrying with the ISO code. A user typing
"Ireland" into a chat gets asked to supply "the country name or ISO alpha-2 code" —
which is what they just typed.

## Root cause
`build_country_index()` populates the lookup from four sources: dataset ISO2
codes, **dataset country names**, `_ALIASES`, and `_DEMONYMS`. `_COUNTRY_NAMES`
(ISO2 → display name) is built separately by `build_display_names()` and is used
only to render output. It never enters the index.

So for every country reachable by a demonym but absent from both dataset lists,
the demonym resolves and the display name does not. **26 of 81 display names do
not resolve to their own ISO2**: Argentina, Austria, Bangladesh, Colombia, Cyprus,
Egypt, Estonia, Greece, Iceland, Iran, Ireland, Israel, Latvia, Lithuania, Malta,
Nepal, Nigeria, Pakistan, Peru, Portugal, Qatar, Saudi Arabia, Serbia, Sri Lanka,
Turkey, Ukraine.

## The second-order defect
`suggest_nationalities()` draws candidates from the display-name table, so 17 of
the 26 fail and then suggest **the exact string that just failed**:

    $ query_visa.py --nationality Argentina
    "error": "Nationality 'Argentina' not recognised. …"
    "suggestions": ["Argentina"]

Per SKILL.md the agent must ask the user to confirm a suggestion. The user
confirms "Argentina", the agent passes "Argentina", it fails again. The other 9
return no suggestions at all, and SKILL.md sends the agent to ask for a country
name the user has already given.

## Why the existing tests miss it
`test_every_dataset_country_has_a_demonym` walks the two **dataset** sections and
checks each has a demonym. It never asks the inverse — whether every name the
skill is willing to *print* is a name the skill can *read*. The 26 affected
countries are exactly those outside the dataset, so the loop never reaches them.

## Fix — applied 2026-08-29 (`0.4.0`)
`build_country_index()` now folds `_COUNTRY_NAMES` into the index via `setdefault`,
placed after the dataset pass (so the dataset stays authoritative) and before the
alias/demonym pass (so p002's ordering guarantee is untouched).
`suggest_nationalities()` additionally drops any candidate whose normalized form
equals the failed input, so the echo shape cannot return by another route.

Unresolvable display names: **26 → 0**. Self-echoing suggestions: **17 → 0**.

Guarded by four new tests, three of which fail against the pre-fix code:
`test_every_display_name_resolves_to_its_own_code` (the invariant, not a list),
`test_country_names_outside_the_dataset_resolve`,
`test_dataset_names_win_over_the_bundled_table` (guards the `setdefault`
precedence the fix could have broken), `test_no_suggestion_echoes_its_own_input`.

## Related
[[p002-alias-shadowed-by-iso-shortcut]] — the same class: a resolution table that
exists but is not consulted on the path users actually take.
