# Fail the harness when a new instrument number arrives with no anchor

**Deps**: weekly-skill-refresh-2026-08-31-verification

## Goal
The 31 August 2026 refresh added three circular numbers and two legal claims to
`baseline.md` citing nothing, and every gate in the repo passed them. One of the
claims was also wrong: it named the State Bank as an Article 9 enforcement body
when Điều 15(4)(b) gives State Bank authorities only Điều 10–13. It was caught by
a code reviewer and then by fetching the decree — not by anything in `tests/` or
`scripts/`.

Nothing here is an oversight in the existing checks. `validate_skills.py` does not
read prose. `check_anchors.py` tests URLs that exist, so a claim citing *nothing*
is invisible to it by construction — the failure mode it was built for is an
anchor that rots, not an assertion that never had one. `audit_refresh.py` governs
`last_verified` on the roster and does not look at `baseline.md` at all.

So the gap is specific and mechanical: **a new instrument number can appear in
`baseline.md` with no anchor added beside it, and nothing notices.** That is worth
closing precisely because the skill's whole value is that a stated fact has a
source behind it.

## Files
- `scripts/check_unanchored.py` (new) — the check
- `tests/test_check_unanchored.py` (new) — its own tests, both directions
- `.github/workflows/test.yml` (edited) — run it in `Skill Harness`
- `AGENTS.md` (edited) — document it under Repository Checks
- `docs/backlog/PRIORITY.md` (edited) — track this spec

## Acceptance
- [ ] An instrument number matching `\d+/20\d\d/(NĐ-CP|TT-BTC|TT-NHNN|QĐ-\w+|NQ-\w+|QH\d+)`
      that appears in `baseline.md` with no anchor for it fails the check
- [ ] A number already carrying an anchor passes, including one whose anchor names
      a different instrument in the same line
- [ ] A number inside an explicitly UNVERIFIED / DRAFT / REPORTED block passes —
      labelling a claim as unconfirmed is the documented alternative to sourcing
      it, and the check must not push an author into deleting the label instead
- [ ] Runs offline. This is a text check, not a fetch; `check_anchors.py` stays
      the network one
- [ ] It fails against `baseline.md` as #47 left it, on the three circulars, and
      passes against `main` as #48 corrected it — the regression that motivated it
- [ ] NOT: a spell-check for Vietnamese legal citation style; NOT: anything that
      needs the network or a per-instrument allowlist to stay green

## Verify
- `python3 scripts/check_unanchored.py` → JSON, `"ok": true` on `main`
- `git stash` the #47 baseline text in, re-run → fails naming the three circulars
- `python3 -m unittest discover -s tests -v` and `python3 scripts/validate_skills.py`

## Notes
Scope it to `vietnam-crypto-radar` first. That is where instrument numbers carry
legal weight and where the misses happened; `vietnam-visa-check` cites a smaller,
more stable set and can be added once the check has earned its keep.

The interesting design question is what counts as "an anchor for it". Matching the
bare number inside the anchors section is the cheap version and will do to start,
but an anchor whose URL is unrelated to the instrument it sits beside would pass.
That is a weaker guarantee than it looks, and the spec should not pretend
otherwise: this catches *absence*, not *mismatch*. Mismatch needs a fetch and
belongs with `check_anchors.py` if it is worth doing at all.

Worth a decision before building: whether the check belongs in `validate_skills.py`
instead of standing alone. Separate is proposed here so it can be skipped
deliberately, the way the network checks are, without weakening the harness.
