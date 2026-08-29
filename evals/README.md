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
    build_visa_cases.py    regenerate the split; ground truth comes from the skill's own script
    grade_visa.py          score a run file
  vietnam-visa-check/
    cases.jsonl            24 cases (generated — edit build_visa_cases.py, not this)
    runs/                  one JSONL per iteration per repeat
    wiki/
      index.md             one line per pattern: problem, root cause, fix
      patterns/            10-30 lines each
      logs.md              chronological, append only
      skill-impact.md      every proposed edit, its diff, its score, accepted or rejected
```

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
```

Run file format, one object per case:

```json
{"case_id": "vvc-06",
 "tool_calls": [{"nationality": "Filipino", "duration_days": 30, "phu_quoc_only": false}],
 "answer": "<the agent's final user-facing reply>"}
```

## What the score means

`pass_rate` is strict: a case passes only when the tool call is right **and**
every rubric check passes. Two sub-scores are reported separately because they
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

`cases.jsonl` is generated. Prompts, probes and rubrics are authored in
`build_visa_cases.py`; the `truth` block of every case is produced by running the
skill's own `query_visa.py`. After a policy refresh, regenerate — the answer key
re-derives from the data instead of rotting against it.

This means the split validates the **skill instructions**, not the script. The
script already has 299 lines of regression tests in `tests/`. Nothing here
duplicates them.
