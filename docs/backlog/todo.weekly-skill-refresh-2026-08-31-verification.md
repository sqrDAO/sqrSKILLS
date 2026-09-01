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
- [ ] Nghị quyết 20/2026/NQ-HĐND is `REPORTED / SINGLE-SOURCE (LOCAL)` with no asserted
      effective date, while VnEconomy is still its only anchor
- [ ] `DIGITAL_ARRIVAL_CARD` calls the Tan Son Nhat pilot optional and keeps the
      instruction not to state the multi-airport expansion as fact
- [ ] `corelia-academy` and `unihackfest` both carry the 403-to-fetchers guardrail
- [ ] `drips-network` keeps the 14 July 2026 legacy-contract exploit warning
- [ ] `base-batches` points at a url that resolves
- [ ] The Colosseum test passes on any formatting carrying both Sep 28 and Nov 2, and
      still fails if either is dropped, or if the two entries disagree
- [ ] This week's sourced material is kept: the Decree 284 trigger, the circulars, the
      deadline updates, `base-batches-accelerator`
- [ ] Neither `solana-foundation-fellowships` nor `tribe-accelerator` is `open` on the
      strength of a cohort already under way or deadlines already passed
- [ ] The split's truth deltas are all explained by `base-batches-accelerator`, and no
      rubric pattern carries a count that was typed rather than derived
- [ ] NOT: revert the whole refresh; NOT: relax a test to make a deletion pass

## Verify
- `python3 evals/scripts/build_web3_cases.py --check` → `"ok": true`. CI-only: the
  `Refresh /` statuses on #47 never ran it, so the staleness was invisible there
- `python3 -m unittest discover -s tests -v` and `python3 scripts/validate_skills.py`
- `SSL_CERT_FILE=/etc/ssl/cert.pem python3 scripts/check_anchors.py --targets baseline,web3` → 0 dead
- Colosseum test fails again if either date is removed from either entry
- `git diff --check` → no whitespace errors

## Notes
Two anchor-hygiene findings NOT fixed here; neither breaks a check. The new Decree 284
bullets (six-month trigger, Circulars 89 and 90/2026/TT-BTC, 39/2026/TT-NHNN) add no
anchors, so three instrument numbers rest on nothing citable. The VON / G-Flow / GM
Services / Dinogo update names fidinam.com and vietnamplus.vn inline without adding
either, though that claim is hedged and overstates nothing.

Scope grew twice past the original list, both times with approval. The stale-split check
exposed two `status` flips the summary never mentioned: `solana-foundation-fellowships`
`closed` → `open`, `tribe-accelerator` `cohort-based` → `open`. Both contradict their own
new notes — the Solana cohort had already started, both of Tribe's deadlines had passed.
The Solana one is sharper: deleting the "lists no program labelled 'Fellowships'"
disavowal *and* flipping the status is the pair that walks past
`test_no_open_entry_disavows_its_own_existence`, which only inspects entries already
`open`. Both reverted, their new facts kept and stated as past.

Regenerating then exposed builder drift: `v2-21`'s rubric carried a hand-typed `\b13\b` for the
dilutive+mixed total beside a generated `<TRUTH_COUNT>`. Nothing reads a generated rubric back,
so a typed number goes stale on the first refresh that moves it. `fill` now resolves
`<TRUTH_COUNT_n>` over every query, the case queries `dilutive,mixed`, and an unfilled token is
a hard error. The regenerated truth's only deltas against `main` are `+1` wherever `base-
batches-accelerator` lands — the one legitimately new entry; before the status reverts they were
`+2`, and that gap is what the flips would have baked into the answer key. It moves v2 truth for
`v2-01`, `v2-19`, `v2-20` and `v2-21`, so #46's baseline (23/24, 24/24) was measured against the
pre-refresh key and does not carry over.

`audit_refresh.py` reported this refresh honest (0 rolled back) because every affected
entry's content changed, which it reads as support for the date bump. A rewritten note
satisfies it exactly as a verified one does. That is the same hole recorded in the 24 August
spec and it is still open.
