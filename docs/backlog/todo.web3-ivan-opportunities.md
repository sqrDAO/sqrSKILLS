# Verify September founder residency opportunities
**Deps**: —

## Goal
Review the five programs in Ivan's 11 September 2026 post against official
sources and update the bundled opportunity catalog without importing its errors.

## Files
- `web3-opportunities/data/web3_opportunities.json` (edited) — verified program snapshots.
- `web3-opportunities/references/sources.md` (edited) — official sources and review caveats.
- `web3-opportunities/SKILL.md` (edited) — version-only patch bump for data update.
- `evals/web3-opportunities/cases*.jsonl` (edited) — regenerate data-derived truth.
- `README.md` (edited) — describe targeted residency coverage.
- `docs/backlog/PRIORITY.md` (edited) — track review pending approval.

## Acceptance
- [x] Review all five programs and record inclusion or deferral reasons.
- [x] Anchor accepted terms/deadlines to official pages, retaining conflicts as caveats.
- [x] Preserve unrelated entry verification dates and existing generic program scope.
- [x] New entries use supported facets; unknown equity terms are not labelled free funding.
- [x] NOT: copy unsupported amounts, guarantee admissions, or change skill instructions.

## Verify
- `python3 scripts/validate_skills.py` → valid repository.
- `python3 -m unittest discover -s tests -v` → all tests pass.
- `python3 scripts/check_unanchored.py --since origin/main` → no new unsourced instruments.
- `python3 scripts/check_anchors.py --targets web3` → no definitive dead anchors.
- `python3 evals/scripts/build_web3_cases.py --check` → truth matches refreshed roster.
- `python3 web3-opportunities/scripts/query_opportunities.py --search residency` → YZi, Fabric and Forge snapshots.
- `git diff --check` → no whitespace errors.

## Notes
- Discovery: https://x.com/ivan_nomadz/status/2098387505225597359
- Read the evaluation wiki; this update changes data and release metadata only.
  No behavioral claim is made; regenerate truth rather than rerun saturated prompt gates.
- Forma remains a sourced discovery candidate until funding/equity and housing conflict resolve.
- Verified: validator, 191 tests, split truth, query checks and whitespace pass.
- Anchors: 45 checked, 44 resolved, 0 dead; existing Tribe HTTP 403 unverified.
- Freshness audit: only YZi changed among existing entries; all other dates retained.
- Keep this spec todo and PR unmerged until explicit approval.
