# Add the Vietnam legal advisor skill
**Deps**: —

## Goal
Import the supplied skill as a reusable Vietnamese legal drafting and review
skill, with portable resources and without assuming the user's company identity.

## Files
- `vietnam-legal-advisor/SKILL.md` (new) — prompt, metadata, portable routing.
- `vietnam-legal-advisor/references/*.md` (new) — seven supplied domain references.
- `vietnam-legal-advisor/assets/document-library.md` (new) — document skeletons.
- `README.md` (edited) — inventory, install command, requirements.
- `AGENTS.md` (edited) — environment requirements.
- `docs/backlog/PRIORITY.md` (edited) — track the addition.

## Acceptance
- [x] All nine source files are imported with version 0.1.0 and advisory tools.
- [x] Company identity, billing details, attribution, and private-archive assumptions
      become placeholders or optional user-provided context.
- [x] Resource paths resolve from the installed skill; companion skills are optional.
- [x] Bundled legal statements are marked unverified pending current primary-source
      checks; no claim of a legal refresh is introduced.
- [x] README documents installation and web verification; no keys or packages needed.
- [x] Required repository checks pass; the branch starts from origin/main.
- [x] NOT: legal-content refresh, global installation, or merging the PR.

## Verify
- `python3 scripts/validate_skills.py` → passes with the new skill.
- `python3 -m unittest discover -s tests -v` → all tests pass.
- `python3 scripts/check_unanchored.py --since origin/main` → passes.
- `git diff --check` → no whitespace errors.
- Compare the nine paths with the archive, resolve all eight resource-map targets,
  and inspect changes for metadata, identity removal, and source-verification scope.
- Scan the new skill for original company names, tax code, email, and addresses.

## Notes
- Source: `/Users/longpham/Downloads/vietnam-legal-advisor.skill`.
- User requested this addition on a separate branch and another PR.
- Completion rename remains subject to explicit user approval.
- Verified: validator (11 skills), all 191 tests, unanchored-instrument and whitespace
  checks, nine archive paths, eight resource targets, and original-identity scan.
- This import does not verify the bundled legal statements or their internal
  consistency; the prompt and every resource require primary-source checks at use.
