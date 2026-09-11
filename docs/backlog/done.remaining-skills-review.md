# Review the remaining operational and business-planning skills
**Deps**: —

## Goal
Audit the six skills without recent substantive review, reproduce concrete
defects safely, and leave prioritized findings and proposed fixes for review.

## Files
- `docs/reviews/2026-09-11-remaining-skills/` (new) — per-skill audits and offline probes.
- `docs/backlog/done.remaining-skills-review.md` (new) — scope and verification record.
- `docs/backlog/PRIORITY.md` (edited) — track the review awaiting user disposition.

## Acceptance
- [x] Review telegram-send, list-telegram-chats, telegram-group-summary,
      nearby-places-search, luma-calendar, and business-model-to-market.
- [x] Each audit uses the same six-dimension rubric and cites exact file lines.
- [x] Reproduce headline script findings using isolated fixtures; verify external
      API claims against current primary documentation.
- [x] Report test results and distinguish confirmed defects from ungated proposals.
- [x] NOT: change skill behavior, contact real recipients, or run a prompt eval campaign.

## Verify
- `python3 docs/reviews/2026-09-11-remaining-skills/probe.py` → JSON evidence; no live API calls.
- `python3 scripts/validate_skills.py` → pass.
- `python3 -m unittest discover -s tests -v` → pass, with environment failures disclosed.
- `python3 scripts/check_unanchored.py --since origin/main` → no new unanchored instruments.
- Walk all six audits and confirm each headline against its cited code and probe output.

## Notes
- Review baseline: main commit `4d1bbb6`.
- Existing legal, visa, Web3, wiki, and evaluation backlog findings are not duplicated.
- User approved completion and merge in PR #59.
- Verified: six audits and isolated probes complete; validator, 192 tests,
  unanchored check, and whitespace check pass at the audit baseline.
- Subsequent behavior fixes are tracked in `done.remaining-skills-fixes.md`.
