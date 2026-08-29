# Backlog Priority

Ranked queue for open `todo.*` specs in this directory. The order records the
latest agreed priority; it is not the completion source of truth. A spec is
complete only when a user explicitly approves completion and the file is renamed
from `todo.<slug>.md` to `done.<slug>.md`.

## Open queue

1. `web3-opportunities-eval-split` — v1 is retired at 24/24 and v2 is built and
   calibrated. What remains is v2 at two repeats to establish a baseline, then
   re-testing the withheld E2 against it. That is one fresh agent per case per
   repeat, so it is a deliberate spend.

## Recently shipped

- `llm-wiki-ordering-and-lookup-invariant` — a sort with ties was really a sort
  by filesystem: `search.py --top 2` returned a disjoint pair of pages depending
  only on `os.listdir` order, so two users with identical wikis got different
  answers. Every sort now ends on a filename tiebreak, pinned by tests that run
  each script under opposite enumeration orders — six of which fail against the
  previous scripts. Also recorded the lookup invariant that `vietnam-visa-check`,
  `web3-opportunities` and `llm-wiki` each found separately, and which the web3
  split paid a 24-agent run to rediscover (#45).
- `visa-country-name-resolution` — indexed `_COUNTRY_NAMES` so a country's own
  name resolves wherever its demonym does: 26 of 81 display names went from
  unresolvable to resolvable, and 17 self-echoing suggestions ("Argentina not
  recognised — did you mean Argentina?") to none. Found by the eval split's
  first run, inside a trace that passed (#38).
- `refresh-direction-and-da-nang-coverage` — only a raised `last_verified` has
  to earn its keep; a lowered one is always kept, since it claims less. The
  weekly prompt now sweeps Da Nang's controlled trials, states the count is a
  floor, and refuses to promote the single-source resolution alone (#36).

- `vietnam-crypto-radar-da-nang-trials` — recorded Da Nang's municipal
  controlled-trial regime: the enabling resolution, the four 22 August 2026
  approvals, the two earlier trials still running, and the applications filed
  but not decided. Supersedes #32 (#35).
- `weekly-skill-refresh-2026-08-24-verification` — corrected the 13 data
  defects merged in #31: `status` values contradicting their own notes,
  deleted deadlines and warnings, and dates bumped onto unchecked claims.
  Added the roster's first regression tests, including cross-field
  invariants that catch the class rather than the instance (#33).
- `refresh-harness-verification` — gave the weekly refresh real pre-merge
  checks, an anchor resolution check, and a `last_verified` audit that rolls
  back dates the refresh did not earn (#29).
- `weekly-skill-refresh-2026-08-17-verification` — corrected the dead anchors,
  misdated Decision 21, restored arrival-rollout claim, and silently deleted
  caveats in the 2026-08-17 automated refresh (#28).
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
