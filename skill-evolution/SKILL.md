---
name: skill-evolution
version: 0.1.0
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash(python3 *)
description: "Audit, build, improve, or gate an agent skill using the three-layer method (raw traces, persistent wiki, executable skill) from WikiSkill, arXiv 2608.27454. Use whenever a skill is the object of work, even without the word audit: write a new skill, improve or fix an existing one, review a skill library, work out why a skill is not firing, add anti-patterns, cut an oversized SKILL.md, build or repair a validation set for a skill, decide whether a skill edit should ship, or set up the wiki and gating layers. Also use when a skill produced a bad output and the question is what to change so it stops. NOT for using a skill to do its own job (scoring a company, drafting a contract, writing Vietnamese), and not for MCP servers or plugins."
---

# Skill evolution

This workflow adapts [WikiSkill](https://arxiv.org/html/2608.27454v1): retain accumulated diagnosis and measure candidate instructions against a validation set. Its reported results describe its experimental setup, not a guarantee for every skill. Numeric workflow budgets below are starting heuristics, not universal requirements.

This package contains only this prompt. An external `skill-evolution-kit` may provide `wiki_init.py`, `gate.py`, `run_with_skill.sh`, `install.sh`, templates, patterns, eval sets, and patches; none are bundled here. If a kit is available, inspect its actual files and interface before using it. Otherwise use the project's existing harness, or deliver an audit and gate design labelled UNGATED; do not invent commands or claim a run. Building a harness is a separate task.

Map Read/Write/Edit to local file tools and Bash to shell execution; tool metadata grants no additional permissions. Follow project rules for specs, validation, and completion. An import or inspection does not authorize an evaluation campaign or library-wide edits. Run only relevant helpers whose effects fit the task; use isolated fixtures for mutating scripts.

## Research motivation

- **Wiki ablation (Gemini-3.5-Flash, four benchmarks; paper §5.1).** Same loop, wiki visible to the skill editor: 63.7%. Wiki removed: 48.7%.
- **The executing agent must not see the wiki.** Giving it access dropped 63.7 to 60.9 in that ablation. The authors hypothesize that solving from the wiki makes traces less informative about missing skill knowledge.

## Layers

```
<skill>/
  SKILL.md          agent-facing; keep concise, no fixed line quota
  references/       agent-facing, read on demand
<author-workspace>/<skill-name>/
  wiki/             author-facing, NEVER shipped
    index.md        one line per pattern: problem + root cause + fix
    patterns/*.md   10 to 30 lines each
    logs.md         chronological, append only
    skill-impact.md every proposal, its diff, its verdict
  raw/traces/       immutable, write once
```

Keep the author workspace outside the installed skill directory. The executor must not receive wiki pages, prior diagnosis, or expected answers through files or inherited conversation context.

Skills roll back on a failed validation. **The wiki never rolls back.** Snapshot the candidate files before editing; revert only the candidate patch, preserving unrelated user changes and author records.

## Auditing a skill

Read every file, not just SKILL.md: references, assets, scripts, agents. Syntax-check scripts and exercise relevant runnable ones with safe fixtures; report skipped checks. Score 0 to 5 per dimension, citing file:line:

1. **Anti-patterns.** Does each rule name the concrete wrong action sequence and the exact fix, or only state correct procedure? Procedure-only is the default failure.
2. **Actionability.** Concrete values, commands, clause text, hex codes, article numbers. In the paper, `goal-directed-action` was rejected for being abstract and `never return an item to its origin location` was accepted.
3. **Triggering.** The frontmatter description, for false negatives, false positives, and collision with every other skill. Boundaries must be written from **both** sides; a one-way cross-reference is invisible from the other skill and routes wrongly.
4. **Progressive disclosure.** Keep the entrypoint concise for its task; line count alone is not a defect. Every pointer resolves; every reference, asset and script is reachable.
5. **Gating readiness.** What ground truth exists.
6. **Structural defects.** Contradictions between SKILL.md and its references, stale dates, duplicated content, script bugs, dead links.

Hunt for **statements a skill makes about its own contents that are false**. Worse than gaps, because an agent acts on them: a claim about what a script does, a file described as existing that does not, a documented color that differs from the shipped asset. Verify each against the actual file.

For a library, use one rubric and write each full audit to a file. When parallel agents are available and authorized, assign bounded groups of skills; otherwise audit sequentially. An audit identifies proposed changes; it does not expand the authorized edit scope.

## Writing an anti-pattern

```
**AP-n. <short name>.** Wrong: <the exact sequence the agent produces, verbatim>.
Fix: <the exact corrective sequence, verbatim>.
```

Wrong and Correct must be real artifacts: actual commands, actual sentences in the target language, actual formulas, actual cell references. Cut prose before cutting these two.

## Building the gate

One eval file per skill. Every case names the anti-pattern it `guards`. Prefer numeric, count, ordering and regex assertions; assert on behavior, not phrasing.

- **No case may be absence-only.** It passes on an empty transcript and inflates every score it appears in.
- At least a third of cases assert something is absent: leakage, drift, a banned phrase.
- Mark `needs_key: true` honestly. Never fake ground truth to make a case runnable.
- 10 to 40 cases. Add one when a real failure gets through, never to pad.

## Gate the eval set before you gate the skill

An eval set written from an audit looks right and mostly does not measure. Run it once against the unchanged skill and triage every case before trusting a single number. The supplied source reports a local run across four skills in which only about 17 of 140 lost weighted points were genuine defects; raw evidence is not bundled, so treat these figures as UNVERIFIED experience, not paper results.

Triage every case, passing ones included, as GENUINE, MIS-SPECIFIED, ENVIRONMENT, or WEAK (passed but so loose a bad answer would also pass). Judge each assertion on its own merits before looking at whether it passed. Never reclassify a case because reclassifying it would raise the score, and never weaken a GENUINE case: those are the only real signal in the set. Record eval repairs as their own iteration, separate from any skill change, so the two are never confounded.

Five harness faults reported in the supplied source; verify any claimed kit fixes against the version actually available:

- Regex must default to **case-sensitive**. Defaulting to ignorecase made a denylist for `Empower` fire on the correct `EMpower`.
- Score the **emitted artifact**, not just the chat message, for any skill whose deliverable is a file. Ten design cases asserted on CSS the transcript could never contain.
- **Exclude confirmed environment-blocked cases from the performance denominator and report every exclusion.** Missing or never-run cases make a run incomplete; do not silently drop them. Distinguish sandbox refusals from a skill-induced refusal.
- **Compare over the intersection** of cases scoreable in both runs. Raw scores over different denominators are not comparable, and a verdict can otherwise turn on which tool call the sandbox refused.
- An eval cannot be written in a form the skill forbids. A Vietnamese eval written in ASCII could not match a skill that mandates diacritics; repairing that alone moved the score from 0.182 to 0.759.

Run cases with the skill injected in full (using an inspected runner, such as an available `run_with_skill.sh`), which is the paper's setup: it removes retrieval and triggering as confounds, so the score measures content only. Triggering is then unmeasured, and remains a separate real problem.

## Cadence

- One atomic, patch-shaped change per iteration, never a rewrite. Rollback only means something if the change is small.
- Read `skill-impact.md` before proposing, so a rejected change is not re-proposed.
- For a requested evolution campaign, budget six to eight iterations as a starting point; stop at the agreed budget, saturation, or when no valid comparison remains. The paper reports substantial gains after iteration two.
- Sample successes as well as failures, roughly 5 failing to 3 passing.
- Treat small deltas cautiously and use paired repeats to assess instability. Under 10 paired cases is exploratory evidence here, not a reliable gate; a fixed point threshold is not a statistical significance test.

## Traps

- **Some proposal tools overwrite the frontmatter description with the proposal card's one-line description.** Inspect the actual diff. Put the full routing description, under 1000 characters, in that field. A summary of the change there leaves the skill nearly untriggerable.
- Some proposal tools carry only SKILL.md; inspect what yours includes. Fixes in scripts, references, assets or CSS have to ship as files.
- Model-specific workarounds can transfer poorly (paper §4.2.2): one model's spreadsheet skill dropped another from 50.5 to 18.1. Keep general procedure and workaround in separate, labeled sections.
- The wiki has no pruning mechanism. Plan a consolidation pass.
- Strict gating discards neutral changes that would have enabled a later gain. Relax it deliberately, never by default.

## Verification before handoff

When implementing a gate, prove both directions against a sandboxed copy: an improvement is ACCEPTED, a deliberate regression is REJECTED and rolled back, and the wiki survives the rollback. For gate work, confirm every case scores zero on empty transcripts or rejects them as invalid. Re-check the audit's headline claims against the actual files, independently of how they were found. Report ungated changes as ungated; a factual correction verified by inspection is worth shipping, but say which kind each change is.
