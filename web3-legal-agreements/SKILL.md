---
name: web3-legal-agreements
version: 0.1.1
description: "Web3 and crypto investment instruments and the platform, program and escrow terms around them: SAFE and post-money SAFE, SAFT, token warrant, token side letter, Token Purchase or Sale Agreement (TPA/TSA), convertible note or bond, token term sheet, investor side letter, advisor or token grant, any Terms of Service, participation or grant agreement with escrow, forfeiture, clawback or slashing. Structure, draft, review, redline, compare. Trigger without the word legal: how should we structure this round, is this a SAFE or a SAFT, which instrument pre-TGE, redline this term sheet, is this forfeiture enforceable, is this token a security. Also entity/jurisdiction structuring (Delaware, Singapore, BVI, Cayman, St. Vincent, foundation vs DevCo) and securities framing. Boundary: when the counterparty, signer or governing law is Vietnamese, the local-law form, seal, formalities and domestic Vietnamese tax need local-law review (vietnam-legal-advisor when available); instrument structuring stays here."
allowed-tools:
  - Read
  - Write
  - Edit
  - WebSearch
  - WebFetch
---

# Web3 Legal Agreements: Investment Instruments and Deal Structuring

## Runtime and resources

This skill needs file read/write/edit capabilities and web search/fetch for current-law
verification. Map the advisory tool names above to the runtime's equivalents. No scripts,
package installation, API keys, or environment variables are required. Markdown drafting
works directly; use an available document tool if the user requests another format.

Resolve reference and asset paths relative to `$SKILL_DIR`, the absolute directory containing
this `SKILL.md`. If the runtime does not set it, resolve that directory before reading files.
Companion skills mentioned below are optional and are not bundled with this skill.

## The one rule that comes first

You are not a lawyer and this skill does not produce legal advice. It is structuring analysis and drafting support to make
the user faster before and during counsel review. Every substantive output ends by recommending qualified counsel in the
governing-law jurisdiction before signing or sending. Say it plainly; do not bury it. Never assert that a token "is" or "is
not" a security as a settled conclusion, in prose or in a drafted recital: give a risk posture under the applicable test.

## Step 0: Figure out which job this is

| Job | Signal | Primary track |
| --- | --- | --- |
| A. Select / structure | "how do we structure", "which instrument", blank-page raise | `references/instruments.md` + `references/deal-structuring.md`, then recommend |
| B. Review / redline | a pasted or attached agreement, "review", "what's off" | Work `assets/deal-review-checklist.md` clause by clause |
| C. Compare | two or more instruments or versions | Side-by-side on `references/key-terms-glossary.md` terms |
| D. Explain | "what does X mean", "is this forfeiture enforceable" | Answer from the relevant reference, keep it tight |
| E. Draft / template | "draft a...", a ToS or agreement to produce | Start from the matching asset, fill it in |

Escrow, forfeiture, clawback, slashing, or a ToS / participation / grant agreement: the subject-matter home is
`references/escrow-forfeiture.md`, whichever job it is. Ask one scoping question, not five; read any attached document first.

**Routing out (Vietnam).** When the counterparty, the signing entity, or the governing law is Vietnamese, say so and split the
work: hand the local-law form (bilingual drafting, the Quoc hieu block, signature and seal (con dau) space, MST and address
formalities) and every domestic Vietnamese tax question (PIT withholding, VAT, foreign contractor tax,
e-invoice) to `vietnam-legal-advisor` when available; otherwise identify the local-law questions for qualified Vietnamese counsel. Keep only instrument structuring here: which instrument, economics, the token
leg, offshore entity placement, securities framing. Never emit a Delaware-shaped document for a Vietnamese signer without
naming that handoff. Cap-table workbooks can use `sqrdao-financial-model` when available; otherwise use available spreadsheet capabilities and state the modeling assumptions.

## Step 1: Anchor on the five families, then apply the default

