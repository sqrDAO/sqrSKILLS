---
name: vietnam-crypto-radar
version: 0.5.0
description: Produce up-to-date intelligence briefings on Vietnam's crypto/digital-asset landscape — laws, decrees, circulars, licensing, tax, accounting, administrative penalties, the pilot exchange market, local controlled technology trials such as Da Nang's crypto/fiat sandbox, city blockchain schemes (Da Nang's Đề án to 2030 and DNC-Chain), Vietnam's International Financial Centre at Ho Chi Minh City and Da Nang, and enforcement. Use this skill WHENEVER the user asks "what's new with Vietnam crypto," wants a regulatory update, asks about a specific instrument (e.g. the DTI Law, Resolution 05, Decree 284, or a TT-BTC circular), wants to know the status of the pilot/VASP licensing, asks about crypto tax or penalties in Vietnam, or needs a briefing for a partner/investor/founder on the VN digital-asset regime. It also covers the retail/consumer reality (see `references/adoption.md`) — why on-chain adoption is top-5 in the world yet you can't pay rent in USDT, which offshore exchanges Vietnamese people actually use (Binance, OKX, Bybit, Bitget, Gate.io, MEXC), whether crypto is spendable day-to-day, and whether crypto cards (Bitget/OKX/SafePal) work here — and maps the VN Web3 ecosystem players as context (communities, builders, student/education programs, events, flagship projects; see `references/ecosystem.md`). Trigger even when the user doesn't say the word "skill" — phrases like "VN crypto reg," "is X legal in Vietnam now," "Vietnam exchange license," "Vietnam crypto fines," "any movement on the sandbox," "Da Nang crypto sandbox," "Da Nang blockchain plan," "what is DNC-Chain," "can I tokenize RWAs in Vietnam," "what is the Vietnam IFC," "which exchanges are popular in Vietnam," "can I pay with crypto/USDT in Vietnam," "do crypto cards work in Vietnam," "who are the Vietnam web3 communities," or "catch me up on Vietnam digital assets" all apply. Prefer this over answering from memory, because the regime is moving fast and stale answers are worse than no answer.
allowed-tools:
  - Read
  - Write
  - WebFetch
  - WebSearch
metadata:
  nanobot:
    always: true
---

# Vietnam Crypto Radar

Generate accurate, current, builder-grade briefings on Vietnam's crypto and digital-asset regulation. The audience is founders, investors, and operators (default register: sharp, crypto-native, precise). The regime went from gray-zone to a comprehensive framework on 1 Jan 2026 and is still issuing implementing rules monthly — so **freshness and the enacted-vs-draft distinction are the whole game.**

If your agent uses different tool names, map `Read` to file-read capability, `Write` to file-write/edit capability, and `WebFetch`/`WebSearch` to whatever live research or browser tools are available.

This skill is not legal advice. It produces intelligence; compliance decisions need licensed Vietnamese counsel. Say so once, briefly, when the output could be read as advice.

## Core method: diff live findings against a dated baseline

"Getting updated" is a diff operation, not a from-scratch research dump. Run it like this:

1. **Load the baseline.** Read `references/baseline.md`. It holds the last-verified snapshot of the regime and a `LAST VERIFIED` date. Everything you report as "new" is new *relative to that date*.
2. **Sweep the sources.** Read `references/sources.md` and pull from sources in tier order — Tier 1 (primary government) first, then Tier 2 (law-firm/analyst trackers), then Tier 3 (crypto-native, fast but noisy). Bias queries to material dated after the baseline's `LAST VERIFIED`. Use the prebuilt query bank in `sources.md` before improvising.
3. **Diff.** For each finding, ask: is this already in the baseline? If yes, skip. If no or changed, it's a candidate update.
4. **Verify before promoting a candidate to fact.** Apply the verification discipline below. Crypto media routinely reports drafts, rumors, and "officials say" as if enacted. Do not repeat that mistake.
5. **Classify status** for every instrument: `EFFECTIVE` / `ENACTED` / `DRAFT` / `PROPOSED` / `EXPECTED` / `REPORTED` / `NEEDS_PRIMARY_SOURCE` / `RUMORED`. This single column is the most valuable thing in the briefing.
6. **Write the briefing** using the output template below.
7. **Offer to update the baseline.** If you confirmed real changes, offer to rewrite `references/baseline.md` with the new state and a fresh `LAST VERIFIED` date, so the next run starts from a better diff point. This is what keeps the skill compounding instead of decaying.

## Verification discipline (do not skip)

Vietnam's process emits a lot of *draft* circulars and ministerial soundbites that never land as written. A finding may be reported as fact in the briefing only if it meets ONE of:

- It cites a **specific instrument number** (e.g. Law 71/2025/QH15, Resolution 05/2025/NQ-CP, Circular 32/2026/TT-BTC, Decision 96/QĐ-BTC) AND a Tier-1 primary source or a named law firm confirms it is signed/issued, **or**
- At least **two independent Tier-2** sources (different firms/outlets) corroborate it.

Everything else is labeled `DRAFT`, `PROPOSED`, or `RUMORED` and clearly flagged. When primary and crypto-native sources conflict, the primary source wins. Always prefer the instrument number over a paraphrase — "Circular 32/2026/TT-BTC" beats "the new tax rule." If you cannot find the instrument number, say the number is unconfirmed.

Distinguish three things that get sloppily merged:
- **Property/asset recognition** (crypto is legally ownable, transferable, inheritable — YES since the DTI Law).
- **Means of payment** (using crypto to pay for goods — still NOT lawful; SBV position persists).
- **Tradable on a licensed market** (only via the pilot's licensed providers; offshore-exchange use sits outside the protected perimeter).

And keep the three permission regimes apart — they have different issuers and perimeters, and sources use "sandbox" for all of them:
- **A municipal controlled trial** (Da Nang, under Nghị quyết 55/2024/NQ-HĐND) — a time-limited technology-trial certificate for a named solution at named sites.
- **The national pilot** (Resolution 05/2025/NQ-CP, Decision 96/QĐ-BTC) — the only route to a licensed crypto-asset trading market.
- **The IFC** (Nghị quyết 222/2025/QH15, Nghị định 323/2025/NĐ-CP) — a special-mechanism zone at HCMC and Da Nang whose Da Nang site is *oriented* toward digital-asset products. Orientation is not authorization.

## Output template

Use this structure. Scale length to the request — a quick "what's new" gets TL;DR + What's New + Sources; a partner briefing gets the full set.

```
# Vietnam Crypto Radar — [Month YYYY]
_Baseline diff since [LAST VERIFIED date]. Not legal advice._

## TL;DR
3–5 bullets. Lead with anything ENACTED or newly EFFECTIVE since the baseline.

## What's new since [date]
Each item: [STATUS] — headline — instrument number — what it changes — source.
If nothing material changed, say so plainly (that is a valid, useful answer).

## Instrument tracker
A compact status table: Instrument | What it governs | Status | Effective date.
Pull the standing rows from baseline.md, update statuses, add new rows.

## Market & licensing
Pilot exchange progress, VASP licensing shortlist/approvals, capital thresholds,
notable entrants/exits, settlement (VND) rules.

## Tax corner
CIT / PIT / VAT treatment, withholding mechanics, effective dates, open questions.

## Watch list
What's expected next and roughly when (drafts in flight, promised decrees,
stated official timelines). Mark each EXPECTED/DRAFT/RUMORED.

## Sources
Primary instruments and Tier-1 links first; analyst/crypto-native after.
```

## Tone

Builder-facing and direct. Crypto-native register is fine and expected (GM, BUIDL, VASP, ser) — but never at the expense of precision on a legal point. A founder reading this should be able to act on it or take it to counsel without re-checking the basics. A light "GM" open or sign-off is fine; the substance must be exact.

## Reference files

- `references/baseline.md` — current regime snapshot + anchor facts + the `LAST VERIFIED` date you diff against. **Read first, every run.** Offer to update it after confirming changes.
- `references/sources.md` — the tiered source registry: where to look, what each covers, suggested cadence, and the verification rule restated. Read when sweeping for updates.
- `references/glossary.md` — Vietnamese legal-instrument types (Luật/Nghị định/Nghị quyết/Thông tư/Quyết định), the regulators and who owns what, and VN-specific crypto terminology. Read when you need to explain or correctly label an instrument.
- `references/adoption.md` — the **retail/consumer reality**: the adoption paradox (top-5 on-chain adoption vs. no lawful merchant payments), how spending actually works (crypto→VND QR gateways, cards), which **offshore exchanges** VN retail actually uses (Binance/OKX/Bybit/Bitget/Gate/MEXC) and how they sit outside the pilot perimeter, and crypto-card availability (Bitget/OKX/SafePal). **Context only — separate from the regulatory diff loop**, but anchored to the same property/payment/tradable distinction. Read on demand for "can I pay with crypto here," "which exchange is popular," or "do crypto cards work" questions, not for a regulatory update.
- `references/ecosystem.md` — the VN Web3 ecosystem map: communities & DAOs, education/student programs, events & hackathons, flagship projects, and a defunct/excluded list. **Context only — separate from the regulatory diff loop.** Read on demand when the user asks who the players/communities/events are, not when they ask for a regulatory update. Cross-links apply-able opportunities to the `web3-opportunities` skill.

## Quick triggers → what to do

- "What's new with VN crypto?" → full diff run, output briefing.
- "Is [X] legal in Vietnam now?" → load baseline, answer with the property/payment/tradable distinction, verify currency of the point, cite the instrument.
- "Status of the pilot / exchange licenses?" → sweep Tier-1 + Tier-2, fill Market & licensing section.
- "What is happening in the Da Nang crypto sandbox?" → load `baseline.md` for all six
  local controlled-trial decisions — 1181 (Basal Pay) and 2895 (MIMO), both still running,
  plus 3809–3812 from 22 Aug 2026 — and `adoption.md` for the crypto→VND use cases. Six is
  a floor, not a total: the regime is not crypto-specific and earlier 2026 batches are not
  enumerated, so check for newer approvals before answering. The regime runs under
  **Nghị quyết 55/2024/NQ-HĐND**, not 20/2026 — the 2025 approvals predate 20/2026. State
  explicitly that a Da Nang technology-trial approval is not a national CASP/exchange license
  and does not legalize direct crypto merchant payments nationwide.
- "What is Da Nang's blockchain plan / DNC-Chain / the Đề án?" → read the
  `Da Nang blockchain scheme to 2030` section of `baseline.md`. Lead with what it is
  (Quyết định 2728/QĐ-UBND, 23 Jun 2026, a municipal programme document) and what it is not
  (no licence, no payment authorisation). Give the four tiers, then be precise about Tier 4:
  SP8 crypto→fiat runs under the **city sandbox** and is already live there; SP9 (crypto-asset
  and RWA issuance, custody, trading) and SP10 (blockchain crowdfunding) run under the **IFC**
  and are at coordination stage, not approved. Flag that DNC-Chain itself will not host a
  crypto exchange, and that one Tier-2 outlet misfiled that constraint under Tier 4.
- "What is the Vietnam IFC / can I tokenize RWAs there?" → Nghị quyết 222/2025/QH15 and
  Nghị định 323, 324 & 329/2025/NĐ-CP: one centre, two sites (HCMC and Da Nang), with the
  Da Nang site *oriented* toward controlled testing of new financial models and digital-asset
  products. Orientation is not a licence and not an operating market — no digital-asset member
  admission is on record. Disambiguate "IFC" from the World Bank's International Finance
  Corporation, which appears in the same coverage. Da Nang's ~US$4bn infrastructure-tokenisation
  proposal is PROPOSED / SINGLE-SOURCE; do not present it as a programme.
- "Vietnam crypto tax?" → Tax corner; trace the rule through Law 109/2025/QH15, Decree 253/2026/NĐ-CP, and Circulars 32, 41 & 87/2026/TT-BTC; include Decree 254/2026/NĐ-CP when e-invoicing is relevant; flag the individual-PIT withholding mechanism's operational status.
- "What are the penalties / can I use an unlicensed exchange?" → load baseline, verify Decree 284/2026/NĐ-CP is in force for the date asked, distinguish organization and individual fine ceilings, and state whether the conduct falls inside the pilot rules before quoting a penalty.
- "Brief a partner/investor on VN digital assets" → full template, lead with the asset-recognition + pilot story, keep it tight.
- "Who are the VN Web3 communities / builders / events?" → read `references/ecosystem.md`, answer from the map (communities, education, events, flagships), and offer a live refresh. This is context, not a regulatory diff — skip the baseline loop. Point builders to the `web3-opportunities` skill for apply-able programs.
- "Can I pay rent / buy things with USDT in Vietnam?" / "Why isn't crypto usable if adoption is so high?" → read `references/adoption.md`, lead with the payment ban + adoption-paradox framing (§1–2), explain the gateway/card workarounds. Verify the SBV payment line is current. This is consumer context, not a regulatory diff.
- "Which exchanges are popular in Vietnam?" / "Do Binance/OKX/Bitget/Gate/MEXC get used there?" → read `references/adoption.md` §3, answer with the offshore-retail reality (Binance dominant; OKX/Bybit/Bitget/Gate/MEXC by use case), and flag they sit **outside** the licensed pilot perimeter. Re-verify popularity live.
- "Do crypto cards (Bitget/OKX/SafePal) work in Vietnam?" → read `references/adoption.md` §4; explain cards route around the payment ban via crypto→fiat conversion but hit country/KYC gates (Bitget most likely available, OKX largely EEA-locked). Re-verify country support live.
