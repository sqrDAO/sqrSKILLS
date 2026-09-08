# Bound what the weekly refresh can spend, and see what it spends

**Deps**: —

## Goal
The refresh runs one Gemini session over all three skills. Across its whole
history — 15 runs, 242 agent-minutes, 2026-06-20 to 2026-09-07 — the two longest
runs were **41.9 min** (08-24, 09-07), together 35% of all agent time. Both
landed days after a jump in `vietnam-crypto-radar/references/baseline.md`, now
**8 KB → 58.8 KB since June** and still climbing ~50% a month. Run 34088320842
spent 41.9 minutes to produce a 66-insertion diff.

The prompt names ~178 KB of mandatory reading (≈44k tokens) across three
unrelated skills, all of it resident for the whole session — including the visa
leg, which loads a 43 KB JSON and on 09-07 changed nothing because its Tier-1
source was unreachable. Cost is turns × context, so one combined session pays the
full corpus on every turn of every skill.

Three problems, in order of how much they cost:

1. **No isolation.** One session, one context, three corpora.
2. **No ceiling.** No `maxSessionTurns`, no step timeout, no `timeout-minutes` on
   the job. The CLI runs `--yolo` and fetches arbitrary pages from the open web,
   so a prompt-injected loop runs until GitHub's 6-hour limit. This is a safety
   bound, not only a cost one.
3. **No observability.** The action computes exact token stats every run and
   discards them — `upload_artifacts` defaults false, so every run's artifact
   list is empty. Every figure above is inferred, not measured.

## Files
- `.github/workflows/weekly-skill-refresh.yml` (edited) — split, cap, upload
- `docs/backlog/PRIORITY.md` (edited) — track this spec

## Acceptance
- [ ] Each skill gets its **own** Gemini invocation, loading only its own corpus
- [ ] Still **one** PR per week, from one job on one working tree — three
      separately-scheduled jobs were rejected, see Notes
- [ ] One skill's agent failing does not discard the other two skills' work; the
      summary says which legs ran and which failed
- [ ] Each invocation sets `maxSessionTurns`, and the job sets `timeout-minutes`
- [ ] `upload_artifacts: true`, so `stdout.log` with real `stats.*.tokens` is
      retrievable per run
- [ ] `gemini_cli_version` pinned to an exact version, and the action pinned to a
      SHA rather than the floating `@v0`
- [ ] `vietnam-crypto-radar` keeps `gemini-2.5-pro`; the two mechanical legs may
      use a cheaper model
- [ ] Every existing gate still runs on the combined tree and still reports into
      the PR body: audit, harness, anchors, the status publish, the final refusal
- [ ] NOT: touching skill data, prompts' verification discipline, or the tier
      rules. This spec changes what the refresh *costs*, never what it *believes*
- [ ] NOT: three crons and three PRs a week

## Verify
- `python3 scripts/validate_skills.py` → `"ok": true`
- `python3 -m unittest discover -s tests` → passes
- Actions → Weekly Skill Refresh → Run workflow → one PR, a summary naming all
  three legs, an artifact per leg carrying `stats.*.tokens`, and total agent
  minutes to compare against the 41.9 min baseline of run 34088320842

## Notes
**Three steps in one job, not three jobs.** Separate jobs get separate runners and
separate working trees, so the three sets of edits would have to be passed as
artifacts and reassembled before the PR step — real complexity for no saving,
since the win comes from the *session* boundary, not the *job* boundary. Separate
crons would also mean three PRs a week and three review surfaces. One job, three
invocations, one tree, one PR.

The saving is structural: the per-turn context floor drops from ~44k tokens to
roughly 14k / 9k / 12k, and cost is turns × context.

`baseline.md` is the term that grows without bound and this spec does not fix it
— splitting the session only stops the *other two* skills paying for it. Halving
the file itself is the follow-up, to be specced once real token stats exist.

`maxSessionTurns` is a CLI settings key a schema change could drop silently;
`timeout-minutes` is enforced by Actions and cannot be lost. Both are set.

The estimates above are wall-clock and corpus arithmetic, not accounting — which
is why `upload_artifacts` is in scope. After one run this spec's own premises
become measurable, and may need revising.
