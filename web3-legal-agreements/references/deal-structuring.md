# Deal Structuring Reference

> UNVERIFIED except for specifically dated, cited propositions. Check current primary
> sources and transaction facts before relying on legal or market assertions.

The decision tree for picking an instrument, how the hybrid structures fit
together, and how to structure the entities and jurisdictions underneath them.

## Contents
1. The selection decision tree
2. Investor side vs founder side
3. Entity and jurisdiction structuring
4. The equity-to-token bridge and conversion ratios
5. Sequencing a round

---

## 1. The selection decision tree

Ask these questions in order. The first "yes" that fits usually settles the
instrument family.

1. **Is there any token, planned or live?**
   - No token, never: plain equity leg only (SAFE, note, or priced round). Stop.
   - Token planned or live: continue.

2. **Does a token exist or launch imminently, and will the buyer take tokens
   directly now?**
   - Yes: **Token Purchase Agreement / Token Sale Agreement** (often with a term
     sheet up front and a side letter for extra rights).
   - No: continue.

3. **Is the entity token-ready and is this raise specifically to fund the token
   launch, with a TGE on a defined horizon (roughly six months)?**
   - Yes: **SAFT** (pay now, tokens at TGE).
   - No: continue.

4. **Pre-TGE, token design still open, entity not yet token-ready?** Use an
   equity instrument plus a token leg:
   - Equity leg: **SAFE** (default) or **convertible note / bond** (if the
     investor or jurisdiction wants debt seniority and a maturity).
   - Token leg: **token warrant** or **token side letter**, depending on allocation
     certainty, flexibility, enforceability, and the jurisdictions involved.

**Candidate hybrid:** SAFE + token warrant (SAFE+T) separates equity terms and token
obligations. Select it only after checking the intended economics, entity capacity,
and counsel's transaction-specific analysis. It does not eliminate securities
exposure or establish a limit on aggregate losses. No market-share or adoption
trend is verified by this reference.

---

## 2. Investor side vs founder side

The instrument is the same; the posture differs.

- **As investor:** push for downside protection
  (cash-out or refund on dissolution, liquidation priority, anti-dilution),
  clarity on the token allocation basis, pro-rata and information rights, and a
  clean lockup that does not leave you last in line. Prefer a warrant over a
  side letter when you want an enforceable, defined allocation. See
  `playbook.md`.
- **As founder-side advisor:** protect runway and control (avoid stacking too
  many SAFEs, keep token commitments flexible pre-TGE, avoid fixed TGE dates you
  cannot hit, cap investor governance over tokenomics), while giving investors
  enough certainty to sign.

Always state which side you are optimizing for at the top of the analysis.

---

## 3. Entity and jurisdiction structuring

Crypto deals usually involve two entities: a development company (DevCo) that
holds the IP and employs the team, and a token issuer (a foundation or an
offshore company) that launches and distributes the token. Separate documents can clarify each entity's obligations;
separation alone does not shield either entity from legal exposure.

Common building blocks seen in practice:

- **Development company (equity leg):** an onshore operating entity where the
  team sits and the IP lives. Delaware C-corp is standard for US-linked
  companies and is what the YC SAFE assumes. Non-US DevCos appear as a Singapore
  Pte Ltd, a Finnish Oy, a Hong Kong Ltd, or an EU entity. The equity
  instrument (SAFE, note, bond) is signed by this entity.
- **Token issuer (token leg):** frequently an offshore company or a foundation
  in a token-friendly jurisdiction. Singapore (an appropriate locally recognized legal form), BVI,
  Cayman, and St. Vincent and the Grenadines are all common issuers. The SAFT or
  TPA is signed by this entity; the token warrant or side letter obliges the
  DevCo to arrange delivery from the issuer's allocation.
- **Investor vehicle:** the investor invests through its own entity. Keep the
  investing entity consistent across a portfolio for clean records, and make
  sure the counterparty on each document is the correct entity (DevCo for
  equity, issuer for the token sale).

Jurisdiction notes:
- The YC post-money SAFE has an international variant for Canada, Cayman, and
  Singapore companies, with an optional country side letter. Use that instead of
  forcing the Delaware form onto a non-US entity.
- For Singapore, investigate whether the Payment Services Act, Securities and
  Futures Act, or other rules apply to the token and activities, considering
  licensing, exemptions, and current law. Use `regulatory.md` and qualified
  Singapore counsel; do not assume every token activity falls under both Acts.
- Match the governing law and arbitration seat in the document to the entity and
  the parties. A token sale by a Singapore issuer typically uses Singapore law
  and a Singapore or SIAC arbitration seat.
- Do not improvise entity or tax structuring. Flag the structure and route it to
  qualified local counsel and a tax advisor.

---

## 4. The equity-to-token bridge and conversion ratios

In a note-plus-warrant deal, the investor's equity exposure and token exposure
have to be reconciled so they are not double-counting or leaving value on the
table. A worked pattern:

- A convertible note converts to equity at a pre-money valuation with a discount
  (say a $8M pre-money, 20 percent discount, plus accrued interest), producing an
  equity percentage.
- A token warrant then defines the investor's token allocation, sometimes as a
  fixed ratio of the equity stake (for example, equity converts to token warrant
  at a 3:2 ratio), or as Investment Amount divided by a set token price, or as a
  pro-rata proportion of the team/company token allocation.
- Sanity-check the two legs against the tokenomics: compute the investor's token
  count at TGE and the implied break-even multiple versus the IDO price. If the
  numbers imply the investor needs a large multiple just to break even, the
  terms are off.

When reviewing, always compute the investor's resulting equity percentage AND
token percentage explicitly, and confirm they are consistent with the term sheet
and the tokenomics table.

---

## 5. Sequencing a round

A typical sequence for a token round:
1. Term sheet (non-binding) to align on economics and key protections.
2. Definitive equity instrument (SAFE or note) signed by the DevCo.
3. Token leg (warrant or side letter) stapled to the equity instrument, or a
   SAFT / TPA signed by the issuer if the token is imminent.
4. Side letter(s) for lead or strategic investors (ROFR, ROFO, pro-rata,
   advisory tokens, MM loan, MFN).
5. Advisor / token grant agreements as needed.
6. At TGE: exercise of warrants, delivery under SAFTs/side letters, subject to
   lockup and vesting.

Keep a single source of truth for who holds what (equity percentage and token
percentage), which side letters modify the base terms, and what vests when.
