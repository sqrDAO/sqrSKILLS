# Anchor a confidence promotion, not just a new instrument number

**Deps**: unanchored-instrument-check

## Goal
`check_unanchored.py` judges **instrument numbers new to the file**. The
2026-09-07 refresh (#51) walked past it twice, and both misses are demonstrated
rather than hypothetical.

**A claim re-attached to an instrument the file already knew.** The 1 September
pass had marked a six-month grace period UNVERIFIED and written "Do not tell a
user they have a grace period." The refresh replaced that with "**CONFIRMED**",
hanging it on Resolution 05/2025/NQ-CP — a standing instrument. The bullet
introduced no new number, so the check found nothing. The claim turned out to be
true (khoản 2 Điều 7, two independent Tier-2 sources, added on the fix branch),
but it shipped citing nothing, and a reviewer reading the diff saw a caveat
become a fact with no source attached. That is p005 exactly: freshness treated as
a field to advance rather than a claim to earn.

**Politburo numbering is unmatched.** `INSTRUMENT` expects `NNN/QĐ-XX`. Party
instruments are `NNN-QĐ/TW` — hyphen before the type, slash inside it. So
`212-QĐ/TW`, added as "EFFECTIVE / CONFIRMED (POLITICAL)" with no anchor, was
invisible to the matcher, as are `69-QĐ/TW` and `264-QĐ/TW` which it replaces.

The roster half of the same refresh needs nothing: `RosterFactTest` caught all
three data regressions. The prose half is where the guard is thin.

## Files
- `scripts/check_unanchored.py` (edited) — judge promotions; match `-QĐ/TW`
- `tests/test_check_unanchored.py` (edited) — both gaps, both directions
- `AGENTS.md` (edited) — restate what the check covers under Repository Checks
- `docs/backlog/PRIORITY.md` (edited) — track this spec

## Acceptance
- [ ] A line the change **adds or rewrites** that raises confidence — gains
      CONFIRMED/EFFECTIVE, or sheds UNVERIFIED/DRAFT/PROPOSED/RUMORED/REPORTED/
      SINGLE-SOURCE/NEEDS_PRIMARY_SOURCE — fails unless the same change adds an
      anchor, whether or not the instrument is new to the file
- [ ] `212-QĐ/TW`, `69-QĐ/TW`, `264-QĐ/TW` are recognised as instruments, and an
      unanchored new one fails the same way `NNN/QĐ-XX` does
- [ ] Fails against `baseline.md` as the #51 refresh left it, naming both the
      grace-period promotion and `212-QĐ/TW`; passes against the corrected tree
- [ ] A promotion that adds an anchor in the same change passes
- [ ] A **demotion** (fact → UNVERIFIED, or a status lowered) always passes, with
      no anchor required. Retreating to a weaker claim is the behaviour the
      refresh prompt asks for and must never cost anything
- [ ] Touching a line without changing its confidence — reflowing, fixing a typo,
      adding detail beside a standing CONFIRMED — does not fire
- [ ] Still runs offline, still judges only what the change introduces, still
      exempts self-labelled-unconfirmed text and the two exempt headings
- [ ] NOT: scanning the standing file. That was tried in the parent spec, reported
      14 instruments, and would demand a data project before the harness could go
      green — the pressure would be to weaken the check rather than source the
      claims
- [ ] NOT: checking that the anchor is *about* the claim. This catches absence,
      not mismatch, and the parent spec's limit stands

## Verify
- `python3 scripts/check_unanchored.py --since main` on the #51 refresh commit →
  fails, naming the grace-period bullet and `212-QĐ/TW`
- Same command on the corrected tree → `"ok": true`
- `python3 -m unittest discover -s tests -v` and `python3 scripts/validate_skills.py`

## Notes
The unit of judgment is what moves, not what is new. "New instrument number" was
a good proxy for the 31 August failure because that refresh invented circulars;
it is a bad proxy for a refresh that rewrites a verdict on an instrument the file
has carried for months. Both are the same act — asserting more than the sources
support — and the second is harder to see in review, because the number in the
line is familiar.

Detecting a promotion reads the diff for confidence markers, not prose, so it
stays a text check. `UNCONFIRMED` already holds half the vocabulary.

One thing this still will not catch, and should not be quietly folded in: #51's
summary reported only additions while the diff deleted four things — Alliance
DAO's second deadline, the Drips exploit caveat, the 1 September verification
note, and the stablecoin/CBDC watchlist question — against a prompt that
explicitly calls a summary listing only additions a false report. A diff-versus-
summary check is a separate spec if it is worth one.
