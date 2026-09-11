# business-model-to-market 0.2.0 — audit

Read: SKILL.md, workbook builder, all seven references, example JSON, both XLSX
assets including values/formulas, and brainstorm DOCX text. Verdict: preserve
the useful planning workflow; fix data fidelity in the workbook.

## Confirmed findings

1. **P2 — Unanswered decision scores become invented numeric scores.**
   `scripts/build_gtm_workbook.py:151` substitutes zero for each missing score,
   then calculates weighted totals and ranks. Zero is outside the default 1–5
   scale and changes an incomplete answer into a scored loser. Missing weights
   are also zero at line 136. This contradicts the unknowns/TBD policy in
   `SKILL.md:38`. Probe: a named idea with no scores gets B6=0 and a RANK formula.
   Fix: leave unknown inputs blank, distinguish intentional numeric zero where
   a scale allows it, and suppress totals/ranks until required inputs are valid.

2. **P2 — Explicit false and numeric zero answers are erased.**
   `scripts/build_gtm_workbook.py:59` uses truthiness to decide whether an answer
   exists. `buyer.is_decision_maker=false` and `buyer.is_purse_holder=false` flow
   through `pair()` and become TBD instead of a negative answer. Probe: False
   becomes TBD. Fix: check only missing/None/empty-string values, preserving
   false and zero with an explicit display policy.

3. **P2 — Workbook-generation stdout is prose, not JSON.**
   `scripts/build_gtm_workbook.py:502` prints several free-text lines. All four
   generated modes reproduce this, contrary to the repository helper contract.
   Fix: return JSON containing output path, sheets, and section completeness;
   keep diagnostics on stderr. The --schema branch already returns JSON.

## Documented-content mismatches and proposals

- `SKILL.md:100` says the script preserves the template and writes only answer
  cells. It actually starts from `Workbook()` at script line 485 and generates
  layout, formulas, labels, and dimensions afresh. A five-factor template and
  one-factor input have different matrix layouts. Correct the claim rather
  than introducing template loading without a requirement (P3).
- `references/business-model-canvas.md:83` maps Offer to Stage 2, Personas to
  Stage 3, and Partnerships to Stage 8; SKILL.md assigns 3, 4, and 9. Update the
  mapping after the canvas insertion (P3).
- `SKILL.md:58` promises delivery/after-sales made operational by the sales-cycle
  reference, but that reference ends at Won/Lost and a delivery handoff. Clarify
  scope or add an actual post-sale planning section; proposed extension is UNGATED.
- `references/icp-personas.md:100` says only unbudgeted discretionary spend can
  close this quarter, but its example at line 122 says reallocation can. Remove
  the unsupported categorical restriction and keep timing as case-specific (P2).
- Methodology definitions are keyed by letter (`scripts/build_gtm_workbook.py:267`).
  MEDDPICC repeats D and C; document unique full-name keys or use an ordered
  list so naive duplicate JSON keys cannot discard criteria/champion definitions.
  This is a schema-usability proposal, not proof that full-name keys fail today.
- The past-tense target-results convention should clearly label planned targets
  separately from actual outcomes, especially when exporting a worksheet alone.
  No false achievement claim by an executing agent was observed.

## Common rubric

| Dimension | /5 | Evidence |
|---|---:|---|
| Anti-patterns | 4 | `SKILL.md:78` names concrete planning failure modes and checks |
| Actionability | 4 | `SKILL.md:97` provides the builder and exact schema discovery |
| Triggering | 3 | `SKILL.md:4` is specific but “partnership” can overlap legal structuring |
| Progressive disclosure | 4 | `SKILL.md:28` routes work to seven focused references |
| Gating readiness | 2 | `scripts/build_gtm_workbook.py:485` is artifact-testable; current split cannot grade workbooks |
| Structural correctness | 2 | `scripts/build_gtm_workbook.py:59`, `:151` discard meaning in inputs |

Verification: all four modes build and reopen with the expected sheet counts;
anchored weight formulas are present, and the original template's documented
Factor-1 bug is real. Cell/value probes confirm missing/false behavior. No formula
recalculation, visual layout check, or planning-quality agent evaluation was run.
