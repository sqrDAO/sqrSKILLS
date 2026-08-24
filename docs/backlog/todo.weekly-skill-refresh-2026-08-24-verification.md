# Correct the 2026-08-24 weekly refresh after merge

**Deps**: weekly-skill-refresh-2026-08-17-verification, refresh-harness-verification

## Goal
PR #31 merged (9a266db) before review findings were applied, so 13 data-correctness
defects are on `main`. Correct them against live sources, and add the regression tests
the roster never had, so the same class cannot pass every gate again.

The refresh passed `validate_skills.py`, `audit_refresh.py`, and all 69 tests. Nothing
it broke was structural: wrong `status` values that steer `query_opportunities.py`,
deleted deadlines and warnings, and `last_verified` bumps onto claims nobody re-checked.
`audit_refresh.py` treats any content change as self-evident support for a date bump,
which is exactly the hole a rewritten note walks through.

## Files
- `web3-opportunities/data/web3_opportunities.json` (edited) — 13 entry corrections
- `vietnam-crypto-radar/references/baseline.md` (edited) — unmarked-anchor date, QĐ 1624 row, second Tier-1 anchor
- `tests/test_web3_opportunities.py` (new) — pin the roster's cross-field invariants and corrected facts
- `tests/test_vietnam_crypto_radar.py` (edited) — pin the two unmarked-anchor dates agree, and the QĐ 1624 row
- `README.md` (edited) — record the 24 August correction pass
- `docs/backlog/PRIORITY.md` (edited) — track this spec

## Acceptance
- [x] No entry is `open` while its own notes say the program does not exist
- [x] No `closed` entry advertises work "in progress" in `cadence`
- [x] `ethereum-protocol-fellowship` is not `open` while the EPF7 cohort runs Jun–Nov 2026
- [x] `alliance-dao` carries both the 23 Sep early and 18 Nov regular deadlines
- [x] The Drips legacy-contract exploit warning and the Colosseum Sep 28–Nov 2 window are restored
- [x] `corelia-academy` and `unihackfest` both carry the 403-to-fetchers / 200-in-a-browser guardrail
- [x] No entry's `url` points at a dead or redirecting target (`polkadot.network/development`, `grants.web3.foundation`)
- [x] No entry's `last_verified` is later than `_meta.last_updated`
- [x] The baseline header and anchors section state the same unmarked-anchor date
- [x] The QĐ 1624 row states the signing date and that no effective date is in the anchor
- [x] Every corrected claim was re-checked against the program's own channel on 24 Aug 2026
- [x] The new tests fail against merged `main` (9/11 roster, 3/3 baseline) and pass here
- [ ] NOT: revert to last week's text where this week's claim turned out to be right (YZi Labs)

## Verify
- `python3 scripts/validate_skills.py` → JSON with `"ok": true`
- `python3 -m unittest discover -s tests -v` → all tests pass
- `python3 scripts/audit_refresh.py --before <main> --after <branch> --report-only` → `"unsupported": []`
- `SSL_CERT_FILE=/etc/ssl/cert.pem python3 scripts/check_anchors.py --targets baseline,web3` → 0 dead
- `git diff --check` → no whitespace errors

## Notes
Two review findings changed on contact with the sources. YZi Labs' 13 Sep cutoff is real
and stated on their own blog (14 Aug 2026), so that date bump was earned — the defect was
the deleted year-round rolling-entry model, not the date. Colosseum was worse than
reported: the refresh named the *next* hackathon "Frontier", which had already run
Apr 6–May 11 2026.

There is no `_meta.enums` block in the roster and nothing enforces the `status` or `type`
vocabulary; `test_every_status_is_in_the_known_vocabulary` is the first thing that does.

Two harness sharp edges found while verifying, worth separate specs:
- `audit_refresh.py` reverts in place by default. A plain audit run rewrote the working
  tree, rolling back five unearned `last_verified` bumps (a16z-csx, tachyon-accelerator,
  base-batches, antler-web3, ethglobal). Correct rollbacks, surprising side effect.
- `check_anchors.py` reported 67/67 `TLS:SSLCertVerification` until `SSL_CERT_FILE` was
  set. AGENTS.md documents the workaround; the script could fall back on its own.
