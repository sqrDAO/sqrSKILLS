# Add Da Nang's blockchain scheme and the IFC layer
**Deps**: vietnam-crypto-radar-da-nang-trials

## Goal
Record what the signed Quyết định 2728/QĐ-UBND (23 Jun 2026) and its annexed Đề án
establish for Da Nang — the DNC-Chain shared infrastructure, the four-tier product
roadmap whose top tier is crypto-asset finance, and the split between the city
sandbox and the International Financial Centre — and close the resulting gap: the
IFC regime is absent from the baseline even though Da Nang is one of its two sites.
Correct the enabling instrument for the controlled trials, which the city's own
signed text names as Nghị quyết 55/2024/NQ-HĐND, not 20/2026/NQ-HĐND.

## Files
- `vietnam-crypto-radar/SKILL.md` (edited) — route the scheme, DNC-Chain and IFC questions; bump to 0.5.0
- `vietnam-crypto-radar/references/baseline.md` (edited) — new instruments, the scheme section, the correction, anchors
- `vietnam-crypto-radar/references/glossary.md` (edited) — IFC name collision, Đề án, DNC-Chain, RWA
- `vietnam-crypto-radar/references/sources.md` (edited) — Da Nang document host, IFC anchors, query bank
- `tests/test_vietnam_crypto_radar.py` (edited) — pin the correction and the new boundaries
- `README.md` (edited) — skill inventory mentions the city blockchain scheme and IFC
- `docs/backlog/PRIORITY.md` (edited) — rank this open spec
- `docs/backlog/todo.vietnam-crypto-radar-danang-blockchain-scheme.md` (new) — task spec

## Acceptance
- [ ] `2728/QĐ-UBND` is recorded with its 23 Jun 2026 signing, its effect-on-signing clause, Sở KH&CN as lead, and a public Tier-1 anchor
- [ ] The anchor is the same document as the file supplied: byte-identical by SHA-256
- [ ] `55/2024/NQ-HĐND` (13 Dec 2024) is recorded as the resolution the controlled-trial regime runs under, sourced to the Đề án's own legal-basis list
- [ ] The baseline no longer implies Decisions 1181 (Aug 2025) and 2895 (Dec 2025) were issued under a resolution dated 29 May 2026
- [ ] `20/2026/NQ-HĐND` keeps its REPORTED / SINGLE-SOURCE label and is described as a later detailing resolution whose relationship to 55/2024 is an open question
- [ ] The four-tier roadmap is recorded with SP8 (crypto→fiat, already running under the sandbox), SP9 (crypto-asset/RWA issuance, custody, trading) and SP10 (blockchain crowdfunding), and with the mechanism each runs under — sandbox for SP8, IFC for SP9 and SP10
- [ ] DNC-Chain's three binding constraints are recorded: no public crypto-asset trading modules, no exchange on the shared infrastructure, and a verification/reconciliation-only role for IFC and sandbox models
- [ ] The "no public crypto exchange" wording is attributed to where it belongs — DNC-Chain's constraints and the Tier-3 principle — not to Tier 4, which one Tier-2 outlet misplaced it under
- [ ] The IFC instruments are added with Tier-1 anchors: `222/2025/QH15`, `323/2025/NĐ-CP`, `324/2025/NĐ-CP`, `329/2025/NĐ-CP`
- [ ] Da Nang's IFC orientation toward digital-asset products and controlled testing is quoted from the Tier-1 government-news anchor, not paraphrased into a licensing claim
- [ ] `143/2025/QH15` is recorded as the statutory basis for crypto-asset services being a conditional business line from 1 Jul 2026, and the signing date it carries is the Tier-1 one (11 Dec 2025), with the Đề án's conflicting 27 Jun 2025 noted as a discrepancy
- [ ] The ~US$4bn Da Nang RWA tokenisation proposal is tracked under IN MOTION as PROPOSED / SINGLE-SOURCE, with the two projects and their values
- [ ] The glossary separates Vietnam's IFC (Trung tâm tài chính quốc tế) from the World Bank's International Finance Corporation, both of which appear in Da Nang coverage
- [ ] The baseline's `LAST VERIFIED` date stays 31 August 2026; this pass is recorded as a targeted document-sourced update, not a sweep
- [ ] NOT: describe the Đề án, DNC-Chain, or an IFC membership as a crypto-asset service-provider or exchange licence
- [ ] NOT: state that SP9 or SP10 is operating — both are coordination-stage items with no approval recorded
- [ ] NOT: cite the annexed Đề án as if it were publicly resolvable; only the promulgating Decision is

## Verify
- `python3 scripts/validate_skills.py` → JSON with `"ok": true`
- `python3 -m unittest discover -s tests -v` → all tests pass
- `python3 scripts/check_unanchored.py --since origin/main` → JSON with `"ok": true`
- `python3 scripts/check_anchors.py --targets baseline` → no dead baseline anchors
- `git diff --check` → no whitespace errors
- `rg -n "2728/QĐ-UBND|55/2024/NQ-HĐND|DNC-Chain|323/2025|143/2025" vietnam-crypto-radar` → new material is discoverable

## Notes
Provenance: the promulgating Decision is public and hash-verified against the supplied
file. The annexed Đề án is not resolvable at the portal's document paths, so annex-only
detail is labelled as such; the city portal and two outlets carry the headline content
(DNC-Chain, ten products, four tiers, the 2026-27 / 2028-30 phasing) independently.

The Đề án is the first Tier-1 text to state which resolution the trials sit under. That
makes the 24 August framing wrong on the point it was least sure about, which is the
outcome its SINGLE-SOURCE label was for.
