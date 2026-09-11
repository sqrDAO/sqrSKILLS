# Instruments Reference

> UNVERIFIED except for specifically dated, cited propositions. Check current primary
> sources and transaction facts before relying on legal or market assertions.

Deep dive on every instrument used in crypto fundraising. Each entry covers what
it is, the mechanics, when to use it, the key negotiable terms, the tradeoffs,
and where to get the canonical form. Read the entry for whichever instrument is
in play; you do not need to read the whole file.

## Contents
1. Post-money SAFE
2. Convertible note / convertible bond
3. Token warrant
4. Token side letter
5. SAFT (Simple Agreement for Future Tokens)
6. Token Purchase Agreement / Token Sale Agreement (TPA / TSA)
7. Term sheet
8. Investor side letter
9. Advisor agreement / token grant
10. How the equity leg and token leg get stapled together

---

## 1. Post-money SAFE

**What it is.** A SAFE provides contractual rights before an equity financing.
For a capped post-money SAFE, investment divided by cap gives implied ownership
before new priced-round money and related dilution, subject to the form's terms.
Liquidity and dissolution events have payout rules, not automatic equity conversion.

**Mechanics.** At equity financing, apply the actual form's share-price and
capitalization definitions. A share count is investment divided by the applicable
price; do not confuse that quotient with the price itself. Liquidity and dissolution
payouts remain subject to priority and available proceeds.

Source checked 2026-09-11: `https://www.ycombinator.com/safe` and its linked forms.
Use the applicable current form; these paragraphs are an explanation, not a substitute.

**Key terms.** Post-money valuation cap; discount; MFN (most favored nation);
pro-rata rights (removed as a default in the post-money form, restored via a
separate Pro Rata Side Letter). See `key-terms-glossary.md`.

**When to use.** Any early equity raise where a token is not the point, or as
the equity leg of a hybrid token deal. Choose the cap, discount, or MFN variant based on the agreed terms.

**Tradeoffs.** Founder-simple, fast, no repayment obligation. Post-money caps
are quietly more dilutive to founders than pre-money because each SAFE holder's
percentage is locked. Stacking too many SAFEs can create a nasty surprise at the
Series A cap table.

**Canonical form.** Y Combinator publishes the official forms free at
ycombinator.com/documents (three variants: cap-only, discount-only, MFN, plus a
Pro Rata Side Letter). YC also publishes an international post-money SAFE
adapted for companies formed in Canada, Cayman, and Singapore, each with an
optional country side letter. Cooley GO has a free generator for customized YC
SAFEs including UK and Singapore adaptations. Do not paste the form text into
outputs; link to the source and describe the mechanics.

---

## 2. Convertible note / convertible bond

**What it is.** A loan that converts into equity on a trigger event. Unlike a
SAFE, it carries interest and a maturity date, and it is debt until it converts.
"Convertible bond" is the same idea under a civil-law or non-US corporate regime
(for example a Finnish capital loan under the Limited Liability Companies Act).

**Mechanics.**
- Principal accrues interest (commonly 5 to 8 percent) until conversion or
  maturity.
- Automatic conversion on a qualifying financing (for example, when the company
  raises a defined minimum in its seed round), typically at a pre-money
  valuation with a discount (commonly 20 percent) to the round price. Accrued
  interest usually converts alongside the principal.
- The issuer may retain a right to repay before conversion (cancelling the
  conversion right), and there are provisions for partial conversion and for
  the holder joining the shareholders agreement on conversion.

**Key terms.** Principal; interest rate; maturity; conversion valuation
(pre-money) and discount; automatic vs optional conversion trigger; repayment
right; transfer restrictions.

**When to use.** When the investor or jurisdiction prefers a debt instrument
with downside seniority and a defined maturity, or where local company law makes
a bond cleaner than a SAFE. In crypto, the note or bond frequently sits under a
token warrant: the note converts to equity, the warrant delivers the token
upside (see section 10).

**Tradeoffs.** More investor protection than a SAFE (interest, maturity,
seniority) at the cost of more complexity and a real repayment obligation on the
books.

---

## 3. Token warrant

**What it is.** A right (not an obligation) for the investor to acquire a defined
allocation of future tokens, usually at a nominal or zero exercise price,
exercisable at or after the Token Generation Event (TGE). It can be used as the token leg alongside an equity instrument.

