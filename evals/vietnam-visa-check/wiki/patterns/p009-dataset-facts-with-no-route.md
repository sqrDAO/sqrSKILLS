# p009 — Dataset facts with no documented route

**Status**: hypothesis · no trace yet

## Predicted symptom
"Can I cross in by land from Cambodia with an e-Visa?" The bundled dataset answers
this. The agent has no documented way to reach the answer, so it either declines
or falls back to training knowledge — which the skill's own Critical Rules call
"frequently wrong and outdated".

## Root cause
`query_visa.py` surfaces a subset of the policy file: exemptions, the e-Visa
block, Phu Quoc, and generated notes. SKILL.md documents the script as the whole
interface. Everything else in the 42 KB dataset is unreachable by the documented
path:

- `frequently_asked_questions_for_agents` — land entry, single-port entry,
  minimum wait between re-entries, Web3 founder pathways
- `evisa_entry_ports` — airports, land crossings by neighbour, sea ports
- `special_passport_exemptions` — ABTC, diplomatic/service, visa-exemption certificates
- `long_term_visa_categories` — DT/LV/GD, and the 2026 reforms

The `--phu_quoc_only` flag is the one place a non-exemption question got its own
entry point, which shows the shape of the fix.

## Predicted root-cause-level fix
Two options, and the loop should decide between them on evidence, not taste:
1. **Document the read** — tell the agent it may read named keys out of
   `data/vietnam_immigration_policy.json` for questions the script does not cover.
   Cheap; widens `allowed-tools` beyond `Bash(python3 *)`.
2. **Widen the script** — add a `--topic` lookup over the FAQ and port tables.
   Keeps one interface and one source of truth; costs a script change, which is
   outside what this loop is supposed to be evolving.

Option 1 is the skill edit. Option 2 is a backlog spec.

## Anti-pattern to record if confirmed
A skill that declares a data file as its source of truth while documenting an
interface that reaches only part of it. The undocumented remainder is where the
agent silently reverts to training knowledge.

## Validation cases
`vvc-23` (land entry), `vvc-17` (VOA exclusion — reachable today only because
`main()` special-cases `CN`, which is evidence for how narrow the current route is).

---

## Iteration 0 result — **falsified as stated; the real gap is narrower**

`vvc-23` (land entry from Cambodia on an e-Visa) **passed.** The agent answered
correctly, cited the ~83 approved ports, and added the verify-before-travel
caveat.

The prediction assumed the answer was unreachable without reading the dataset.
It was not. `build_evisa_option()` already lifts four fields the prediction
assumed were stranded — `entry_modes_allowed`, `approved_ports_count`,
`entry_port_restriction`, `eligible_nationalities` — and `entry_port_restriction`
contains the full answer including the caveat, verbatim.

**Zero of 24 traces read any file inside the skill directory other than SKILL.md.**
The agents never needed to. Option 1 ("document the read") would have widened
`allowed-tools` to solve a problem that does not exist.

What survives is the observation underneath, restated correctly: the script
returns fields SKILL.md's Output section does not list. See
[[p013-documented-output-schema-lags-the-script]].
