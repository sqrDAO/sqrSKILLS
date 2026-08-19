# Backlog Priority

Ranked queue for open `todo.*` specs in this directory. The order records the
latest agreed priority; it is not the completion source of truth. A spec is
complete only when a user explicitly approves completion and the file is renamed
from `todo.<slug>.md` to `done.<slug>.md`.

## Open queue

- `refresh-harness-verification` — give the weekly refresh real pre-merge
  checks and make `last_verified` mean something.
- `weekly-skill-refresh-2026-08-17-verification` — correct the dead anchors,
  misdated Decision 21, restored arrival-rollout claim, and silently deleted
  caveats in PR #28. Shipped in #28; awaiting approval to mark done.

## Recently shipped

- `weekly-skill-refresh-2026-08-10` — reconciled PR #26 with current `main`,
  retaining its Web3 refresh without regressing the visa corrections in #27.
- `vietnam-visa-policy-verification-corrections` — corrected blanket health and
  arrival-declaration claims, the Timor-Leste signing date, and their source registry.
- `vietnam-visa-nationality-resolution` — resolved demonyms, qualified forms, and
  short aliases in `vietnam-visa-check`; fixed the silent wrong answer for `UK`,
  added the `NOT_REQUIRED` pathway for `VN`, and moved unrecognised input to an
  exit-0 structured error (#20).
- `vietnam-crypto-radar-regulatory-refresh` — refreshed the dated regulatory
  baseline with Decree 284 enforcement rules and the omitted accounting, tax, and
  electronic-invoice instruments (#16).
- `repository-harness` — added the portable skill validator, regression tests,
  required `Skill Harness` CI, YouAI-style spec processing, contributor docs, and
  audited/enforced protection for `main`.
