# Correct the 2026-08-31 weekly refresh before merge

**Deps**: weekly-skill-refresh-2026-08-24-verification, refresh-harness-verification

## Goal
PR #47 fails `Refresh / harness` with 6 test failures and `Refresh / anchors` with one
dead anchor. Correct the refresh on a branch off its own head, so the sourced material
it found this week ships and the unsourced material does not.

Five of the six failures are one behaviour: the refresh **rewrote** notes and status
fields rather than amending them, deleting caveats earlier correction passes had added.
The workflow prompt forbids exactly this ("Never delete an existing caveat, scope note,
or verification instruction ... If you believe one is wrong, say so in the summary and
leave it in place"). Four of the deleted caveats are the same ones the 24 August pass
restored; the tests that pass added are what caught the repeat.

The sixth failure is the harness's, not the refresh's: the Colosseum test asserts a
literal date format rather than the claim it documents.

## Files
- `vietnam-crypto-radar/references/baseline.md` (edited) — restore the Resolution 20 single-source status
- `vietnam-visa-check/data/vietnam_immigration_policy.json` (reverted) — restore the optional-pilot description
- `vietnam-visa-check/SKILL.md` (reverted) — version bump no longer earned
- `web3-opportunities/data/web3_opportunities.json` (edited) — restore 3 caveats, fix 1 url
- `tests/test_web3_opportunities.py` (edited) — assert the Colosseum window, not its formatting
- `README.md` (edited) — record the 31 August correction pass
- `docs/backlog/PRIORITY.md` (edited) — track this spec

## Acceptance
- [ ] Nghị quyết 20/2026/NQ-HĐND is `REPORTED / SINGLE-SOURCE (LOCAL)` while its only
      anchor is VnEconomy, and asserts no effective date
- [ ] `DIGITAL_ARRIVAL_CARD` describes the Tan Son Nhat pilot as optional, and keeps the
      instruction not to state the multi-airport expansion as fact
- [ ] `corelia-academy` and `unihackfest` both carry the 403-to-fetchers guardrail
- [ ] `drips-network` keeps the 14 July 2026 legacy-contract exploit warning
- [ ] `base-batches` points at a url that resolves
- [ ] The Colosseum test passes on any formatting that carries both Sep 28 and Nov 2,
      and still fails if either date is dropped or the two entries disagree
- [ ] This week's sourced material is kept: the Decree 284 six-month trigger, the
      implementing circulars, the deadline updates, `base-batches-accelerator`
- [ ] NOT: revert the whole refresh; NOT: relax a test to make a deletion pass

## Verify
- `python3 -m unittest discover -s tests -v` → all tests pass
- `python3 scripts/validate_skills.py` → JSON with `"ok": true`
- `SSL_CERT_FILE=/etc/ssl/cert.pem python3 scripts/check_anchors.py --targets baseline,web3` → 0 dead
- Colosseum test fails again if either date is removed from either entry
- `git diff --check` → no whitespace errors

## Notes
Two findings NOT fixed here, because they are outside the corrections the user approved
and neither breaks a check:

- The new Decree 284 bullets (the "6-month trigger", Circulars 89/2026/TT-BTC,
  90/2026/TT-BTC, 39/2026/TT-NHNN) add no anchors. `baseline.md` changed by 7 insertions
  and 6 deletions in total, none of them in the anchors section, so three new instrument
  numbers rest on nothing citable.
- The VON / G-Flow / GM Services / Dinogo status update names fidinam.com and
  vietnamplus.vn inline without adding either to the anchors section. The claim is
  correctly hedged, so this is anchor hygiene rather than an overstatement.

`audit_refresh.py` reported this refresh honest (0 rolled back) because every affected
entry's content changed, which it reads as support for the date bump. A rewritten note
satisfies it exactly as a verified one does. That is the same hole recorded in the
24 August spec and it is still open.
