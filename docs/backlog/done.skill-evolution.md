# Add the skill evolution skill
**Deps**: —

## Goal
Import the supplied skill-evolution prompt for auditing skills and measuring
instruction changes, with portable metadata and honest toolkit requirements; resolve review ambiguity
about project gates and harness compatibility.

## Files
- `skill-evolution/SKILL.md` (new) — imported workflow and integration corrections.
- `README.md` (edited) — inventory, install command, requirements.
- `AGENTS.md` (edited) — per-skill requirements.
- `docs/backlog/PRIORITY.md` (edited) — track the addition.

## Acceptance
- [x] Import the supplied workflow with version 0.1.1 and advisory tools.
- [x] Toolkit references are optional external examples, not missing bundled files.
- [x] Author wiki and raw traces stay outside the installed skill; rollback keeps
      diagnosis and preserves unrelated work.
- [x] Research claims have a primary anchor; local heuristics and unverified
      experience reports are distinguished from research results.
- [x] README documents installation and evaluation prerequisites.
- [x] Opus review: project gate/eligibility rules take precedence; external case
      fields are illustrative, and optional shell runners need matching permissions.
- [x] Repository checks pass; change is isolated on a branch from origin/main.
- [x] NOT: build a new harness, run paid evaluation campaigns, change other skills,
      install globally, or claim measured improvement from an import.

## Verify
- `python3 scripts/validate_skills.py` → passes.
- `python3 -m unittest discover -s tests -v` → all tests pass.
- `python3 scripts/check_unanchored.py --since origin/main` → passes.
- `python3 scripts/check_anchors.py --timeout 5 --attempts 1` → no dead anchors.
- `git diff --check` → no whitespace errors.
- Compare the imported prompt with the archive; inspect toolkit fallbacks,
  wiki isolation, research attribution, and referenced-file claims.

## Notes
- Source: user-supplied `skill-evolution.skill` archive, containing only SKILL.md.
- This is an import verified by inspection, not a gated behavioral improvement.
- Verified: repository validator (13 skills), all 191 tests, unanchored and
  whitespace checks; anchor check: 106 checked, 98 resolved, 0 dead, 8 unverified.
- New paper anchor opened separately; default anchor checker scans bundled datasets.
- Generic skill-creator quick validator rejects the repository-required version
  field; repository harness is authoritative for that metadata.
- Opus 5 reviewed head 0b41d34: no P1 findings; gate-policy and harness-contract
  ambiguities accepted for clarification. Source-coverage concern was already
  disclosed and the paper opened separately; no behavior improvement claimed.
- Post-review validation: all 191 tests, repository validator, unanchored check,
  and whitespace check pass; prompt version 0.1.1.
- User approved marking done and merging PR #57 on 2026-09-11.
