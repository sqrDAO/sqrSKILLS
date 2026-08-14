# Reconcile weekly skill refresh for 10 August 2026

**Deps**: vietnam-visa-policy-verification-corrections

## Goal
Update PR #26 onto current `main`, preserve its independent Web3 opportunity
refresh, and discard its superseded Vietnam visa edits so the PR becomes
mergeable without regressing the primary-source corrections shipped in #27.

## Files
- `web3-opportunities/SKILL.md` (edited) — retain the refresh version bump
- `web3-opportunities/data/web3_opportunities.json` (edited) — retain verified opportunity updates
- `vietnam-visa-check/SKILL.md` (edited) — resolve to current `main`
- `vietnam-visa-check/data/vietnam_immigration_policy.json` (edited) — resolve to current `main`
- `docs/backlog/PRIORITY.md` (edited) — track this open spec
- `docs/backlog/todo.weekly-skill-refresh-2026-08-10.md` (new) — reconciliation spec

## Acceptance
- [ ] PR #26 contains current `main` and GitHub reports no merge conflicts
- [ ] Final PR diff retains the Web3 opportunity refresh at version `0.2.9`
- [ ] Final PR diff contains no Vietnam visa files superseded by PR #27
- [ ] Timor-Leste still routes to `EVISA`
- [ ] Blanket health-declaration and five-airport PAI claims remain absent
- [ ] Repository validator and unit tests pass after reconciliation
- [ ] NOT: overwrite the divergent local automation branch or force-push history

## Verify
- `git merge-base --is-ancestor origin/main HEAD` → exit 0
- `git diff --name-only origin/main...HEAD` → Web3 refresh plus backlog files; no visa files
- `python3 scripts/validate_skills.py` → JSON with `"ok": true`
- `python3 -m unittest discover -s tests -v` → all tests pass
- `python3 vietnam-visa-check/scripts/query_visa.py --nationality TL` → `EVISA`
- `git diff --check origin/main...HEAD` → no whitespace errors

## Notes
Resolve visa conflicts in favor of #27 because it is newer (14 Aug), cites primary
government sources, and includes regression tests absent from the 10 Aug refresh.
