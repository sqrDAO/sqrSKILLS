# p013 — The documented output schema lags the script

**Status**: confirmed (documentation defect) · **no observed failure** ·
supersedes the surviving half of [[p007-exemption-conditions-dropped]] and
[[p009-dataset-facts-with-no-route]]

## What is true
SKILL.md's **Output** section shows an example JSON object. The script returns
more than the example shows:

| Query | Fields returned | Not in SKILL.md |
|---|---|---|
| `--nationality Polish --duration_days 7` | 24 | `visa_free.source_refs`, `evisa_option.entry_modes_allowed`, `.approved_ports_count`, `.entry_port_restriction`, `.eligible_nationalities` |
| `--nationality US --phu_quoc_only` | 22 | the four above, plus `phu_quoc.restriction`, `.entry_modes_allowed`, `.passport_validity_required_days` |

`entry_port_restriction` is a full prose answer to a common question — land entry,
port nomination, and the caveat to verify the live list. It is the single most
useful string the script emits and it appears nowhere in the documentation.

## What is *not* true
That this causes failures. It does not, on the evidence:

- `vvc-23` answered the land-entry question correctly **from these undocumented
  fields**, having read only SKILL.md.
- `vvc-12`/`vvc-13`/`vvc-14` used `visa_free.conditions` correctly.
- `vvc-20` used the Phu Quoc restriction fields correctly.

The agent reads the JSON it actually receives, not the schema it was promised.
Two separate predictions (p007, p009) assumed the opposite and both were wrong.

## Why record it at all
Three reasons, none of them "fix it now":

1. It is the standing explanation for why p007 and p009 were mispredicted. Without
   this page, the next person reading the skill makes the same inference.
2. Documentation drift is a leading indicator. The Output section was accurate
   once; fields were added to the script without it. The next addition may be one
   the agent does not handle gracefully.
3. It bounds a real claim: an agent on a smaller model, or one that skims rather
   than reads the raw JSON, is likelier to depend on the documented schema. This
   baseline is Sonnet-specific (see `../skill-impact.md`). The gap is latent, not
   absent.

## Not proposed as a skill edit
Editing SKILL.md to document eight more fields costs context on every invocation
and, by this evidence, buys nothing measurable. Revisit if a cheaper model is
added to the roster and these cases regress — that is the experiment that would
settle it.

## Anti-pattern (for the maintainer, not the agent)
Adding a field to a skill's script without updating the documented output shape.
The `--check` mode of `build_visa_cases.py` regenerates ground truth after a data
refresh; nothing yet guards the schema.
