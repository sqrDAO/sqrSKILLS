# Escrow, Forfeiture, and Platform / Program Terms Reference

> UNVERIFIED except for specifically dated, cited propositions. Check current primary
> sources and transaction facts before relying on legal or market assertions.

Covers three related things the investment instruments do not: how value is held
in escrow and released, when a forfeiture actually sticks, and how to draft or
review the platform and program terms (Terms of Service, participation
agreements, grant agreements) that carry these mechanics. Read this whenever a
request involves escrow, forfeiture, clawback, slashing, deposit or reward
loss, or a ToS / participation / grant document. This is structuring and drafting
support, not legal advice; forfeiture enforceability turns on jurisdiction and
facts, so route the conclusion to counsel.

## Contents
1. When this module applies
2. Escrow structures and release mechanics
3. Forfeiture: what it is and when it is enforceable
4. Terms of Service and program / participation terms
5. Drafting guidance: making escrow and forfeiture hold up
6. Where to go next

---

## 1. When this module applies

Reach here for: milestone or vesting escrow, deposit or stake forfeiture,
unclaimed-reward or airdrop expiry, staking slashing, grant clawback, launchpad
or IDO allocation forfeiture, program-participation terms (accelerator,
residency, hackathon, bounty), and any platform Terms of Service that holds user
funds or imposes a loss condition. The governing legal question is usually contract enforceability (the penalty and forfeiture
doctrines) plus, for anything consumer-facing, unfair-terms and transparency law.

---

## 2. Escrow structures and release mechanics

Escrow holds an asset for a party until defined conditions are met, then releases
or refunds. Three structures dominate in Web3:

- **Escrow-agent (custodial).** A named third party (law firm, licensed escrow
  provider, or platform operator) holds fiat or crypto and releases on
  instruction or verification. Simplest to enforce off-chain; introduces
  counterparty and licensing risk, and often KYC.
- **Multi-signature wallet.** Funds sit in a wallet requiring m-of-n signatures
  (for example buyer, seller, and an arbiter) to move. Trust is spread across
  signers rather than one agent.
- **Smart-contract escrow (non-custodial).** Code locks the asset and releases
  it when on-chain or oracle-verified conditions are satisfied. Trust-minimizing
  and 24/7, but only as good as the audited code, and off-chain facts still need
  an attestation or oracle to enter the contract.

Release-condition patterns (name which one applies):
- **Milestone / deliverable:** release in tranches as defined deliverables are
  confirmed. Model it as a state machine (created, funded, released) per tranche.
- **Time-lock:** release on a date or after a duration (vesting, lockup expiry).
- **Oracle / external data:** release when a trusted data feed confirms an event.
- **Mutual approval / confirmation:** release when both parties (or the arbiter)
  sign off.

Every escrow needs, and every review should check: who holds the asset and under
what authority; the exact release and refund triggers (objective and verifiable,
not vague); a dispute and fallback path (arbiter, multisig, timeout to refund,
or a decentralized arbitration protocol) so funds are never locked forever; fees
and who bears them; whether assets are segregated or commingled; and, for a
custodial holder, any money-transmission or escrow-licensing exposure in the
holder's jurisdiction. On-chain escrow adds: audit status of the contract,
upgrade or admin keys (who can move funds outside the rules), and the oracle
trust assumption.

---

## 3. Forfeiture: what it is and when it is enforceable

Forfeiture is the loss of a deposit, stake, allocation, or unvested asset on a
defined trigger (a leaver event, a missed milestone, a rule breach, an expiry).
Whether it is enforceable is the crux, and the answer differs by whether the
counterparty is a business or a consumer and by governing law.

### The primary vs secondary obligation distinction (the drafting lever)

Under English law, the penalty doctrine applies on a **secondary** obligation, meaning a
consequence imposed for **breach** of contract. A term that adjusts the primary
bargain (a conditional right, a price adjustment, or a benefit that was never
earned unless a condition is met) is generally outside the doctrine. So a
forfeiture drafted as "the asset only vests / is only earned if X occurs" (a
condition on a primary right) is far more robust than "on breach, you forfeit"
(a penalty on breach). This distinction is the single most important drafting
lever.

### English law; verify other jurisdictions independently

