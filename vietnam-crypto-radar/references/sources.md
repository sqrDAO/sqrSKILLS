# Source Registry — Vietnam Crypto Radar

Sweep in tier order: Tier 1 (primary government) → Tier 2 (legal/analyst) → Tier 3
(crypto-native). Bias every query to material dated after the baseline's `LAST VERIFIED`.

**Verification rule (restated):** report a finding as fact only if it cites a specific
instrument number confirmed by a Tier-1 source or a named law firm, OR if two independent
Tier-2 sources corroborate it. Otherwise label DRAFT / PROPOSED / RUMORED. Primary beats
crypto-native on every conflict. Always carry the instrument number.

---

## Tier 1 — Primary government (authoritative; slow but definitive)

| Source | URL | Covers | Cadence |
|---|---|---|---|
| Government legal documents DB | vanban.chinhphu.vn | Decrees, resolutions, decisions — full text + status | Per run |
| Government News (EN) | en.baochinhphu.vn | Official announcements, minister statements | Per run |
| Government News (VN) | baochinhphu.vn | Same, fuller/earlier in Vietnamese | Per run |
| Ministry of Finance | mof.gov.vn | Asset market, circulars, tax policy, pilot | Per run |
| State Bank of Vietnam | sbv.gov.vn | Payments, AML, monetary, the payment-ban line | Monthly |
| General Department of Taxation | gdt.gov.vn | Tax declaration/withholding, guidance | Monthly |
| State Securities Commission | ssc.gov.vn | Market-conduct supervision (watch for crypto-market remit) | Monthly |
| National Assembly | quochoi.vn | Primary laws, legislative agenda | Quarterly / on news |
| Legal text database | thuvienphapluat.vn | Searchable instrument lookup, status, effective dates (partly paywalled but best for confirming a number/status) | Per run when confirming an instrument |
| Official Gazette (Công báo) | congbao.chinhphu.vn | Authoritative publication of issued instruments | When confirming issuance |
| Da Nang city portal | danang.gov.vn | Municipal controlled technology trials and local implementation decisions | On Da Nang signal |

> Tip: the fastest way to *confirm* a rumored circular is real is to search its number on
> thuvienphapluat.vn or find it on vanban.chinhphu.vn / congbao. No number on a primary site = treat as DRAFT/RUMORED.

### Known primary anchors

- DTI Law passage/effective date: `https://en.baochinhphu.vn/law-on-digital-technology-industry-approved-111250614143640329.htm`
- Decree 284/2026/NĐ-CP status, signed text, and effective date: `https://vanban.chinhphu.vn/?docid=218906&pageid=27160`
- Government summary of Decree 284 penalties: `https://baochinhphu.vn/cung-cap-dich-vu-lien-quan-den-tai-san-ma-hoa-khi-chua-duoc-cap-phep-bi-phat-toi-200-trieu-dong-10226071715275345.htm`
- Circular 15/2026/TT-BTC accounting rules: `https://vanban.chinhphu.vn/?docid=217123&pageid=27160`
- Decree 253/2026/NĐ-CP PIT implementation: `https://vanban.chinhphu.vn/?classid=1&docid=218684&orggroupid=2&pageid=27160`
- Circular 87/2026/TT-BTC general PIT guidance: `https://vanban.chinhphu.vn/?classid=1&docid=218772&orggroupid=4&pageid=27160`
- Decree 254/2026/NĐ-CP electronic invoices: `https://vanban.chinhphu.vn/?classid=1&docid=218689&pageid=27160`
- Government summary of Decree 254 Article 6: `https://baochinhphu.vn/quy-dinh-doi-tuong-su-dung-hoa-don-dien-tu-10226070308163723.htm`
- National Assembly legal text search: `https://quochoi.vn` and legal databases for the law number/title.
- When checking payment legality, search SBV for both English and Vietnamese terms: `tiền ảo`, `tài sản ảo`, `tài sản mã hóa`, `phương tiện thanh toán`, `NHNN-PC`.
- Da Nang Decisions 3809–3812/QĐ-UBND controlled technology trials: `https://danang.gov.vn/vi/web/dng/w/chi-dao-dieu-hanh-noi-bat-cua-ubnd-chu-tich-cac-pho-chu-tich-ubnd-thanh-pho-ngay-22-8` (confirmed 24 Aug 2026). Treat these as local trial approvals, not national CASP/exchange licenses.

