# Repository harness and docs workflow
**Deps**: —

## Goal
Give sqrSKILLS the same explicit checks, spec lifecycle, and PR-only development
flow used in YouAI, adapted to this repository's portable Python skills.

## Files
- `scripts/validate_skills.py` (new) — stdlib-only repository validator
- `tests/test_validate_skills.py` (new) — validator regression tests
- `.github/workflows/test.yml` (new) — required CI harness
- `.github/main-branch-protection.json` (new) — auditable GitHub protection policy
- `AGENTS.md` (edited) — checks, backlog lifecycle, Git flow, and spec format
- `README.md` (edited) — contributor-facing validation and backlog commands
- `web3-opportunities/data/web3_opportunities.json` (edited) — repair JSON exposed by harness
- `web3-opportunities/SKILL.md` (edited) — patch version for data repair
- `docs/backlog/PRIORITY.md` (new) — ranked active-spec index
- `docs/backlog/todo.repository-harness.md` (new) — this implementation spec

## Acceptance
- [ ] One local command validates skill frontmatter, versions, referenced scripts,
      README inventory, JSON data, Python syntax, and backlog document shape
- [ ] Validator output is machine-readable JSON; diagnostics go to stderr
- [ ] Unit tests prove the validator accepts the repository and rejects malformed skills
- [ ] Pull requests and pushes to `main` run a status check named `Skill Harness`
- [ ] Agent guidance documents Plan → Do → Check → Verify → Act and requires explicit
      user approval before `todo.*` becomes `done.*`
- [ ] Contributor docs show the same commands CI runs
- [ ] Existing bundled datasets pass strict JSON parsing
- [ ] GitHub `main` rejects force pushes/deletion and requires a PR plus `Skill Harness`
- [ ] NOT: add a package manager or non-stdlib runtime dependency

## Verify
- `python3 scripts/validate_skills.py` → JSON with `"ok": true`
- `python3 -m unittest discover -s tests -v` → all tests pass
- `git diff --check` → no whitespace errors
- `gh api repos/sqrDAO/sqrSKILLS/branches/main/protection` → PR and required-check rules present

## Notes
Completion approved by the user on 2026-07-18 after local verification and push of
implementation commit `4ab1514`. The review requirement was subsequently adjusted
for a sole-maintainer repository: PR and harness gates remain required, but a
different person is not required to approve the last push.