The modern test comes from Cavendish Square Holding BV v Makdessi (2015), which
replaced the old Dunlop "genuine pre-estimate of loss" test. A clause triggered
by breach is an unenforceable penalty if the detriment it imposes is out of all
proportion to the innocent party's **legitimate interest** in enforcing the
primary obligation, that is, if it is extravagant, exorbitant, or unconscionable.
Key points:
- The legitimate interest can be non-monetary (protecting goodwill, a program's
  integrity, a network's health), not just a pre-estimate of loss.
- Freely negotiated bargains between advised commercial parties of comparable
  bargaining power are usually upheld.
- Even a valid forfeiture may face **relief against forfeiture**, an equitable
  power to excuse the loss, but courts exercise it sparingly in commercial cases.

### United States

Broadly parallel: a liquidated-damages or forfeiture provision must be a
reasonable measure tied to the harm or the legitimate interest, not a punitive
penalty. Grossly disproportionate forfeitures risk being struck as penalties, and
some contexts add statutory or equitable limits. Confirm the specific state law.

### Consumer contracts (where the relevant regime applies)

If the counterparty is a consumer (most retail platform users), a second filter
applies on top of the penalty doctrine: unfair-terms law. Where applicable, under the UK Consumer
Rights Act 2015 or the relevant national implementation of EU Directive 93/13, a term is not binding
if, contrary to good faith, it causes a significant imbalance in the parties'
rights to the consumer's detriment; terms must also be transparent and, where
relevant, prominent. ParkingEye v Beavis (2015) shows a charge can survive both
filters if it serves a genuine, clearly-disclosed legitimate interest and is not
concealed or excessive. The practical lesson: consumer-facing forfeitures must be
proportionate, plainly disclosed, and prominently presented, or they fall even if
they would pass the commercial penalty test. MiCA and local consumer regimes add
disclosure duties for EU-facing crypto services.

---

## 4. Terms of Service and program / participation terms

A Terms of Service (ToS) is a platform-to-user or program-to-participant
agreement, a different genre from an investor instrument. Escrow and forfeiture
show up in a ToS as: unclaimed or expiring rewards and airdrops, staking and
slashing, deposit or performance-bond forfeiture, launchpad or allocation
forfeiture on failed KYC or missed windows, and grant or milestone clawbacks in
accelerator, residency, hackathon, or bounty programs.

What a ToS with these mechanics must get right:
- **Acceptance and incorporation.** Clear affirmative acceptance (not buried
  browsewrap), and any incorporated documents (escrow terms, program rules,
  privacy policy) referenced and accessible.
- **Consumer vs B2B classification.** Decide whether users are consumers; if so,
  the stricter unfair-terms and transparency rules apply and the drafting must
  meet them.
- **Escrow / custody terms.** Who holds user assets, the release and refund
  rules, dispute path, and any custody or money-transmission licensing.
- **Forfeiture terms.** Drafted as conditional rights where possible (see section
  5), proportionate, and tied to a stated legitimate interest.
- **Notice, cure, and change control.** How users are told of forfeiture events,
  whether there is a cure period, and how the ToS itself can be amended.
- **Governing law, dispute resolution, and any arbitration or class-action
  waiver**, matched to the operator's entity and enforceable in the users'
  jurisdictions.
- **Regulatory overlays.** Consumer protection, data protection, AML/KYC, and
  (for token rewards) the securities and MiCA framing from `regulatory.md`.

---

## 5. Drafting guidance: making escrow and forfeiture hold up

When drafting or redlining, apply these to maximize enforceability:

1. **Frame forfeiture as a condition on a primary right, not a penalty for
   breach.** "Tokens vest only upon X and are otherwise not earned" beats "on
   breach you forfeit your tokens." This is the strongest single move.
2. **Anchor to a stated legitimate interest.** Spell out why the forfeiture
   exists (protecting other participants, network integrity, program fairness),
   so a court can see the commercial purpose.
3. **Keep it proportionate.** Avoid all-or-nothing forfeiture where a graduated
   or pro-rata loss would serve the interest; extravagant or punitive losses are
   the ones that get struck.
4. **Be transparent and prominent, especially for consumers.** Plain language,
   surfaced at the point of acceptance, not concealed in a long ToS.
5. **Give notice and, where fair, a cure period** before forfeiture triggers.
6. **Make escrow release conditions objective and verifiable**, with a defined
   dispute path and a timeout-to-refund so funds are never trapped.
7. **Define every trigger term precisely** (leaver, breach, milestone, expiry,
   slashing event) and align on-chain logic with the written terms.
8. **Match governing law and forum** to the entity and the counterparties, and
   sanity-check enforceability in the jurisdictions where users actually sit.
9. **Route to counsel** for the final enforceability call, particularly the
   forfeiture clause and any consumer-facing terms.

---

## 6. Where to go next

- To review an escrow / forfeiture / ToS document, use the dedicated section of
  `../assets/deal-review-checklist.md`.
- To produce a first draft, start from
  `../assets/tos-escrow-forfeiture-template.md` and fill in the brackets.
- For securities and MiCA framing of token rewards, see `regulatory.md`.
- For the program / ToS archetype and reuse posture, see `playbook.md`.

### Sources to re-check (law evolves)
- Penalty doctrine: Cavendish Square Holding BV v Makdessi; ParkingEye v Beavis
  (UK Supreme Court, 2015); Dunlop (1915, superseded test).
- Relief against forfeiture: Shiloh Spinners; Cukurova line.
- Consumer unfair terms: UK Consumer Rights Act 2015 s62; EU Directive 93/13.
- Escrow: standard escrow-agent, multisig, and smart-contract patterns; confirm
  custody / money-transmission licensing in the holder's jurisdiction.

English-law source checked 2026-09-11: `https://www.supremecourt.uk/cases/uksc-2013-0280`
(*Cavendish*, judgment of 4 November 2015). Substance governs the distinction;
renaming a breach remedy does not determine the result. Do not assume this test
is the law of Singapore, Delaware, Cayman, Vietnam, or any other jurisdiction.
Assess securities and financial-services overlays for token-related terms too.
