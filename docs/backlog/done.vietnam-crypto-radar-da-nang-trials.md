# Add Da Nang controlled crypto trials
**Deps**: refresh-harness-verification

## Goal
Add the four Da Nang technology trials approved on 22 August 2026 to
`vietnam-crypto-radar`, with primary-source support and clear boundaries between
these local trials, the national licensed crypto-market pilot, and lawful means of
payment.

## Files
- `vietnam-crypto-radar/SKILL.md` (edited) — route Da Nang sandbox questions and bump version to 0.4.7
- `vietnam-crypto-radar/references/baseline.md` (edited) — add the four decisions and dated status
- `vietnam-crypto-radar/references/adoption.md` (edited) — replace generic gateway-only context with confirmed local trials
- `vietnam-crypto-radar/references/sources.md` (edited) — add the Da Nang primary anchor and queries
- `tests/test_vietnam_crypto_radar.py` (edited) — preserve the four decisions and legal boundary
- `README.md` (edited) — include local controlled trials in the skill inventory
- `docs/backlog/PRIORITY.md` (edited) — rank this open spec
- `docs/backlog/todo.vietnam-crypto-radar-da-nang-trials.md` (new) — task spec

## Acceptance
- [x] Decisions 3809, 3810, 3811, and 3812/QĐ-UBND are recorded with solution, operator, and duration
- [x] The trials that predate them are recorded too: 1181/QĐ-UBND (Basal Pay) and 2895/QĐ-UBND (MIMO, running to Dec 2028)
- [x] The enabling instrument, Nghị quyết 20/2026/NQ-HĐND, is recorded as what the approvals sit under
- [x] Filed-but-undecided applications (VON, G-Flow, GM Services, Dinogo) are tracked under IN MOTION
- [x] Trial sites are named per decision, not generalised to a whole ward
- [x] The Umi Pay prediction-market discrepancy is labelled UNVERIFIED rather than resolved by guess
- [x] No unqualified "first crypto trial in Vietnam" claim: Basal Pay predates MIMO, and each operator's narrower claim stays attributed
- [x] The trial count is stated as a floor, not a total — the regime is not crypto-specific and the 2026 first batch was not enumerated
- [x] The trials are classified as effective from 22 August 2026 and sourced to Da Nang's official portal
- [x] The baseline `LAST VERIFIED` date advances only for content checked on 24 August 2026
- [x] Skill version is bumped to `0.4.7` (`0.4.6` was taken by the 2026-08-24 refresh in #31)
- [x] Da Nang sandbox questions route to the regulatory baseline and adoption context
- [x] Regression coverage protects the decision set, primary anchor, and national-license caveat
- [x] NOT: describe a local technology-trial approval as a national CASP/exchange license
- [x] NOT: imply that USDT/USDC became a generally lawful means of payment in Vietnam

## Verify
- `python3 scripts/validate_skills.py` → JSON with `"ok": true`
- `python3 -m unittest discover -s tests -v` → all tests pass
- `python3 scripts/check_anchors.py --targets baseline` → no dead baseline anchors
- `git diff --check` → no whitespace errors
- `rg -n "3809|3810|3811|3812|PayD|TORA|Umi Pay|Money X-Border" vietnam-crypto-radar` → all trials are discoverable

## Notes
Primary confirmation: Da Nang city portal, 22 August 2026. Rebased onto `main` after #31
and #33; conflicts resolved in `README.md`, `SKILL.md`, `baseline.md`, `PRIORITY.md`, and
`tests/test_vietnam_crypto_radar.py`.

The `baseline.md` conflict was not cosmetic. #32's header ("anchors without a 17 August
marker…") was true when written but not once anchors carry 24 August markers, and it failed
`test_the_two_unmarked_anchor_dates_agree` from #33. That test was itself brittle — it
matched one literal space, so a correctly merged header failed it purely because the phrase
now wraps across a blockquote line. Both regexes tolerate `[\s>]+` and assert the fact.

Every fact #32 stated verified exactly: four decisions, operators, durations, and Sở Khoa
học và Công nghệ as controlling body. What was missing was context, not accuracy.

A second pass before merge caught three defects in this spec's own completeness work:

1. It called MIMO "the first such licence in the country" while listing Basal Pay, an
   earlier Da Nang crypto/fiat trial, directly above — the self-contradiction class #33
   exists to catch. Both operators claim a narrower first (Dragon Lab: first non-custodial
   intermediation into VND; AlphaTrue: first to fully integrate the Travel Rule). Both now
   attributed.
2. "Six trials are live" was stated as a total. The regime is not crypto-specific and the
   2026 first batch was never enumerated, so six is a floor — stating a total would repeat
   the undercount this spec set out to fix.
3. The Effective column carried MIMO's issuance date (31 Dec 2025) while its trial runs
   from 18 Dec 2025.

Three regression tests cover these, plus a CafeF anchor corroborating Basal Pay's date.

Completion approved by the user on 24 August 2026. Shipped in #35, superseding #32.
Checks at merge: validate_skills.py ok, 92/92 tests, 32/32 baseline anchors resolve with
0 dead, git diff --check clean.
