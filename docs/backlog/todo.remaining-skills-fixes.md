# Fix confirmed defects in the remaining skills
**Deps**: remaining-skills-review

## Goal
Correct the confirmed runtime and data-fidelity defects found in the six-skill
review, while preserving the existing user-facing workflows and leaving
speculative prompt improvements explicitly ungated.

## Files
- `telegram-group-summary/scripts/fetch_messages.py` (edited) — safe polling,
  JSON/JSONL fixtures, UTC cutoffs, captions/channel posts, bounded limits.
- `telegram-send/scripts/send.py`, `telegram-send/scripts/list_groups.py` (edited)
  — literal code preservation, JSON results, deterministic ordering.
- `list-telegram-chats/scripts/list_chats.py` (edited) — timestamps and ordering.
- `nearby-places-search/scripts/search_places.py` (edited) — scoped memory,
  free-text types, explicit radius/error behavior, deterministic ranking.
- `luma-calendar/scripts/luma_calendar.py` (edited) — current documented API
  routes/payload names and structured transport errors.
- `business-model-to-market/scripts/build_gtm_workbook.py` (edited) — preserve
  false/zero values, blank unknown scores, JSON stdout.
- Corresponding `SKILL.md` and references (edited) — align commands/contracts;
  bump SemVer patch versions.
- `tests/test_remaining_skills.py` (new) — offline regression coverage.
- `README.md`, `docs/backlog/PRIORITY.md` (edited) — support scope and status.

## Acceptance
- [x] Opus follow-up: short location tokens cannot select arbitrary cache entries;
      free-text results are filtered by exact distance before ranking.
- [x] Canvas stage references agree with SKILL.md; probe freezes the active clock;
      empty workbook containers remain TBD while false/zero remain explicit.
- [ ] Summary documentation limits local history support to raw Telegram JSON/JSONL;
      native OpenClaw transcripts and SQLite require an export or separate adapter.
- [ ] Literal placeholder-like text cannot collide with protected code regions.
- [ ] Luma CLI venue example matches the documented manual-address shape.
- [ ] No read-only summary call changes Telegram `allowed_updates`; valid UTC
      filtering, captions, channel posts, JSONL records, and limits work.
- [ ] Code spans remain literal; send/list outputs are valid JSON and deterministic.
- [ ] Nearby cache never selects coordinates from an unrelated location; API
      errors and effective radius are truthful.
- [ ] Luma uses current public routes and required create fields; transport errors
      remain structured JSON.
- [ ] Workbook preserves false/zero answers and does not rank incomplete scores.
- [ ] Existing behavior remains covered by all repository checks.
- [ ] NOT: add live API calls, send messages/guests, change legal/visa datasets,
      or run a prompt evaluation campaign.

## Verify
- `python3 -m unittest discover -s tests -v` → all tests pass.
- `python3 scripts/validate_skills.py` → pass; all changed skills retain valid SemVer.
- `python3 docs/reviews/2026-09-11-remaining-skills/probe.py --dependency-dir /tmp/sqrskills-review-deps` → updated evidence passes.
- `python3 scripts/check_unanchored.py --since origin/main` → no unanchored instruments.
- `git diff --check` → no whitespace errors.

## Notes
- Implement confirmed code defects first; audit-only proposals remain recorded in
  the review and are not silently promoted into this change.
- The review PR is #59; append implementation commits to its branch.
- Review follow-ups verified: 204 tests run (202 passed, 2 optional skips);
  all 12 focused tests pass with openpyxl. Validator/unanchored/diff checks pass.
- Opus fixes verified: all 207 tests pass with openpyxl, all four workbook modes
  reopen, probe cutoff error is 0.0 hours; validator/unanchored/diff checks pass.
