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
Primary confirmation: Da Nang city portal's 22 August 2026 executive summary.

## Notes
Rebased onto `main` after #31 and #33 merged. Conflicts resolved in `README.md`,
`SKILL.md`, `baseline.md`, `PRIORITY.md`, and `tests/test_vietnam_crypto_radar.py`.

The `baseline.md` conflict was not cosmetic. This branch's header said "anchors without a
17 August marker were last checked on 3 August 2026", which was true when written but is
not any more: anchors now carry 24 August markers too, so that phrasing sweeps them in.
Taking it also failed `test_the_two_unmarked_anchor_dates_agree`, added in #33. The merged
header carries both sweeps and keeps the wording that test pins.

That test turned out to be brittle in its own right — it matched a single literal space
between words, so the correctly merged header failed it purely because the phrase wraps
across a blockquote line. Both regexes now tolerate `[\s>]+`, asserting the fact rather
than the line-wrap.

Verification of the branch's own claims against the primary anchor on 24 August 2026: all
four decisions, operators, and durations check out exactly, as does Sở Khoa học và Công
nghệ as the controlling body. What was missing was context, not accuracy — see the added
acceptance items.
