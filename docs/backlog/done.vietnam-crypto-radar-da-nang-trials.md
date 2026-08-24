# Add Da Nang controlled crypto trials
**Deps**: refresh-harness-verification

## Goal
Add the four Da Nang technology trials approved on 22 August 2026 to
`vietnam-crypto-radar`, with primary-source support and clear boundaries between
these local trials, the national licensed crypto-market pilot, and lawful means of
payment.

## Files
- `vietnam-crypto-radar/SKILL.md` (edited) — route Da Nang sandbox questions and bump version
- `vietnam-crypto-radar/references/baseline.md` (edited) — add the four decisions and dated status
- `vietnam-crypto-radar/references/adoption.md` (edited) — replace generic gateway-only context with confirmed local trials
- `vietnam-crypto-radar/references/sources.md` (edited) — add the Da Nang primary anchor and queries
- `tests/test_vietnam_crypto_radar.py` (edited) — preserve the four decisions and legal boundary
- `README.md` (edited) — include local controlled trials in the skill inventory
- `docs/backlog/PRIORITY.md` (edited) — rank this open spec
- `docs/backlog/todo.vietnam-crypto-radar-da-nang-trials.md` (new) — task spec

## Acceptance
- [x] Decisions 3809, 3810, 3811, and 3812/QĐ-UBND are recorded with solution, operator, and duration
- [x] The trials are classified as effective from 22 August 2026 and sourced to Da Nang's official portal
- [x] The baseline `LAST VERIFIED` date advances only for content checked on 24 August 2026
- [x] Skill version is bumped from `0.4.5` to `0.4.6`
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
