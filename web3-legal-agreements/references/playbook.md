# Deal Playbook

Practical posture for using these instruments, for both sides of the table, plus
the market-standard structures worth reaching for instead of starting from a
blank page. This is project-neutral: it works for any Web3 team raising and any
investor writing a check. State which side you are optimizing for at the top of
every analysis; the instrument is the same, the posture flips.

## Investor-side posture

A crypto-native investor usually wants both equity exposure and token upside.
Optimize for:

- **Both legs, reconciled.** Expect an equity leg and a token leg, and compute
  the resulting equity percentage and token percentage explicitly. Do not sign a
  token project on equity alone with a vague token promise; pin the token basis.
- **Defined token allocation.** Prefer a token warrant or a clearly formula-based
  side letter over a loose promise. Know exactly how the token count is derived
  (fixed price vs pro-rata of the team allocation).
- **Downside protection.** Look for cash-out or refund on dissolution,
  liquidation priority on the equity leg, and anti-dilution / tokenomics-upgrade
  protection on the token leg.
- **Rights that fit the check size.** Pro-rata / ROFO to hold percentage,
  information rights, and (for larger or strategic checks) tokenomics-change
  consent and ROFR on the next project.
- **Clean vesting.** Confirm lockup and vesting are symmetric with other
  investors and that you are not left last in line.
- **Advisor allocation kept separate.** Where an advisor role is attached, keep
  advisor tokens in a distinct allocation with their own (often longer) vesting.
- **Correct counterparty.** Sign equity with the development company and token
  documents with the issuer entity; keep your investing vehicle consistent across
  a portfolio for clean records.

## Founder-side posture

A team raising should give investors enough certainty to sign while protecting
runway and control:

- **Protect the cap table.** Avoid stacking too many SAFEs into a Series A
  surprise; model conversion before signing.
- **Keep token commitments flexible pre-TGE.** Use a warrant or side letter that
  does not lock final tokenomics; avoid fixed TGE dates you cannot hit (use a
  deadline, for example "no later than 12 months", if a date is needed).
- **Contain token risk.** Keep the token leg in a separate entity and document
  from the corporate cap table.
- **Cap investor governance.** Narrow tokenomics-change consent and information
  rights to what a lead reasonably needs; resist broad vetoes.
- **Match the instrument to stage.** Do not sign a SAFT before the entity is
  token-ready; do not run a direct token sale (TPA) before you can legally issue.

## Common executed structures (reach for these first)

These are battle-tested market archetypes. Start from the closest one rather than
a blank page.

- **SAFT (raise-for-token, TGE delivery).** For a token-ready issuer raising to
  launch: purchase amount and token price in an exhibit, TGE within a defined
  window, refund on dissolution, non-security framing with a legal-opinion
  posture. Reach for this when the entity is ready and the raise is a token raise.
- **Post-money SAFE + token side letter.** For an early (often US-incorporated)
  company: equity on the standard YC post-money SAFE, token upside via a side
  letter defining a pro-rata share of the team / contributor allocation. Reach
  for this pre-TGE when tokenomics are open.
- **Convertible note or bond + token warrant.** For a team wanting debt seniority
  on the equity leg: a note or bond converting to equity at a pre-money valuation
  with a discount, plus a warrant delivering the token allocation at TGE, with the
  equity-to-token exposure reconciled (sometimes by a fixed ratio). Reach for this
  when the token is still months out.
- **Token warrant (standalone, stapled to an investment agreement).** Where the
  warrant defines the allocation as Investment Amount divided by a set token
  price, with a lockup (for example 18 months) from Token Launch. Reach for this
  as the token leg when you want an enforceable, defined allocation, especially
  for a US developer company.
- **Term sheet, then TPA, then side letter (at-or-near-TGE sale).** For a direct
  token sale by an issuer alongside institutional co-leads: a non-binding term
  sheet sets reference price, supply, vesting (for example six-month lockup then
  linear vesting), anti-dilution, tokenomics-change consent, information rights,
  and any legal-opinion covenant; the TPA executes the sale; a side letter adds
  lead rights (ROFR on the next project, ROFO / pro-rata, advisory tokens, a
  market-making token loan). Reach for this at TGE.
- **Advisor agreement + advisor token grant.** Where a principal advises a
  portfolio company and takes a separate advisor token allocation with long
  vesting.
- **Platform ToS or program participation agreement + escrow / forfeiture.** For
  a platform holding user assets or a program (accelerator, residency, hackathon,
  bounty, grant, launchpad) with milestone escrow, reward vesting, or clawback:
  pair a Terms of Service or participation agreement with an escrow mechanism
  (agent, multisig, or smart contract) and forfeiture drafted as a condition on a
  primary right rather than a penalty on breach. Reach for this for anything
  post-raise or user-facing that holds value or imposes a loss condition. Full
  guidance and a fill-in template are in `escrow-forfeiture.md` and
  `../assets/tos-escrow-forfeiture-template.md`.

## Review shortcuts

When reviewing an incoming agreement:
1. Identify which archetype above it most resembles and diff against that
   precedent; flag any term worse than what is normally accepted.
2. Compute the two legs (equity percentage, token percentage) and the break-even
   multiple versus any known IDO / trading price. If a large multiple is needed
   just to break even, push back on the reference price.
3. Confirm the correct entity is the counterparty for each leg, that governing law
   and arbitration seat match the entity, and that any issuer carries a
   legal-opinion covenant where local law requires it.
4. Confirm downside protection (refund on dissolution, liquidation priority,
   anti-dilution) is present and not weaker than the archetype.
5. List side letters and advisor allocations so nothing modifies the effective
   deal off the books.

## Customizing for your firm

This playbook is generic on purpose. A fund or studio can extend it with its own
house rules: standard check size and preferred instrument, a private precedent
library of executed deals to diff against, standing entity and jurisdiction
choices, and attribution or confidentiality conventions for external-facing memos.
Keep any confidential portfolio terms out of shared copies of the skill; strip a
prior counterparty's specifics before reusing a precedent for a new deal.
