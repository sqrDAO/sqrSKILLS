# Backlog Priority

Ranked queue for open `todo.*` specs in this directory. The order records the
latest agreed priority; it is not the completion source of truth. A spec is
complete only when a user explicitly approves completion and the file is renamed
from `todo.<slug>.md` to `done.<slug>.md`.

## Open queue

1. `unanchored-instrument-check` — a new instrument number can appear in
   `baseline.md` citing nothing and no gate notices: `validate_skills.py` does not
   read prose, and `check_anchors.py` only tests URLs that exist. Two claims from
   the 31 August refresh went through that gap, one of them wrong about Article 9
   enforcement competence.

2. `superseded-refresh-pr-hazard` — because the repo squash-merges, a refresh PR
   corrected on a separate branch stays open and reverts those corrections if
   merged. #47 would have undone four fixes and written conflict markers into two
   data files. Structural, so it recurs weekly until the workflow changes.

3. `rubric-lexical-proximity` — `excused_by` discharges a whole check from a
   phrase anywhere in the answer. The negation half of this was fixed on #46;
   this half was deferred because sentence-scoping the excuse costs web3 v1
   iter1 its 1.0 and makes `v2-22` a stable failure. The unit is a section, and
   it differs per check.

## Recently shipped

- `weekly-skill-refresh-2026-08-31-verification` — held the weekly refresh to what
  it sourced. #47 deleted four caveats earlier passes had added, flipped two
  `status` values its summary never mentioned, pointed an entry at a dead url, left
  the eval answer key stale, and stated a wrong claim about Article 9 enforcement
  competence plus an unsupported six-month grace period. Corrected on top of the
  refresh so the week's real findings still shipped (#48).

- `web3-opportunities-eval-split` — the gated skill-evolution loop, end to end on
  a second skill. v1 baseline 22/24, one edit applied and gated to 24/24 with the
  gain honestly attributed to a single case; v1 retired on saturation and
  replaced by v2 (web-disabled, multi-turn, repeats). v2 baseline ran at two
  repeats: **23/24 and 24/24, call 1.0, no stable failure**. E2 withheld — the
  call score left nothing to gate it against. Standing tally across the whole
  spec: **eleven harness corrections against one skill edit**, which is the
  result worth remembering (#46).
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
