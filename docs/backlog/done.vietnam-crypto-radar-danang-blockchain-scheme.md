# Add Da Nang's blockchain scheme and the IFC layer
**Deps**: vietnam-crypto-radar-da-nang-trials

## Goal
Record what the signed Quyết định 2728/QĐ-UBND (23 Jun 2026) and its annexed Đề án
establish for Da Nang — the DNC-Chain shared infrastructure, the four-tier product
roadmap whose top tier is crypto-asset finance, and the split between the city
sandbox and the International Financial Centre — and close the resulting gap: the
IFC regime is absent from the baseline even though Da Nang is one of its two sites.
Correct the instrument the 2025 trial approvals were issued under, which the city's
own signed text names as Nghị quyết 55/2024/NQ-HĐND, not 20/2026/NQ-HĐND.

## Files
- `vietnam-crypto-radar/SKILL.md` (edited) — route the scheme, DNC-Chain and IFC questions; bump to 0.5.0
- `vietnam-crypto-radar/references/baseline.md` (edited) — new instruments, the scheme section, the correction, anchors
- `vietnam-crypto-radar/references/glossary.md` (edited) — IFC name collision, Đề án, DNC-Chain, RWA
- `vietnam-crypto-radar/references/sources.md` (edited) — Da Nang document host, IFC anchors, query bank
- `scripts/check_anchors.py` (edited) — a `.pdf` anchor must come back as a PDF, not a 200 HTML error page
- `tests/test_refresh_harness.py` (edited) — regression coverage for that rule
- `.github/workflows/weekly-skill-refresh.yml` (edited) — the refresh prompt carries the correction
- `AGENTS.md` (edited) — record the anchor-checker invariant
- `tests/test_vietnam_crypto_radar.py` (edited) — pin the correction and the new boundaries
- `README.md` (edited) — skill inventory mentions the city blockchain scheme and IFC
- `docs/backlog/PRIORITY.md` (edited) — rank this open spec
- `docs/backlog/todo.vietnam-crypto-radar-danang-blockchain-scheme.md` (new) — task spec

## Acceptance
- [x] `2728/QĐ-UBND` is recorded with its 23 Jun 2026 signing, its effect-on-signing clause, Sở KH&CN as lead, and a public Tier-1 anchor byte-identical to the supplied file by SHA-256, which `check_anchors.py` now content-checks so a moved `.pdf` cannot pass on its status code
- [x] `55/2024/NQ-HĐND` (13 Dec 2024) is recorded as the resolution the 2025 approvals were issued under, sourced to the Đề án's own legal-basis list, with the date pinned to the row
- [x] The baseline no longer implies Decisions 1181 (Aug 2025) and 2895 (Dec 2025) were issued under a resolution dated 29 May 2026
- [x] `20/2026/NQ-HĐND` keeps its REPORTED / SINGLE-SOURCE label and is described as a later detailing resolution whose relationship to 55/2024 is an open question
- [x] The four-tier roadmap is recorded with SP8 (crypto→fiat, which the roadmap records as already running under the sandbox), SP9 (crypto-asset/RWA issuance, custody, trading) and SP10 (blockchain crowdfunding), and with the mechanism each runs under — sandbox for SP8, IFC for SP9 and SP10
- [x] DNC-Chain's three binding constraints are recorded: no public crypto-asset trading modules, no exchange on the shared infrastructure, and a verification/reconciliation-only role for IFC and sandbox models
- [x] The "no public crypto exchange" wording is attributed to where it belongs — DNC-Chain's constraints and the Tier-3 principle — not to Tier 4, which one Tier-2 outlet misplaced it under
- [x] The IFC instruments are added with Tier-1 anchors: `222/2025/QH15`, `323/2025/NĐ-CP`, `324/2025/NĐ-CP`, `329/2025/NĐ-CP`
- [x] Da Nang's IFC orientation toward digital-asset products and controlled testing is quoted from the Tier-1 government-news anchor, not paraphrased into a licensing claim
- [x] `143/2025/QH15` is recorded as the statutory basis for crypto-asset services being a conditional business line from 1 Jul 2026, and the signing date it carries is the Tier-1 one (11 Dec 2025), with the Đề án's conflicting 27 Jun 2025 noted as a discrepancy
- [x] The ~US$4bn Da Nang RWA tokenisation proposal is tracked under IN MOTION as PROPOSED / SINGLE-SOURCE, with the two projects and their values
- [x] The glossary separates Vietnam's IFC (Trung tâm tài chính quốc tế) from the World Bank's International Finance Corporation, both of which appear in Da Nang coverage
- [x] The baseline's `LAST VERIFIED` date stays 31 August 2026; this pass is recorded as a targeted document-sourced update, not a sweep
- [x] NOT: describe the Đề án, DNC-Chain, or an IFC membership as a crypto-asset service-provider or exchange licence
- [x] NOT: state that SP9 or SP10 is operating — both are coordination-stage items with no approval recorded
- [x] The weekly refresh prompt carries the correction, the Tier-4 mechanism mapping and the IFC disambiguation, since it regenerates `baseline.md` wholesale
- [x] No file states which resolution governs the 22 Aug 2026 batch — `SKILL.md`, `glossary.md` and `adoption.md` agree with the baseline that it is unresolved
- [x] NOT: cite the annexed Đề án as if it were publicly resolvable; only the promulgating Decision is
- [x] NOT: present an approval inside a trial period as verified user-facing operation

## Verify
- `python3 scripts/validate_skills.py` → JSON with `"ok": true`
- `python3 -m unittest discover -s tests -v` → all tests pass
- `python3 scripts/check_unanchored.py --since origin/main` → JSON with `"ok": true`
- `python3 scripts/check_anchors.py --targets baseline` → no dead baseline anchors
- `git diff --check` → no whitespace errors
- `rg -n "2728/QĐ-UBND|55/2024/NQ-HĐND|DNC-Chain|323/2025|143/2025" vietnam-crypto-radar` → new material is discoverable

## Notes
Provenance: the promulgating Decision is public and hash-verified against the supplied
file, but its number and day are blank in its text layer — both come from the portal
filename and the file timestamp, which agree. The annexed Đề án is not resolvable at the
portal's paths and carries one unnamed CA seal, not a dated named signature, so
annex-only detail is labelled. It is nonetheless the first Tier-1 text to say which
resolution the trials sit under, making the 24 August framing wrong on the point it was
least sure about — the outcome its SINGLE-SOURCE label existed for.

Review found seven defects in this spec's own work. Two were load-bearing: the weekly
refresh prompt still named 20/2026/NQ-HĐND and knew nothing about the scheme, so the next
run would have restored the corrected framing — a correction made only in the data file
has a one-week half-life here; and the state-of-play asserted the Annex IV commencement
flat while its own row recorded that the Tier-1 page does not carry it. Three were tests
asserting the presence of prose rather than the claim inside it: the Tier-4 test passed on
a baseline with the sandbox and IFC mechanisms reversed, and the Investment Law test on
the wrong signing date. CodeRabbit then found the same over-assertion, fixed in
`baseline.md`, still standing in `SKILL.md`, `glossary.md` and `adoption.md` — the
strongest claim in the least-qualified file, which is what an agent reads first. It also
caught that `sources.md` documents Da Nang's 200-with-HTML trap while `check_anchors.py`
could not act on it; `.pdf` anchors are now content-checked.

Completion approved by the user on 4 September 2026. Shipped in #50. Checks at merge:
validate_skills.py ok, 191/191 tests, check_unanchored ok, 47 baseline anchors resolve
with 0 dead (1 unverified, a 403 from thuvienphapluat), git diff --check clean.
