# Add the Web3 legal agreements skill
**Deps**: —

## Goal
Import the user-supplied `web3-legal-agreements.skill` archive as an installable,
portable repository skill, preserving its drafting guidance and bundled resources.

## Files
- `web3-legal-agreements/SKILL.md` (new) — prompt, version, tool metadata, portable routing.
- `web3-legal-agreements/references/*.md` (new) — six supplied reference documents.
- `web3-legal-agreements/assets/*.md` (new) — supplied checklist and ToS scaffold.
- `README.md` (edited) — inventory, direct installation, and requirements.
- `AGENTS.md` (edited) — environment requirements for the new skill.
- `docs/backlog/PRIORITY.md` (edited) — record the approved addition.

## Acceptance
- [x] All nine archive files are imported; references and assets remain unchanged.
- [x] Skill has SemVer and advisory tools, resolves resources from its installed directory,
      and handles unavailable companion skills without requiring their installation.
- [x] README documents installation and web access for current-law checks; no API keys.
- [x] Repository checks pass and every resource in the prompt's reference map exists.
- [x] NOT: a legal-content refresh, new helper scripts, global installation, or merge.

## Verify
- `python3 scripts/validate_skills.py` → no errors, includes the new skill.
- `python3 -m unittest discover -s tests -v` → all tests pass.
- `python3 scripts/check_unanchored.py --since origin/main` → no new unanchored instruments.
- `git diff --check` → no whitespace errors.
- Compare imported paths and resource bytes against the supplied ZIP; inspect the
  prompt diff to confirm only metadata and runtime compatibility adaptations.

## Notes
- Source: `/Users/longpham/Downloads/web3-legal-agreements.skill`.
- The supplied regulatory snapshot is dated early 2026; its re-verification rule stays.
- User approved completion and requested commit/push on 2026-09-11.
- Verified: repository validator (11 skills), 191 unit tests, unanchored-instrument
  check, whitespace check, nine archive paths, and eight byte-identical resources.
- Unit tests passed with external DNS access after the sandbox blocked resolution.
- The generic skill-creator validator rejects the repository-required `version`
  field; retained it per AGENTS.md and used the repository validator as authority.
- Git commands succeed but report an existing AppleDouble pack-index warning.
