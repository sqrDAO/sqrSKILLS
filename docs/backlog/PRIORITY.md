# Backlog Priority

Ranked queue for open `todo.*` specs in this directory. The order records the
latest agreed priority; it is not the completion source of truth. A spec is
complete only when a user explicitly approves completion and the file is renamed
from `todo.<slug>.md` to `done.<slug>.md`.

## Open queue

_Empty._

## Recently shipped

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