**Mechanics.**
- Issued in connection with an equity investment (a SAFE, note, or investment
  agreement). The warrant references that instrument.
- The holder's token allocation is defined either as a fixed formula (Investment
  Amount divided by a set token price) or as a pro-rata proportion of the
  founders' or company's token allocation, calculated on a fully diluted,
  as-converted basis.
- Exercise price is often USD 0 or nominal. Exercise happens via an Exercise
  Notice around the TGE.
- A lockup period (commonly 12 to 18 months from Token Launch) plus a vesting
  schedule governs release.

**Key terms.** Token allocation basis (fixed price vs pro-rata proportion);
exercise price; exercise window; lockup; vesting; transfer restrictions;
definition of Token Launch / TGE.

**When to use.** Pre-TGE, when a token is planned but not yet issuable, and
where the proposed warrant terms fit the transaction and jurisdiction.
Document its relationship to the equity instrument.

**Tradeoffs.** Deferred token delivery does not cap total losses at the warrant cost.
Assess bundled consideration, exercise obligations, and the actual delivery covenants. More
drafting than a side letter. Guard against warrant holders disrupting circulating
supply at launch.

---

## 4. Token side letter

**What it is.** A contractual promise that the investor will receive a pro-rata
token allocation if and when a token is launched, entered in connection with a
convertible equity instrument (a SAFE or note). It is lighter and vaguer than a
warrant by design.

**Mechanics.**
- Ties the investor's token entitlement to their pro-rata share of the company's
  or contributors' token allocation, computed from the shares they hold
  (including as-converted convertible instruments).
- Typically does not fix a hard token cap, a fixed date for the TGE, or final
  tokenomics. That vagueness is the feature: it lets the team keep designing the
  token.
- The developer company carries the obligation to deliver or arrange delivery of
  the tokens once a token entity launches them.

**Key terms.** Pro-rata formula and worked examples; definition of "Company's or
Contributors' Allocation"; transfer restrictions; most-favored-terms provisions
if another token instrument (SAFT, TPA) is later signed with better terms.

**When to use.** Very early, while tokenomics are unfinished, if a contractual allocation
promise fits the agreed economics. Compare with a warrant under the actual
jurisdictions and facts; non-US incorporation is not a safety conclusion.

**Tradeoffs.** Fast and flexible, but the looseness cuts both ways: fewer hard
commitments for the investor to rely on, and the delivery mechanics depend on a
future token entity that may not exist yet.

---

## 5. SAFT (Simple Agreement for Future Tokens)

**What it is.** The investor pays now for the right to receive a set number of
future tokens at the TGE. Modeled on the SAFE but for tokens. Best suited to a
project that is raising specifically to fund a token launch and already has an
entity capable of issuing.

**Mechanics.**
- Purchase Amount and token economics are set in an exhibit (token price,
  number of Future Tokens, or a formula).
- The company commits to use commercially reasonable efforts to reach the TGE
  within a defined window (for example six months), at which point tokens are
  created and delivered.
- Conditions precedent to delivery (compliance with law, accurate reps and
  warranties on both sides).
- A Dissolution Event triggers a refund of the Purchase Amount (often 100
  percent less taxes and expenses).

**Key terms.** Purchase Amount; token price / valuation; TGE deadline; delivery
conditions; lockup and vesting; refund on dissolution; applicable-test risk analysis, fact-supported purchaser representations
that do not bind regulators, and the legal-opinion requirement.

**When to use.** Entity is token-ready, the raise is a token raise, and the TGE
is on a defined horizon. Less appropriate when the token design is still open
(use a warrant or side letter then).

**Tradeoffs.** Clean when the token is the actual product being sold, but it
carries the most direct securities risk of the token instruments because the
investor pays cash for a future token with an expectation of profit. Representations and legal opinions do not eliminate exposure. See `regulatory.md`.

---

## 6. Token Purchase Agreement / Token Sale Agreement (TPA / TSA)

**What it is.** A direct sale of tokens: the buyer pays and tokens are issued at
or near signing (subject to lockup and vesting), rather than the deferred
delivery of a SAFT. Used at or close to the TGE.

**Mechanics.**
- Defines the token, the network, total supply, reference price per token,
  accepted consideration (commonly USDC / USDT), and the buyer's allocation.
- Heavy on disclaimers and risk factors, fact-supported purchaser representations and acknowledgments
  under the applicable test, and a dispute-resolution clause. Representations do
  not bind regulators; retain any legal-opinion covenant and residual-risk warning.
