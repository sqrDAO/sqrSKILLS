# llm-wiki deterministic ordering, and the lookup invariant

## Goal

Two findings from assessing which skill can carry the third validation split.

`llm-wiki` is the only remaining candidate: four offline stdlib scripts over a
`$WIKI_DIR`, no network and no credentials. It is not eligible yet, and one of
the reasons is a live bug. `search.py` and `list.py` sort on score or date alone
and then fall back to whatever order `os.listdir` returned, which is filesystem
hash order. On a four-way tie, `search.py --top 2` returns two arbitrary pages:

```text
as enumerated by APFS   ['pages/banana.md', 'pages/apple.md']
enumeration reversed    ['pages/zebra.md',  'pages/mango.md']
```

Disjoint. Nothing in the code decides that. Two users with the same wiki get
different answers, and a generated answer key would encode the machine that
built it — the `--check` staleness gate would pass on macOS and fail on CI.
`lint.py` and `log.py` are already order-independent.

Second finding: three skills have each independently grown a clause telling the
agent to run the lookup script instead of answering from the skill text
(`vietnam-visa-check` 0.4.0, `web3-opportunities` 0.2.12, `llm-wiki` 0.1.3). The
`web3-opportunities` split rediscovered it as pattern p009 at the cost of a
24-agent run. Three instances is enough; record it as an invariant new skills
inherit rather than one each skill pays to learn.

## Files

- `llm-wiki/scripts/search.py` — tiebreak on filename after score.
- `llm-wiki/scripts/list.py` — tiebreak on filename after title and after date.
- `llm-wiki/SKILL.md` — version 0.1.3 -> 0.1.4.
- `tests/test_llm_wiki.py` — the invariant, not a snapshot: run each script
  twice with `os.listdir` returning opposite orders and require equal output.
- `AGENTS.md` — the lookup invariant, in `Adding a New Skill`.
- `evals/README.md` — correct the eligibility note for `llm-wiki`; a fixture
  wiki was never the only blocker.

## Acceptance

- [x] `search.py` and `list.py` return identical output under forward and
      reversed enumeration, for ties on score, on title, and on `last-updated`.
- [x] Ordering is total: no two distinct pages compare equal under any sort.
- [x] `lint.py` covered by the same test, to keep it order-independent.
- [x] No behaviour change when there are no ties — the existing sort keys stay
      primary and only the tiebreak is new.
- [x] `AGENTS.md` states the lookup invariant with its three instances.
- [x] `evals/README.md` records all three llm-wiki blockers: the fixture wiki,
      this ordering bug, and the harness's inability to grade file writes.
- [x] `SKILL.md` behaviour is unchanged. The weaker wording of llm-wiki's own
      lookup clause is a hypothesis with no trace behind it and is not edited
      here.

## Verify

```bash
python3 scripts/validate_skills.py
python3 -m unittest discover -s tests -v
python3 evals/scripts/build_web3_cases.py --check
python3 evals/scripts/build_visa_cases.py --check
```

## Notes

This is a script defect, so per `AGENTS.md` it goes to `tests/` and a spec, not
into a split — the split validates instructions, not code.

Fixing it does not make `llm-wiki` eligible. Two blockers remain: no committed
fixture wiki with copy-on-run (`log.py` appends and stamps `date.today()`, so
cases would contaminate each other), and no way to grade the write side of the
skill — ingest, contradiction notes, filing answers back — which the current
graders cannot see because they read recorded calls and the final answer only.
