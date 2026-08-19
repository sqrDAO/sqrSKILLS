# Correct the 2026-08-17 weekly refresh before merge

**Deps**: vietnam-visa-policy-verification-corrections

## Goal
Bring PR #28 up to the repository's own verification standard. The automated refresh
added real instruments alongside dead citations, one misdated instrument, an arrival
claim the project had already ruled out, and a large silent deletion of caveats added
by PR #25.

## Files
- `vietnam-crypto-radar/references/baseline.md` (edited) — restore caveats, correct dates, repoint anchors
- `vietnam-visa-check/data/vietnam_immigration_policy.json` (edited) — restore the PAI text, repoint Decree 286
- `web3-opportunities/data/web3_opportunities.json` (edited) — restore the YZi Labs rolling posture
- `README.md` (edited) — record the 17 August refresh
- `tests/test_vietnam_crypto_radar.py` (new) — pin the corrected crypto facts
- `tests/test_vietnam_visa_check.py` (edited) — pin Decree 286's scope
- `docs/backlog/PRIORITY.md` (edited) — track this spec

## Acceptance
- [ ] `DIGITAL_ARRIVAL_CARD` states the Tan Son Nhat-only pilot; the airport-expansion claim is labelled unconfirmed
- [ ] Every source anchor added by the refresh resolves, or its claim is dropped
- [ ] `Quyết định 21/2026/QĐ-TTg` is dated 30 Apr 2026 signed / 1 Jul 2026 effective
- [ ] Blockchain is described as one item in Group 1, not a standalone national priority
- [ ] The caveats added by PR #25 are present: 66.23 scope, anchor-resolution rule, single-source promotion rule
- [ ] Material legal qualifiers survive: Decree 254 high-tax-risk carve-out, Decree 284 one-half rule and transition warning
- [ ] The unconfirmed Securities Law claim is recorded as UNVERIFIED, not stated as fact
- [ ] YZi Labs is not advertising an unsourced application cutoff
- [ ] Regression tests fail if any of the above regress
- [ ] NOT: assert a PAI rollout beyond Tan Son Nhat on Tier-3 commercial visa sites

## Verify
- `python3 scripts/validate_skills.py` → JSON with `"ok": true`
- `python3 -m unittest discover -s tests -v` → all tests pass
- `git diff --check` → no whitespace errors

## Notes
Anchors confirmed to resolve on 17 August 2026: `vanban.chinhphu.vn/?docid=218986`
(Decree 296), `vanban.chinhphu.vn/?docid=218002` and
`baochinhphu.vn/10-nhom-cong-nghe-chien-luoc-tu-1-7-2026-...` (Decision 21),
`baochinhphu.vn/cac-bo-nganh-dia-phuong-phoi-hop-...` (Decree 286), VietnamPlus and
Saigon Giai Phong (Conviction 2026), VietnamPlus (combined AML bill, 5 Aug 2026).

The refresh workflow opens PRs as `github-actions`, so `Repository Checks` sits at
`action_required` and never runs. The failing test here was invisible on the PR page.
Worth fixing separately so the harness is not advisory.
