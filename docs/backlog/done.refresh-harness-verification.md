# Make the weekly refresh check itself

**Deps**: weekly-skill-refresh-2026-08-17-verification

## Goal
The 2026-08-17 refresh shipped a failing test, four dead citations, and a blanket
`last_verified` bump across 41 entries, and none of it was visible on the PR.
Close both holes: give the refresh real checks, and make `last_verified` mean
something.

## Files
- `scripts/check_anchors.py` (new) — fail on citations that no longer resolve
- `scripts/audit_refresh.py` (new) — roll back unattested `last_verified` bumps
- `tests/test_refresh_harness.py` (new) — cover both scripts offline
- `.github/workflows/weekly-skill-refresh.yml` (edited) — run the checks before opening the PR
- `web3-opportunities/data/web3_opportunities.json` (edited) — repoint three dead URLs
- `AGENTS.md` (edited) — document both commands
- `docs/backlog/PRIORITY.md` (edited) — track this spec

## Acceptance
- [x] A PR opened by the refresh reports harness, anchor, and honesty results in its body
- [x] A failing test in a refresh turns the Actions run red instead of passing silently
- [x] `REFRESH_PAT`, when set, makes the PR trigger `Repository Checks` normally
- [x] Anchors fail only on 404/410 or NXDOMAIN; 403 and timeouts report as unverified
- [x] A `last_verified` bump survives only with a content change or an attestation
- [x] Reverting a date leaves the rest of the file byte-identical
- [x] The three roster entries whose domains no longer resolve point at live pages
- [x] NOT: make the default `Skill Harness` check depend on the network

## Verify
- `python3 scripts/validate_skills.py` → JSON with `"ok": true`
- `python3 -m unittest discover -s tests -v` → all tests pass
- `python3 scripts/check_anchors.py` → `"dead": 0`
- Replay: `audit_refresh.py` over 826ad2b→0d36b32 reverts 35 of 41 dates
- `git diff --check` → no whitespace errors

## Notes
GitHub does not trigger workflows for events raised with the default
`GITHUB_TOKEN`, which is why the refresh PR had an empty checks list. The inline
harness works without any secret; `REFRESH_PAT` is the optional upgrade that
restores real PR checks.

Reverting unattested dates rather than only warning is deliberate: an unattended
weekly job that merely warns produces warnings nobody reads, and by then the
wrong date has shipped.
Completion approved by the user on 19 August 2026. Shipped in #29 (merged as
c82d810), including four review findings fixed and verified: a swallowed audit
failure, shell interpolation of untrusted URLs, disabled TLS verification, and a
zip() comparison that truncated. `REFRESH_PAT` remains optional and unset; the
inline checks and the commit status added afterwards cover the PR page without it.
