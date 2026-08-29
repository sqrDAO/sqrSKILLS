# Stop the refresh audit re-inflating corrected dates, and sweep Da Nang weekly

**Deps**: refresh-harness-verification, weekly-skill-refresh-2026-08-24-verification

## Goal
Two gaps the 2026-08-24 work exposed, both of which bite on the next Monday run.

`audit_refresh.py` asks only "did the content change?", never "which way did the date
move?". A correction pass that *lowers* `last_verified` — reducing a freshness claim
because the entry was not actually re-checked — is reported as UNSUPPORTED and, run
without `--report-only`, is reverted back up. The tool built to stop unearned dates
would restore five of them. Lowering a date is always safe: it claims less.

The weekly prompt also never mentions Da Nang. `vietnam-crypto-radar` now carries six
municipal controlled trials, an enabling resolution, and four undecided applications,
and nothing in the run tells the agent to look at any of it.

## Files
- `scripts/audit_refresh.py` (edited) — only a *raised* date needs support
- `.github/workflows/weekly-skill-refresh.yml` (edited) — sweep Da Nang; keep the floor caveat
- `tests/test_refresh_harness.py` (edited) — pin the direction rule and its edge cases
- `AGENTS.md` (edited) — describe what the audit actually enforces
- `docs/backlog/PRIORITY.md` (edited) — track this spec

## Acceptance
- [x] A lowered `last_verified` is never reported unsupported and never reverted
- [x] A raised `last_verified` still needs a content change or an attestation
- [x] A date that cannot be parsed as ISO is treated as raised, so the conservative path wins
- [x] The result JSON distinguishes lowered dates from supported ones rather than hiding them
- [x] `--report-only` and the reverting path agree on which entries are unsupported
- [x] The weekly prompt sweeps the Da Nang portal for new, extended, or suspended trials
- [x] The prompt states the trial count is a floor and names the four undecided applications
- [x] The prompt says Nghị quyết 20/2026/NQ-HĐND is single-source and must not be promoted alone
- [x] AGENTS.md states the direction rule
- [x] NOT: relax the rule for raised dates, which is the abuse the script exists to stop

## Verify
- `python3 -m unittest discover -s tests -v` → all tests pass
- `python3 scripts/validate_skills.py` → JSON with `"ok": true`
- `python3 scripts/audit_refresh.py --before <main roster> --after <same> --report-only`
  → `"unsupported": []`
- Replay the 2026-08-24 correction: lowering four dates reports `unsupported: []` and
  `lowered: 4`, and the reverting path leaves the file untouched
- `git diff --check` → no whitespace errors

## Notes
Replayed against the real 2026-08-24 correction (merged `main` at 9a266db vs 251df01):
`unsupported: []`, `lowered: 4`, and the roster comes back byte-identical through the
reverting path. Before this change the same replay reported four UNSUPPORTED and would
have raised every one of them back to a date nobody earned.

`--report-only` and the reverting path are driven by the same `unsupported` list, so they
cannot disagree; a test pins that end to end.

Not fixed here: `check_anchors.py` still reports 67/67 `TLS:SSLCertVerification` until
`SSL_CERT_FILE` is set. AGENTS.md documents the workaround. Separate spec.

