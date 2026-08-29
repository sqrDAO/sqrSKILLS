# evals — validation splits and skill wikis

A skill improves because a change was measured, not because it read better. This
directory holds the measurement.

Adapted from *WikiSkill* (2026). The load-bearing result there is the ablation:
removing the persistent wiki from the component that edits skills dropped average
performance from 63.7% to 48.7%. Skill quality tracks how much accumulated
diagnostic knowledge the editor can see — not how carefully the skill was written.

## Layout

```
evals/
  scripts/
    rubric.py              shared: negation-aware checks, run integrity, the summary shape
    build_visa_cases.py    regenerate a split; ground truth comes from the skill's own script
    grade_visa.py          score a run file
    build_web3_cases.py
    grade_web3.py
  <skill-name>/
    cases.jsonl            24 cases (generated — edit the builder, not this)
    runs/                  one JSONL per iteration per repeat
    wiki/
      index.md             one line per pattern: problem, root cause, fix
      patterns/            10-30 lines each
      logs.md              chronological, append only
      skill-impact.md      every proposed edit, its diff, its score, accepted or rejected
```

Two splits exist: `vietnam-visa-check` (saturated at 24/24 — see its
`skill-impact.md`) and `web3-opportunities` (built, not yet run).

## Which skills can have a split

Ground truth is *generated*, never typed. That requires a skill whose answers
come from a deterministic, offline script over bundled data — run the script,
store what it returned, and a data refresh re-derives the answer key instead of
rotting against it.

Of the ten skills in this repo, three qualify: `vietnam-visa-check` and
`web3-opportunities` (both have one), and `llm-wiki`, whose scripts are
deterministic over a `$WIKI_DIR` and would need a committed fixture wiki first.
Five call live APIs and hold credentials (`luma-calendar`,
`nearby-places-search`, and the three Telegram skills) — no reproducible answer
key without a recorded-fixture layer that does not exist. `vietnam-crypto-radar`
ships references but no script, so its truth would have to be hand-written and
would go stale at the next refresh. `business-model-to-market` is a judgement
workflow whose output is a workbook, not an answer.

Do not build a split for a skill in the second group by hand-writing the answer
key. A split that rots is worse than none: it fails on refresh, gets "fixed" by
editing the expectations, and after two rounds of that it is measuring nothing.

## Two rules that make it work

**The wiki is never read at runtime.** It lives here, outside the skill directory,
and the executing agent never sees it. An agent that reads the pattern pages will
produce the right answer *from the wiki* and the trace stops being evidence about
the skill. In the paper, giving the executing agent wiki access cost 2.8 points.
The wiki informs the editor; the skill informs the executor.

**Skills roll back, the wiki does not.** A rejected edit is reverted from
`SKILL.md` and recorded permanently in `skill-impact.md`, with its diff and the
reason. That record is what stops the same idea being re-proposed later.

## The loop

1. **Execute** — run the split. Each case is one fresh agent that sees the skill
   directory and nothing else. Record the tool calls and the final answer.
2. **Diagnose** — root-cause the traces, update `wiki/patterns/`. Sample
   successes too, not only failures: passing traces show which instructions are
   carrying weight. Feeding the editor failures only produces skills that overfit
   to error modes — it degraded one model by 4 points in the paper.
3. **Propose** — one atomic edit to `SKILL.md`, patch-shaped, derived from the
   wiki.
4. **Gate** — rerun the split. Keep the edit only if the pass rate improves;
   otherwise revert. Either way, log it.

Do not stop at iteration 2. Only 39–52% of accepted updates landed in the first
two iterations; roughly half the value arrived in iterations 3–7.

## Running it

```bash
python3 evals/scripts/build_visa_cases.py           # regenerate after a data refresh
python3 evals/scripts/build_visa_cases.py --check   # CI: fail if stale
python3 evals/scripts/grade_visa.py evals/vietnam-visa-check/runs/iter0-a.jsonl

python3 evals/scripts/build_web3_cases.py
python3 evals/scripts/grade_web3.py evals/web3-opportunities/runs/iter0.jsonl
```