---

## Tier 2 — Legal & analyst trackers (high signal, English, instrument-anchored)

These firms publish client alerts that cite instrument numbers and effective dates — ideal for the tracker.

- **Vietnam Briefing (Dezan Shira)** — vietnam-briefing.com — practical regulatory + tax explainers.
- **Baker McKenzie / BMVN** — bakermckenzie.com (insights) — detailed tax & market alerts (authored Circular 32/41 analysis).
- **Tilleke & Gibbins** — tilleke.com — fintech/digital-asset notes.
- **Allens, VILAF, YKVN, Frasers, Russin & Vecchi** — client alerts (often surfaced via Lexology).
- **Lexology** — lexology.com — aggregates the above firm alerts; good single search surface.
- **RMIT Vietnam** — rmit.edu.vn/news — academic/policy commentary.
- **Global Legal Insights / Chambers / Mondaq** — annual or periodic VN crypto-regulation chapters (good for structured baselines, less for breaking news).

### Known Tier-2 anchors

- DTI Law overview: `https://www.vietnam-briefing.com/news/vietnam-passes-first-ever-law-on-digital-technology-industry.html/`
- Vietnam Briefing search pattern: `site:vietnam-briefing.com Vietnam digital assets crypto Law on Digital Technology Industry`
- Lexology search pattern: `site:lexology.com Vietnam crypto assets circular tax TT-BTC`

---

## Tier 3 — Crypto-native & market (fast, broad, NOISY — verify before reporting)

Use for early signal and market color (entrants, license shortlists, sentiment). Never the
sole basis for a stated fact.

- **Coin68** — coin68.com — leading Vietnamese crypto outlet.
- Local VN tech/business press — VnExpress (vnexpress.net), Tuoi Tre, VietnamNet — pick up minister statements and forum remarks early.
- **CoinDesk / Cointelegraph / The Block** — regional/SEA desks for international framing.
- **Chainalysis** — chainalysis.com — Global Crypto Adoption Index, on-chain reports.
- Exchange research/help centers (e.g. tax guides) — useful for *how rules are being operationalized*, but they are interpretations, not law.

---

## Suggested run cadence
- **Lightweight "what's new" check:** Tier 1 government news + Lexology + Coin68, filtered to last 2–4 weeks.
- **Full briefing:** all of Tier 1 + Tier 2, with Tier 3 for market/licensing color.
- **Confirming a specific instrument:** thuvienphapluat.vn / vanban.chinhphu.vn / congbao for the number and status, then one firm alert for plain-English interpretation.

## Query patterns that work
- `Vietnam crypto regulation [current month year]`
- `[instrument number] TT-BTC` or `Nghị định crypto Vietnam`
- `Vietnam VASP license pilot exchange [year]`
- `Vietnam crypto tax circular [year]`
- `tài sản mã hóa Việt Nam` (Vietnamese: "crypto assets Vietnam" — surfaces local/primary results earlier)
- `tài sản số nghị định` (Vietnamese: "digital assets decree")
- `"Law on Digital Technology Industry" "digital assets" Vietnam`
- `"Resolution 05/2025/NQ-CP" "crypto" Vietnam`
- `"05/2025/NQ-CP" "tài sản mã hóa"`
- `"Decision 96/QĐ-BTC" "tài sản mã hóa"`
- `"Circular 32/2026/TT-BTC" crypto`
- `"Circular 41/2026/TT-BTC" crypto`
- `"thuế" "tài sản mã hóa" "TT-BTC"`
- `"284/2026/NĐ-CP" "tài sản mã hóa"`
- `"253/2026/NĐ-CP" "tài sản mã hóa"`
- `"254/2026/NĐ-CP" "tài sản mã hóa"`
- `"87/2026/TT-BTC" "tài sản mã hóa"`
- `site:vanban.chinhphu.vn "tài sản mã hóa" [current month year]`
- `site:baochinhphu.vn "tài sản mã hóa" after:[LAST VERIFIED as YYYY-MM-DD]`
- `site:danang.gov.vn ("tài sản số" OR "tài sản mã hóa") ("thử nghiệm có kiểm soát" OR sandbox)`
- `"3809/QĐ-UBND" OR "3810/QĐ-UBND" OR "3811/QĐ-UBND" OR "3812/QĐ-UBND"`
