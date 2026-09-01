# Stop a corrected refresh PR from staying open and destructive

**Deps**: weekly-skill-refresh-2026-08-31-verification

## Goal
#47 was corrected on a separate branch and merged as #48. Because this repository
squash-merges, the automation commit `7087236` never became an ancestor of `main`,
so GitHub still showed #47 as open and mergeable-looking with a green-ish page.
Merging it at that point would have:

- silently reverted four corrections with no conflict — the visa arrival-card
  status, both `status` flips, and the Resolution 20 promotion; and
- written literal `<<<<<<<` / `>>>>>>>` markers into `web3_opportunities.json`
  and `baseline.md`, breaking JSON parsing.

It was closed on 1 September 2026 only because someone thought to compute the
merge first. Nothing in the repository or the workflow would have stopped it.

This is structural, not a one-off: **any** refresh PR corrected on a branch taken
off its head ends in the same state, every week, for as long as the repo squashes.

## Files
- `.github/workflows/weekly-skill-refresh.yml` (edited) — the fix, whichever is chosen
- `AGENTS.md` (edited) — record the hazard under Git Workflow
- `docs/backlog/PRIORITY.md` (edited) — track this spec

## Acceptance
- [x] A refresh PR whose content has landed by another route cannot sit open in a
      state where merging it reverts the corrections
- [x] The weekly schedule still runs unattended, and a refresh with nothing to
      correct still opens one reviewable PR as it does now
- [x] The PR remains the review gate: nothing merges automatically, which is the
      property the workflow comment says matters for legal/visa/crypto data
- [x] Whichever option is taken, `AGENTS.md` states plainly that a corrected
      refresh must not be merged from its original branch, and why
- [x] NOT: switching the repository to merge commits to dodge this — the squash
      convention is deliberate and #43–#48 all rely on it

## Verify
- Reproduce the hazard on a scratch branch: squash-merge a correction of a refresh
  commit, then `git merge-tree --write-tree origin/main <refresh branch>` and
  confirm the reverts and conflict markers appear
- Re-run after the fix and confirm the hazardous state is unreachable
- One full `workflow_dispatch` run that opens a PR normally

## Notes
Three options, in rough order of preference.

**Correct in place.** Push corrections to `automation/weekly-skill-refresh` itself
instead of branching off it, so one PR carries refresh and corrections and squashes
cleanly. Simplest, and it removes the second PR entirely — but it rewrites a branch
the workflow also force-pushes weekly, so the two writers need to not collide.

**Have the workflow close a superseded PR.** On each run, close any open PR on its
own branch before opening the new one. Cheap and unconditional, but it only helps
on the next Monday — a stale PR is live and dangerous for up to a week.

**A guard check.** A `Refresh /` status that fails when the PR's own changes are
already present on `main` in corrected form. Most precise, most work, and the
hardest to keep honest.

**Correct in place was chosen.** `AGENTS.md` now states the rule and why merging a
corrected refresh from a fork of its branch is destructive. The collision it opens —
workflow and human both writing that branch — is closed by a guard step that refuses
to run while a refresh PR is open, rather than by force-pushing over review work.