Both `--check` runs are a required CI step. A split that has drifted from the
data it was generated from is not a gate.

Every script takes its paths as inputs and falls back to this repo's layout:
`--query-script`, `--out` on the builders; `--cases`, `--query-script` (and
`--policy` for visa) on the graders. Point `--cases` at a subset file to score a
targeted probe.

## Calibrate a new split before running it

An agent run is the expensive part. Before spending one, write two fixture runs
by hand and grade them:

1. An **ideal** answer for every case. This proves only that the rubric is
   satisfiable — you wrote both sides. Its value is the other direction: any
   check that fails a good answer is a broken check. On the `web3-opportunities`
   split one did, and it was a `forbid_all` written as a phrase whose match
   window jumped a paragraph break to reach the sentence that was being correct.
2. A **deliberately wrong** answer for every case, each committing the specific
   failure that case exists to catch. Every one must fail, and must fail on
   *its own* check rather than on something incidental. A case that cannot fail
   reports a success nobody observed.

Keep the numbers and any correction they forced in the wiki. The fixtures
themselves are scratch.

**The run file must contain every case exactly once.** A missing, duplicated, or
unknown `case_id` is refused with `"ok": false` and no score. Otherwise a run that
quietly dropped its failures would report a higher pass rate than it earned.

Run file format, one object per case. `tool_calls` records what the agent
actually invoked, in whatever shape that split's grader reads:

```json
{"case_id": "vvc-06",
 "tool_calls": [{"nationality": "Filipino", "duration_days": 30, "phu_quoc_only": false}],
 "answer": "<the agent's final user-facing reply>"}

{"case_id": "w3o-03",
 "tool_calls": [{"argv": ["--dilution", "non-dilutive", "--chain", "solana"]}],
 "answer": "<the agent's final user-facing reply>"}
```

The `web3-opportunities` split records the raw argv and normalises it by running
the skill's own script and reading the `query` block it echoes back, so the
grader and the executor cannot disagree about what a flag meant.

## What the score means

`pass_rate` is strict: a case passes only when **every** required tool call is
right **and** every rubric check passes. A case may require more than one
invocation — `vvc-24` needs both nationalities looked up, and one of them is not
enough. Where a visa prompt states no duration, the call must either omit
`--duration_days` or pass the script's own default; any other value changes the
pathway and is graded as a wrong call. On the roster split an expected call is a
*facet constraint*: it pins only the facets that matter and leaves the rest free,
but a facet it does pin must match as a set — `--dilution non-dilutive` is a
different question from `--dilution non-dilutive,mixed`, and the skill documents
that difference as a trap. Two sub-scores are reported separately because they
call for different edits — `call_score` (did the agent invoke the script
correctly) and `answer_score` (did the reply carry what the result made
available).

At n=24, one case is 4.2 points. Three repeats per iteration; a one-case
difference is noise, not a result.

The rubric is keyword and regex based. That is a real limit: it can be satisfied
by an answer that names the right things badly, and it will fail a good answer
that phrases something unusually. It is calibrated to catch the failure modes in
`wiki/patterns/`, not to judge writing quality. When a check fires on a good
answer, fix the check and say so in `skill-impact.md` — a rubric edited to make a
skill edit look better is how a gate stops meaning anything.

## Ground truth

`cases.jsonl` is generated. Prompts, probes and rubrics are authored in the
builder; the `truth` block of every case is produced by running the skill's own
query script. After a data refresh, regenerate — the answer key re-derives from
the data instead of rotting against it.

Rubric patterns can be generated too, and the ones that would otherwise rot are.
`build_web3_cases.py` substitutes `<DATA_AS_OF>` and `<TRUTH_COUNT>` from the
script's own output, so a check that requires the roster's date or a result count
survives the next refresh instead of failing it.

This means a split validates the **skill instructions**, not the script. The
scripts have their own regression tests in `tests/`; nothing here duplicates
them. `tests/test_evals_harness.py` covers the grading machinery itself, which is
the part that has historically been wrong most often.
