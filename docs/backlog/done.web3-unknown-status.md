# Let the refresh mark an unconfirmed web3 status `unknown`

**Deps**: —

## Goal
The 2026-11-16 refresh (PR #80) could not confirm `polkadot-hackathons` or
`optimism-retro-funding` as open. It tried `unknown`, which the roster's own
`enums.status` and `query_opportunities.py --status` both accept, but
`tests/test_web3_opportunities.py` pinned a status list without it, so the refresh
put both back to `open` while raising `last_verified`. A user asking what is open
then got both as open "as of 2026-11-16", a claim the research did not support.
Correct it on the refresh branch itself, per AGENTS.md "Correcting a refresh".

## Files
- `tests/test_web3_opportunities.py` (edited) — add `unknown`; pin the list to the enum
- `web3-opportunities/data/web3_opportunities.json` (edited) — both entries `unknown`
- `web3-opportunities/SKILL.md` (edited) — 0.2.24 -> 0.2.25 (PATCH, data change)
- `evals/web3-opportunities/cases{,-v2}.jsonl` (edited) — regenerated ground truth
- `docs/backlog/PRIORITY.md` (edited) — recently shipped

## Acceptance
- [x] Both entries are `unknown`; their notes and the refresh's dates are kept
- [x] The test's status list equals the roster's `enums.status`, and fails if they drift
- [x] `--status open` no longer returns either entry
- [x] NOT: relax any other roster test; NOT: change the refresh's sourced notes

## Verify
- `python3 -m unittest tests.test_web3_opportunities -v` → OK
- `python3 evals/scripts/build_web3_cases.py --check` → `"ok": true`
- `SKILL_DIR=./web3-opportunities python3 web3-opportunities/scripts/query_opportunities.py --status open`
  → neither id in the results
- `python3 scripts/validate_skills.py` → no errors
