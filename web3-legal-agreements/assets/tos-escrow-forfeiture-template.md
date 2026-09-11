# ToS / Participation Agreement Template: Escrow and Forfeiture (skeleton)

A neutral, fill-in skeleton for a platform Terms of Service or program
participation agreement that holds assets in escrow and imposes forfeiture. It is
a starting scaffold, not a finished contract and not legal advice. Fill every
[bracket], delete what does not apply, keep the drafting notes in mind, and have
counsel in the governing jurisdiction review before use, especially the
forfeiture and consumer-facing terms.

Drafting notes are marked `>> NOTE:` and should be removed from the final draft.

---

## 1. Parties and acceptance
- **Operator:** [legal entity name, number, jurisdiction, registered address].
- **User / Participant:** the person or entity accepting these terms.
- **Acceptance:** By [creating an account / depositing assets / entering the
  Program], you agree to these Terms and the documents incorporated by reference
  in Section 12.
>> NOTE: Use affirmative click-through acceptance, not passive browsewrap. If
users may be consumers, say so and meet the transparency and prominence duties.

## 2. Definitions
Define precisely: "Assets", "Deposit", "Escrow", "Escrow Agent / Contract",
"Release Conditions", "Milestone", "Forfeiture Event", "Leaver", "Program",
"Rewards", "Slashing", "TGE", "Vesting", "Cure Period".
>> NOTE: Every trigger word used later must be defined here and must match any
on-chain logic.

## 3. Escrow and custody of assets
3.1 **Holder and authority.** Assets are held by [Escrow Agent / the smart
contract at address 0x... / a [m]-of-[n] multisig] under the rules in this
Section.
3.2 **Deposit.** [What the User deposits, when, in what asset.]
3.3 **Release Conditions.** Assets are released to [recipient] only when [define
objective, verifiable conditions: milestone confirmation / time-lock / oracle
event / mutual approval].
3.4 **Refund.** If [Release Conditions fail / a timeout of [X] elapses], Assets
are returned to [the User], less [fees / taxes].
3.5 **Dispute and fallback.** Disputes over release are resolved by [arbiter /
multisig vote / decentralized arbitration]; if unresolved within [X], Assets
[refund to User / other]. Assets are never locked indefinitely.
3.6 **Segregation and fees.** Assets are [segregated / commingled]; escrow fees of
[amount] are borne by [party].
>> NOTE: If the Operator itself custodies user assets, check money-transmission
and escrow-licensing exposure in the Operator's jurisdiction.

## 4. Vesting, lockup, and earning of Assets
4.1 [Rewards / Tokens / Allocations] are **earned only upon** [condition], and
are **not earned** until then.
4.2 Vesting schedule: [TGE unlock %], [cliff], [linear period]. Lockup: [period]
from [start point].
>> NOTE: Framing value as "earned only upon a condition" (a primary right) is far
stronger than "forfeited on breach" (a penalty). Prefer 4.1's framing wherever
possible.

## 5. Forfeiture
5.1 **Forfeiture Events.** The following result in loss of [unvested Assets /
Deposit / allocation]: [list precisely].
5.2 **Legitimate interest.** This forfeiture exists to [protect other
participants / preserve network or program integrity / ensure fair allocation];
it is not a penalty and is proportionate to that interest.
5.3 **Proportionality.** Forfeiture is limited to [unvested / pro-rata / the
portion tied to the unmet condition], not the User's entire holding, except
[narrow, justified exceptions].
5.4 **Notice and cure.** Before forfeiture, the Operator will give [X days] notice
and, where applicable, a cure period of [X days].
>> NOTE: For consumer users, keep this clause plain, proportionate, and prominent,
or it risks being unfair and unenforceable.

## 6. Program participation terms (if applicable)
[Eligibility, obligations, milestones, grant or reward mechanics, clawback tied
to Section 5, IP and confidentiality, code of conduct.]

## 7. Representations and eligibility
[User authority, KYC/AML where required, sanctions, non-restricted jurisdiction,
own-account and risk acknowledgments for any token rewards.]

## 8. Risk disclosures and disclaimers
[Token/asset risk, no-investment-advice, non-security framing where supportable
(cross-check regulatory.md), technology and smart-contract risk, no warranty.]

## 9. Limitation of liability and indemnity
[Cap, carve-outs, indemnity, consumer-law carve-outs that cannot be excluded.]

## 10. Changes to these Terms
[How amendments are made and notified; when continued use equals acceptance;
consumer-fair change control.]

## 11. Governing law and dispute resolution
Governing law: [jurisdiction]. Disputes: [courts / arbitration seat and rules];
[class-action waiver if used and enforceable].
>> NOTE: Match to the Operator entity and confirm enforceability where users sit.

## 12. Incorporated documents
[Escrow terms, program rules, privacy policy, token terms], each accessible at
[links].

---
End the delivered draft with: this is a starting scaffold, not legal advice; have
qualified counsel in the governing jurisdiction review before use.