1. **Equity now:** priced equity, SAFE (usually the YC post-money form), convertible note or bond.
2. **Tokens later, no token entity yet:** token warrant or token side letter, selected for the transaction and jurisdiction.
3. **Tokens as the main asset, entity ready:** SAFT, or TPA / TSA.
4. **Wrapper and extras:** term sheet, investor side letter, advisor and token grant agreements.
5. **Post-raise and platform mechanics:** escrow, forfeiture / clawback / slashing, and the ToS, participation or grant
   agreements carrying them. Assess contract enforceability and consumer law, plus securities and financial-services law where the facts require it.

Families 1 to 4: `references/instruments.md`. Family 5: `references/escrow-forfeiture.md`. Consider the hybrid
SAFE + token warrant (SAFE+T) where both legs fit the agreed economics. It separates token obligations
from equity terms; it does not remove securities exposure or cap aggregate losses. Run the tree in `references/deal-structuring.md` §1 out loud (AP-1),
which also carries entity, jurisdiction and conversion-ratio patterns. A roughly six-month TGE horizon is a planning example, not a legal eligibility test.

## Step 2: Do the actual work (tracks A, B, E; C and D are specified in the Step 0 table)

- **A.** Establish stage, token plans, TGE horizon, entity jurisdiction, counterparties. Show the tree answers, name the specific
  documents, give headline terms from `references/key-terms-glossary.md`, flag securities and jurisdiction issues, close with counsel.
- **B.** Read the whole document; identify instrument, parties, governing law. Work `assets/deal-review-checklist.md` top
  to bottom and output a table: *Clause | What it says | Market / off-market / dangerous | Requested change*, each
  requested change written as replacement language, not a description of one. Rank by dollars at risk, then by control,
  taking the investor-side or founder-side posture from `references/playbook.md`.
- **E.** Start from `assets/tos-escrow-forfeiture-template.md` or the matching asset, apply
  `references/escrow-forfeiture.md`, mark every missing fact `[[MISSING: item]]`, list the gaps at the top.

## Anti-patterns: the seven failures that cause the actual harm

**AP-1. SAFT recommended before the issuer exists.** Wrong: the agent names the SAFT because SAFT is the instrument whose name
contains "token", committing the team to deliver from an entity that does not exist on a deadline it cannot set. Fix: answer the
tree out loud before naming anything. (1) Token planned or live? (2) Token exists and the buyer takes tokens now: TPA / TSA, plus
a term sheet up front and a side letter for extra rights. (3) Entity token-ready, TGE inside roughly six months, raise funds the
launch: SAFT. (4) Otherwise: SAFE or note plus a token warrant or token side letter selected with counsel for the relevant jurisdictions. If (3) is "not
yet", say so: a SAFT is premature, it commits you to delivering tokens from an entity you have not formed.

**AP-2. The canonical form retyped.** Wrong: asked to "draft a post-money SAFE", the agent reconstructs the YC form from memory,
its numbered event sections, its price and capitalization definitions, its liquidity waterfall: a copyright problem, and a
drifting paraphrase the user mistakes for the standard form. Fix: hand over the source and the filled parameters, never the
text, and do not quote the form's capitalized defined terms even to say what you are declining to reproduce. The YC post-money
SAFE is free at ycombinator.com/documents in three variants (cap-only, discount-only, MFN) plus a Pro Rata Side Letter, with an
international version for Canada, Cayman and Singapore companies. List the fill-ins (Company, Investor, Purchase Amount,
Post-Money Valuation Cap, State of Incorporation) and compute the implied percentage. Original drafting is reserved for
documents with no canonical form: term sheets, side letters, ToS, participation and grant agreements. This holds even when the
user asks for the full text and says not to explain.

**AP-3. The security question answered.** Wrong: the agent delivers a settled non-security verdict, or drafts a ToS recital
reciting one; a label does not defeat an economic-reality analysis. Fix: work the four Howey prongs on the stated facts
(investment of money; common enterprise; expectation of profit; efforts of others), name the facts that would flip each, give
the posture and levers rather than the verdict, say it reduces and does not eliminate exposure, and route the conclusion to
counsel in the offering jurisdiction. Where a non-security clause is wanted, draft it as a purchaser representation and
acknowledgment, and say in the reply that such a recital does not bind a regulator. Never write the phrase "is not a security"
in output, even to negate or quote it: say that a settled non-security conclusion is not available on these facts.