- Full definitions, reps and warranties, tokenomics-change consent rights,
  vesting (for example six-month lockup then linear monthly vesting over 24
  months), and information rights.

**Key terms.** Reference price per token; purchase amount; total token supply and
tokenomics schedule; vesting and lockup; anti-dilution / tokenomics-upgrade
pro-rata; consideration; governing law and arbitration seat.

**When to use.** The token exists or launches imminently and the buyer takes it
directly. Often paired with a term sheet up front and a side letter for extra
rights.

**Tradeoffs.** Most concrete of the token instruments (real tokens, real price),
but also the most exposed to securities and money-transmission analysis in the
jurisdiction of sale. Requires the issuer entity to be properly structured.

---

## 7. Term sheet

**What it is.** A short, non-binding statement of the principal terms of a
proposed deal, executed before the definitive agreements. Creates no legally
binding obligation to invest (except usually confidentiality and exclusivity if
included).

**Mechanics.** Summarizes parties, instrument type, amount, price (valuation cap
or reference price per token), token supply and tokenomics, vesting, and the
key protective terms to be carried into the definitive documents. States
explicitly that it is an expression of intent only.

**Key terms for a token term sheet.** Company and founders; investors and lead;
advisors and advisor token allocation; total purchase amount; reference price
per token; total token supply; vesting schedule; tokenomics-change consent;
representations, warranties and covenants (including a legal-opinion undertaking
on local licensing); indemnity; anti-dilution protection; information rights;
refund on dissolution.

**When to use.** At the front of any non-trivial round to align on economics and
key protections before spending on definitive drafting.

**Tradeoffs.** Non-binding, so leverage still shifts during definitive drafting;
but it front-loads the negotiation of the terms that actually matter and reduces
wasted legal spend.

---

## 8. Investor side letter

**What it is.** A separate agreement granting a specific investor rights on top
of the standard instrument, used to give a lead or strategic investor extra
protection without changing the base document for everyone.

**Common provisions.** Right of first refusal (ROFR) over the founder's next
project or token; right of first offer / pro-rata to maintain ownership in
future rounds; advisory token allocation with its own lockup and vesting;
market-making token loan (documented separately); mutual consent on tokenomics
and token operations; MFN. Governing law and assignment (usually assignable only
to affiliates without consent).

**When to use.** For a lead or strategic check that expects rights beyond the
standard terms. Track which side letters exist: they modify the effective deal
and must be reflected on the cap table and in the data room.

---

## 9. Advisor agreement / token grant

**What it is.** Compensation for advisory services, in equity or (in crypto)
tokens. The YC-style advisor agreement covers services, compensation, term and
termination, confidentiality, IP ownership, and independent-contractor status.
Token grants add allocation, lockup, and vesting (advisor token vesting often
runs long, for example 48 months, with a lockup).

**When to use.** When a person (including a fund's principals) advises a
portfolio company and receives an allocation. Keep advisor tokens in a separate
allocation so they do not reduce the team or investor pools, and confirm the
services are genuine to support the tax and securities characterization.

---

## 10. How the equity leg and token leg get stapled together

Real deals combine instruments. The common patterns:

- **SAFE + token side letter.** Equity via the SAFE; token upside via the side
  letter's pro-rata formula. Consider pre-TGE where the terms fit the jurisdiction and transaction.
- **SAFE / note + token warrant.** A possible hybrid (SAFE+T).
  Equity converts on a priced round; the warrant delivers a defined or pro-rata
  token allocation at TGE under its conditions. Neither leg is insulated from securities analysis.
- **Convertible note / bond + token warrant.** The note converts to equity at a
  pre-money valuation with a discount; the warrant then converts equity exposure
  into a token allocation, sometimes at a fixed ratio (for example, equity
  converts to token warrant at a 3:2 ratio). Useful when a debt instrument is
  preferred for the equity leg.
- **Term sheet, then TPA / TSA, then side letter.** For an at-or-near-TGE token
  sale: the term sheet aligns economics, the TPA does the sale, the side letter
  adds lead-investor rights.

When you see one leg, ask where the other leg is. If token rights were promised, a SAFE with no token document
is a gap; an expressly equity-only deal need not grant token rights; a token warrant with no equity instrument is
unusual. Reconcile the two legs so the investor's total economics (percentage of
equity and percentage of tokens) are internally consistent.
