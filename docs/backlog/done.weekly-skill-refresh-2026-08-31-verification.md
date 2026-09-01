# Correct the 2026-08-31 weekly refresh before merge

**Deps**: weekly-skill-refresh-2026-08-24-verification, refresh-harness-verification

## Goal
PR #47 fails `Refresh / harness` (6 tests) and `Refresh / anchors` (1 dead). Correct it
on a branch off its own head, so the sourced material ships and the unsourced does not.

Five of the six failures are one behaviour: the refresh **rewrote** notes and status
fields rather than amending them, deleting caveats earlier passes had added — which the
workflow prompt forbids outright. Four are the same caveats the 24 August pass restored;
the tests it added are what caught the repeat. The sixth is the harness's own: the
Colosseum test asserts a literal date format rather than the claim it documents.

## Files
- `vietnam-crypto-radar/references/baseline.md` — restore Resolution 20's single-source status
- `vietnam-visa-check/{data/vietnam_immigration_policy.json,SKILL.md}` — reverted; the
  arrival-card rewrite was the only substantive change, so the bumps go back with it
- `web3-opportunities/data/web3_opportunities.json` — 3 caveats, 2 statuses, 1 url
- `tests/test_web3_opportunities.py` — assert the Colosseum window, not its formatting
- `evals/scripts/build_web3_cases.py` — derive a second query's count instead of typing it
- `evals/web3-opportunities/cases{,-v2}.jsonl` — regenerated, re-deriving ground truth
- `README.md`, `docs/backlog/PRIORITY.md` — record and track

## Acceptance
- [x] Nghị quyết 20/2026/NQ-HĐND is `REPORTED / SINGLE-SOURCE (LOCAL)` with no asserted
      effective date, while VnEconomy is still its only anchor
- [x] `DIGITAL_ARRIVAL_CARD` calls the Tan Son Nhat pilot optional and keeps the
      instruction not to state the multi-airport expansion as fact
- [x] `corelia-academy` and `unihackfest` both carry the 403-to-fetchers guardrail
- [x] `drips-network` keeps the 14 July 2026 legacy-contract exploit warning
- [x] `base-batches` points at a url that resolves
- [x] The Colosseum test passes on any formatting carrying both Sep 28 and Nov 2, and
      still fails if either is dropped, or if the two entries disagree
- [x] This week's sourced material is kept: the Decree 284 trigger, the circulars, the
      deadline updates, `base-batches-accelerator`
- [x] Neither `solana-foundation-fellowships` nor `tribe-accelerator` is `open` on the
      strength of a cohort already under way or deadlines already passed
- [x] The split's truth deltas are all explained by `base-batches-accelerator`, and no
      rubric pattern carries a count that was typed rather than derived
- [x] NOT: revert the whole refresh; NOT: relax a test to make a deletion pass

## Verify
- `python3 evals/scripts/build_web3_cases.py --check` → `"ok": true`. CI-only: the
  `Refresh /` statuses on #47 never ran it, so the staleness was invisible there
- `python3 -m unittest discover -s tests -v` and `python3 scripts/validate_skills.py`
- `SSL_CERT_FILE=/etc/ssl/cert.pem python3 scripts/check_anchors.py --targets baseline,web3` → 0 dead
- Colosseum test fails again if either date is removed from either entry
- `git diff --check` → no whitespace errors

## Notes
Scope grew three times past the original list, each time with approval and each time because a check
or a reviewer found what the previous pass had not. The stale-split check exposed two `status` flips the summary never mentioned:
`solana-foundation-fellowships` `closed` → `open`, `tribe-accelerator` `cohort-based` → `open`. Both
contradict their own new notes — the Solana cohort had already started, both of Tribe's deadlines had
passed. Deleting the "lists no program labelled 'Fellowships'" disavowal *and* flipping the status is
the pair that walks past `test_no_open_entry_disavows_its_own_existence`, which only inspects entries
already `open`. Both reverted, their new facts kept and stated as past.

Regenerating exposed builder drift: `v2-21` carried a hand-typed `\b13\b` beside a generated
`<TRUTH_COUNT>`, and nothing reads a generated rubric back, so it goes stale on the first refresh that
moves it. `fill` now resolves `<TRUTH_COUNT_n>` over every query; an unfilled token is a hard error. The regenerated truth's only deltas are `+1` wherever `base-batches-accelerator`
lands; before the status reverts they were `+2`, which is what the flips would have baked in. It also
moves the key under every stored web3 run — v2 `0.9583 / 1.0` → `0.9167 / 0.9583`, v1 `0.9167 / 1.0`
→ `0.8333 / 0.9167`, on `v2-21` and the two `<DATA_AS_OF>` checks. Nothing regressed; the roster moved
under fixed transcripts. Tabled in `logs.md`.

Fetching Decree 284 (CodeRabbit) found the enforcement sentence wrong in both directions — Article 15(4)
gives Article 9 to the SSC, police and provincial People's Committees, not the State Bank — and found no
support for the six-month grace period that was #47's headline crypto item. It is labelled UNVERIFIED,
not contradicted: Resolution 05's own text was not read.

`audit_refresh.py` still passes any refresh whose content changed — a rewritten note satisfies it as
a verified one does. Same hole as the 24 August spec, still open.

Completion approved by the user on 1 September 2026, after #46 merged (83b3290) and every acceptance item
was re-verified against the branch. Nothing here was found by the refresh's own summary: the tests caught
the deleted caveats, CI the stale split, CodeRabbit the enforcement claim, a primary source the grace
period. The one gap none of them covers deserves its own spec — a check that fails when a new instrument
number appears in `baseline.md` with no anchor beside it.