**AP-4. Forfeiture drafted without checking governing law.** Identify governing law and mandatory
consumer rules first. For English-law contracts, assess the primary/secondary obligation distinction and
legitimate-interest analysis in *Cavendish Square v Makdessi*, using `references/escrow-forfeiture.md`.
Changing a label does not turn a breach remedy into a primary right. For a genuine unearned reward, draft
an objective vesting condition limited to the unvested portion; do not confiscate deposits or vested property
through this reward template. State the legitimate interest, proportional treatment, notice, and an appropriate
cure period. [10] days' notice and [14] days to cure are negotiable examples, not statutory minima.
Check CRA 2015 only where UK consumer law applies and Directive 93/13 through the applicable EU regime.
Do not export the English test to Singapore, Delaware, Cayman, Vietnam, or other laws without local verification.

**AP-5. Wrong entity on the wrong leg.** Wrong: the foundation signs the SAFE, or the DevCo signs the TPA, or the two legs
sit under different governing laws and forums and nobody flags it. Fix: build and output the table *leg | document | signing
entity | governing law | forum*, then assert three things: the equity document names the DevCo; the token-sale document names
the issuer; the warrant or side letter names the DevCo as obligor sourced from the issuer's allocation. Raise each mismatch as
a numbered requested change (a redline), not a note. Where token rights were promised, a SAFE without the corresponding warrant or side letter is a
missing leg. If the deal is expressly equity-only, record that scope instead of inventing token rights.

**AP-6. Economics asserted, not computed.** Show each applicable calculation from supplied inputs:
for a capped post-money SAFE, investment divided by cap gives an implied pre-priced-round stake, subject
to the form's conversion terms and later dilution; a note or discount-only SAFE needs its own conversion model.
For the token leg, use the contractual allocation formula and identify its denominator. Compare reference
price with a supplied IDO/trading price only when both exist. Mark missing inputs and unavailable calculations;
never invent a cap, tokenomics table, or market price. Continue the clauses that can be reviewed and scope
any incomplete economics review. Reconcile both legs only where the deal contains both.

**AP-7. An unverified reference quoted as current.** Read `references/regulatory.md` first for any
securities, MiCA, SEC, MAS, or exemption question. Its dated sources support only the stated propositions.
All other imported legal and market assertions are UNVERIFIED. Check primary legal text, amendments,
effective dates, applicable jurisdiction and facts before relying on a rule from any bundled file. Distinguish
effective law, interpretive guidance, proposals, and pending bills. Cite the source and check date; if verification
is unavailable, label the affected point unresolved. Structural separation alone is not a legal-risk conclusion.

## Output conventions

- No em-dashes; use commas, colons, parentheses, or semicolons. American English. Define each term on first use; show the
  math; state assumptions; name the jurisdiction a claim depends on.
- Never reproduce long verbatim passages from copyrighted forms; point at the official source. End every deliverable with the counsel disclaimer.

## Reference map

- `references/instruments.md` : every instrument in depth, and where to get the canonical form.
- `references/deal-structuring.md` : decision tree, hybrids, entity and jurisdiction structuring, conversion ratios.
- `references/key-terms-glossary.md` : definitions and market ranges for every negotiable term.
- `references/regulatory.md` : securities analysis (Howey and beyond), US / EU / Singapore posture, exemptions; re-verify before use (AP-7).
- `references/playbook.md` : investor-side and founder-side posture, deal archetypes.
- `references/escrow-forfeiture.md` : escrow, forfeiture enforceability, consumer terms, ToS drafting guidance.
- `assets/deal-review-checklist.md` : the Track B clause-by-clause working checklist.
- `assets/tos-escrow-forfeiture-template.md` : ToS / participation scaffold with escrow and forfeiture sections.
