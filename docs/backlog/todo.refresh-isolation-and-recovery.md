# Isolate weekly refresh writers and recover PR 60
**Deps**: —

## Goal
Restore the reviewed baseline after PR 60 deleted safeguards, and prevent timed-out
research processes from changing data after cleanup, audit, or validation.

## Files
- `.github/workflows/weekly-skill-refresh.yml` (edited) — isolated research jobs and packaging gate.
- `scripts/collect_refresh.py` (new) — import only successful, permitted research outputs.
- `tests/test_refresh_workflow.py` (new) — exercise publication guard, statuses and regeneration.
- `tests/test_collect_refresh.py` (new) — failure isolation and output scope regressions.
- `vietnam-crypto-radar/SKILL.md` (edited) — restore pre-refresh version.
- `vietnam-crypto-radar/references/baseline.md` (edited) — restore reviewed safeguards and citations.
- `web3-opportunities/SKILL.md` (edited) — restore pre-refresh version only.
- `web3-opportunities/data/web3_opportunities.json` (edited) — discard failed refresh dates.
- `REFRESH_SUMMARY.web3-opportunities.md` (deleted) — remove leaked scratch output.
- `REFRESH_VERIFIED.json` (deleted) — remove leaked attestation.
- `AGENTS.md` (edited) — document isolation and complete refresh validation.
- `docs/backlog/PRIORITY.md` (edited) — track this correction pending approval.

## Acceptance
- [x] Malformed artifacts reject only their own leg; healthy outputs still package.
- [x] Research failures/rejections publish a failing commit status and run result.
- [x] Audited data regenerates the three allowlisted evaluation case files.
- [x] The open-PR guard runs again immediately before publication.
- [x] Version comparison preserves all prompt-body bytes and rejects duplicate keys.
- [x] Crypto and Web3 data match the reviewed main baseline; no new freshness claims.
- [x] Research jobs cannot mutate the packaging job's checkout.
- [x] Failed research outputs never enter the checkout or verification audit.
- [x] Only permitted data and version-only SKILL changes can be imported.
- [x] Both generated evaluation splits are checked by the inline harness.
- [x] Open refresh PR guard runs before research, avoiding wasted work.
- [x] PR 60 is corrected on its existing branch and checks are rerun.
- [x] NOT: merge PR, rename spec before approval, or weaken regression tests.

## Verify
- `python3 scripts/validate_skills.py` → passes.
- `python3 -m unittest discover -s tests -v` → passes.
- `python3 scripts/check_unanchored.py --since origin/main` → passes.
- `python3 scripts/check_anchors.py` → no dead anchors; report unverified hosts.
- `python3 evals/scripts/build_visa_cases.py --check` → current.
- `python3 evals/scripts/build_web3_cases.py --check` → current.
- `git diff origin/main -- vietnam-crypto-radar web3-opportunities` → empty.
- `gh pr checks 60 --repo sqrDAO/sqrSKILLS` → corrected commit checks pass.

## Notes
Opus 5 follow-up: fix the five confirmed findings; retain rejected-leg diagnostics
and add coverage for malformed outputs, body-version edits and workflow wiring.
The old run validated a changing tree: its Web3 date test failed, but the final
commit contained a later top-level date. Recovery discards that leg entirely.
Crypto's destructive rewrite is withdrawn rather than treated as verified research.
The version reversions undo unmerged metadata only; no runtime prompt is changed.

Validation: 213 tests pass (three optional openpyxl tests
and one unavailable historical-revision test skipped); both generated
splits are current; actionlint 1.7.12 and the unanchored check pass.
Anchor check: 109 checked, 0 dead, 5 unverified.
GitHub Skill Harness passed for correction d90e06e (run 34820855499).

Opus follow-up validation: 221 tests pass (same four skips), including executions
of the workflow guard, status publisher and regeneration shell blocks. Validator,
unanchored check, both split checks and actionlint pass; baseline diff stays empty.
