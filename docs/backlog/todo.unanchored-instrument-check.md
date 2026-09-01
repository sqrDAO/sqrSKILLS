# Fail the harness when a new instrument number arrives with no anchor

**Deps**: weekly-skill-refresh-2026-08-31-verification

## Goal
The 31 August 2026 refresh added three circular numbers and two legal claims to
`baseline.md` citing nothing, and every gate in the repo passed them. One of the
claims was also wrong: it named the State Bank as an Article 9 enforcement body
when Điều 15(4)(b) gives State Bank authorities only Điều 10–13. It was caught by
a code reviewer and then by fetching the decree — not by anything in `tests/` or
`scripts/`.

Nothing here is an oversight in the existing checks. `validate_skills.py` does not read
prose. `check_anchors.py` tests URLs that exist, so a claim citing *nothing* is invisible to
it by construction — the failure mode it was built for is an anchor that rots, not an
assertion that never had one. `audit_refresh.py` governs `last_verified` on the roster and
does not look at `baseline.md` at all.

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
- [x] An instrument number **newly introduced by the change under review** with no
      anchor for it fails the check
- [x] A number already carrying an anchor passes, including one whose anchor names
      a different instrument in the same line
- [x] A number inside an explicitly UNVERIFIED / DRAFT / REPORTED block passes —
      labelling a claim as unconfirmed is the documented alternative to sourcing
      it, and the check must not push an author into deleting the label instead
- [x] A number already present in the base revision does not fail, however it is
      cited — the check governs what a change adds, not the standing file
- [x] An anchor naming a range (`Decisions 3809–3812/QĐ-UBND`) anchors every
      instrument in it
- [x] Runs offline. This is a text check, not a fetch; `check_anchors.py` stays
      the network one
- [x] It fails against `baseline.md` as #47 left it, on the three circulars, and
      passes against `main` as #48 corrected it — the regression that motivated it
- [x] NOT: a spell-check for citation style; NOT: anything needing the network or
      a per-instrument allowlist; NOT: a demand that the standing file be brought
      up to date before the check can go green

## Verify
- `python3 scripts/check_unanchored.py --since origin/main` → `"ok": true` on `main`
- Same command against the #47 refresh commit → fails, naming the three circulars
- `python3 scripts/check_unanchored.py --all` → reports the standing file's 14
  pre-existing unanchored instruments without failing the harness
- `python3 -m unittest discover -s tests -v` and `python3 scripts/validate_skills.py`

## Notes
**Scanning the whole file was tried first and was wrong.** It reported 14 instruments on
corrected `main`: some are anchored under a range the matcher did not expand, but most are
long-standing claims whose anchors are titled by subject rather than by number. Failing the
harness on those would demand a data project before the check could ever go green, and the
pressure would be to weaken the check rather than source the claims. The failure mode being
defended against is a *refresh adding* an uncited instrument, so the check compares against
a base revision and judges only what the change introduces. `--all` still reports the
standing backlog, without a verdict.

Scope it to `vietnam-crypto-radar` first. That is where instrument numbers carry
legal weight and where the misses happened; `vietnam-visa-check` cites a smaller,
more stable set and can be added once the check has earned its keep.

The interesting design question is what counts as "an anchor for it". Matching the bare
number inside the anchors section is the cheap version and will do to start, but an anchor
whose URL is unrelated to the instrument it sits beside would pass. That is a weaker
guarantee than it looks, and the spec should not pretend otherwise: this catches *absence*,
not *mismatch*. Mismatch needs a fetch and belongs with `check_anchors.py` if it is worth
doing at all.

Standalone rather than folded into `validate_skills.py`, so it can be skipped
deliberately the way the network checks are, without weakening the harness.
