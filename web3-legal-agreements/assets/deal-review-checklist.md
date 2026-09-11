# Deal Review Checklist (Track B working template)

Work top to bottom on any incoming agreement. For each item, record: what the
document says, whether it is market / off-market / dangerous, and the specific
change to request. Skip items that do not apply to the instrument type.

## 0. Orientation
- [ ] Instrument type identified (SAFE, note/bond, SAFT, token warrant, side
      letter, TPA/TSA, term sheet, advisor agreement).
- [ ] Parties identified: who is issuer / company, who is investor, which is the
      DevCo vs the token issuer.
- [ ] Governing law and dispute-resolution seat noted.
- [ ] Which side am I optimizing for (investor / founder)? Stated at the top.
- [ ] Binding vs non-binding confirmed (term sheets: confirm only confidentiality
      / exclusivity bind).

## 1. Economics (equity leg)
- [ ] Purchase amount correct.
- [ ] Post-money valuation cap and/or discount, and implied ownership computed.
- [ ] Interest rate and maturity (notes/bonds), and whether interest converts.
- [ ] Conversion trigger and mechanics (priced round threshold, pre/post-money).
- [ ] Liquidation priority and cash-out floor.
- [ ] MFN present? Pro-rata present or via separate side letter?

## 2. Economics (token leg)
- [ ] Token allocation basis pinned: fixed price formula vs pro-rata of team
      allocation.
- [ ] Reference price per token, and effective discount vs known IDO/trading
      price.
- [ ] Token count at TGE computed; break-even multiple computed.
- [ ] Total supply and tokenomics table cross-checked.
- [ ] Anti-dilution / tokenomics-upgrade protection present; ratchet vs pro-rata;
      survives vesting?
- [ ] Refund on dissolution present and prioritized (SAFT / term sheet).

## 3. Vesting, lockup, delivery
- [ ] Lockup period and start point (from TGE / Token Launch) defined.
- [ ] Vesting schedule (TGE unlock, cliff, linear period) defined and symmetric
      with other investors.
- [ ] TGE / Token Launch defined precisely (no vague trigger).
- [ ] Exercise window and exercise price (warrants).
- [ ] Delivery conditions and who bears the obligation (DevCo vs issuer).

## 4. Control and information
- [ ] Information rights.
- [ ] Tokenomics-change consent (and how broad).
- [ ] ROFR / ROFO / pro-rata rights.
- [ ] Board / governance rights, if any.
- [ ] Transfer / assignment restrictions (and affiliate carve-out).

## 5. Risk and framing
- [ ] Non-security / utility framing present and supportable.
- [ ] Legal-opinion covenant present (especially Singapore issuers: Payment
      Services Act, Securities and Futures Act, gaming law if applicable).
- [ ] Reps and warranties balanced (issuer vs investor).
- [ ] Indemnity scope.
- [ ] Arbitration clause and its effect on litigation rights.
- [ ] Correct entity as counterparty for this leg (DevCo for equity, issuer for
      token sale).

## 6. Reconciliation and side agreements
- [ ] Equity percentage and token percentage computed and internally consistent.
- [ ] All side letters and advisor allocations listed; effect on the base deal
      noted.
- [ ] Governing law consistent across the equity and token legs.
- [ ] Compared against the closest deal archetype (see playbook.md); any term
      worse than precedent flagged.

## 7. Escrow, forfeiture, and ToS (if the document has these; see references/escrow-forfeiture.md)
- [ ] Escrow holder and authority identified (agent / multisig / smart contract),
      and custody or money-transmission licensing considered.
- [ ] Release and refund conditions are objective and verifiable (milestone /
      time-lock / oracle / mutual approval), not vague.
- [ ] Dispute and fallback path present; a timeout-to-refund so funds cannot lock
      forever; fees and segregation stated.
- [ ] Smart-contract escrow: audit status, admin/upgrade keys, oracle trust
      assumption checked.
- [ ] Forfeiture framed as a condition on a primary right ("earned only if")
      rather than a penalty on breach, where possible.
- [ ] Forfeiture tied to a stated legitimate interest and proportionate (graduated
      or pro-rata, not punitive all-or-nothing).
- [ ] Notice and, where fair, a cure period before forfeiture triggers.
- [ ] Consumer classification decided; if consumer-facing, terms are transparent,
      prominent, and pass the unfair-terms filter (good faith + no significant
      imbalance).
- [ ] ToS acceptance is affirmative (not browsewrap); incorporated documents
      referenced and accessible; change-control and governing-law/forum clean.
- [ ] Every trigger term (leaver, breach, milestone, expiry, slashing) defined and
      aligned with any on-chain logic.

## 8. Output
- [ ] Lead with the 2-3 items that move money or control.
- [ ] Redline summary: each proposed edit with a one-line rationale.
- [ ] Offer to draft replacement language for the top-priority clauses.
- [ ] Close with: this is structuring support, not legal advice; have qualified
      counsel in the governing-law jurisdiction review before signing.
