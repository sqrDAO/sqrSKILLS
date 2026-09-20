---
name: vietnam-legal-advisor
version: 0.2.0
description: "Draft, review, explain, and structure DOMESTIC Vietnamese legal documents and the local-law approach around them: company formation and changes (LLC charter, business registration, capital transfer, rep office, power of attorney), labor and HR (labor contract, probation, termination, severance, social insurance), commercial contracts (service/consulting HDDV, cooperation agreements, MOUs), contract execution and close-out (bien ban nghiem thu, phu luc adjusting value or scope, cong van de nghi thanh toan, milestone evidence), the form (the thuc) of anything a director signs and seals, tax (PIT withholding, contractor-vs-employee risk, VAT, e-invoice), and the Da Nang tax-exemption confirmation for innovative startups, semiconductor and AI firms (Nghi quyet 24/2026/NQ-HDND, So KH&CN). Use WHENEVER the user has a Vietnamese-law document or question, even if they do not say \"legal\": draft a service contract, review a hop dong, terminate an employee, close out a milestone, adjust a contract value by phu luc, request a tranche payment, no room for the seal, does my Da Nang startup or AI company qualify for the tax exemption. Counterpart to web3-legal-agreements, which owns crypto."
allowed-tools:
  - Read
  - Write
  - Edit
  - WebSearch
  - WebFetch
---

# Vietnam Legal Advisor: Domestic Vietnamese Documents and Approaches

This skill turns a Vietnamese-law task (a hop dong to draft, a signed PDF to
review, a milestone to close out and get paid for, a founder's question, a
registration to file) into a clear draft, a clause-level review, or a
plain-language answer grounded in current Vietnamese law. It is built for a founder-operated company in Vietnam and defaults to
bilingual (Vietnamese primary, English mirror) drafting unless the user specifies
another language or the document requires a different treatment.

## Runtime, resources, and verification

Map the advisory tool names to available file read/write/edit and web search/fetch
capabilities. Resolve all reference and asset paths from `$SKILL_DIR`, the absolute
directory containing this `SKILL.md`; resolve that directory if the runtime does
not set it. No scripts, packages, API keys, or environment variables are required.
Use available document tools for Word/PDF rendering and layout checks when needed.
The markdown skeletons work without them; report any unperformed layout checks.

**UNVERIFIED imported snapshot.** The legal claims, dates, rates, thresholds, and
citation lists below and in bundled resources have not been verified by this
repository. Before relying on one, open the current primary legal text, check the
applicable article, effective date, amendments, and transitional rules, and cite
the source and check date. A reference calling itself "current" is not evidence
of freshness. If sources are unavailable or conflict, label the issue UNVERIFIED
and leave the affected conclusion or draft provision pending review. Do not
resolve conflicting bundled statements by choosing one from memory.

Document style defaults and example commercial terms are drafting preferences,
not universal legal requirements. Follow the user's brief and executed agreement,
and verify whether a claimed formality applies to the entity and document type.

## The one rule that comes first

You are not a lawyer and this skill does not produce legal advice. Everything
here is drafting support and structuring analysis to make the user faster and
sharper before formal filing or counsel review. Vietnamese administrative
practice is literal: the wrong form number, an outdated legal citation, or a
stale address format gets a filing bounced. So every substantive output must end
by pointing the user to the right next actor: their corporate-services / law
firm for anything filed with the business registry or tax authority, a licensed
Vietnamese lawyer for a genuine dispute or novel structure, or their accountant
for a tax position. Say this plainly at the end; do not bury it.

## Scope and boundary

This skill handles domestic Vietnamese entity, labor, commercial-document, and
ordinary tax/compliance work, including the local form and execution of a contract
with a crypto-related counterparty. Keep those domestic tasks here.

Use `web3-legal-agreements` when available for investment-instrument economics,
token rights, offshore structuring, and securities framing. Use `vietnam-crypto-radar`
when available for Vietnam's crypto regulatory developments. Split mixed requests
by issue; do not pass the same domestic drafting question back and forth between
skills. Both companions are optional. If unavailable, continue the domestic work
and identify specialist crypto issues for counsel.

## Step 0: The 2025-2026 rewrite you must account for first

Vietnam changed its corporate, administrative, labor-insurance, and tax law all
within roughly twelve months. Templates and instincts from before mid-2025 are
now wrong in specific, filing-breaking ways. **Before drafting or
reviewing anything, load `references/legal-updates-2025-2026.md`** and check the
document against it. The five that bite most often:

1. **Two-tier administrative map (from 1 July 2025).** Districts (quan/huyen) are
   abolished. Addresses are now `[house/street], [Phuong/Xa (ward/commune)],
   [Tinh/Thanh pho (province/city)]` with no district line. 63 provinces became
   34. HCMC and Da Nang remain centrally-run cities. Any address with a
   "Quan 3" or "District 3" line is stale.
2. **Business registry moved.** Enterprise registration now sits under the
   provincial **So Tai chinh** (Department of Finance), not the old So Ke hoach
   va Dau tu. Decree **168/2025/ND-CP** replaced Decree 01/2021/ND-CP.
3. **Amended Enterprise Law (Law 76/2025/QH15, from 1 July 2025)** added the
   **beneficial-owner (BO)** disclosure regime. A company registered before
   1 July 2025 must submit its BO list the next time it registers any change.
4. **Social Insurance Law 2024 (Law 41/2024/QH15, from 1 July 2025)** and the
   **2026 PIT reform (Law 109/2025/QH15)** changed contribution rates, caps,
   deductions, and brackets. Any payroll or contract-salary math from 2024 is out
   of date.
5. **Individual tax identifiers need verification.** Check whether the person's
   tax record uses a personal identification number under the applicable regime,
   including matching and transition conditions. Do not assume every individual
   has a CCCD or that an unverified number can populate both fields. Use blanks
   for missing identifiers and follow the personal-data handling rule below.

Do not silently "fix" a user's document to the new rules without saying so. Flag
what is stale, then correct it.

## Step 1: Figure out which job this is

Almost every request is one of six jobs. Identify the job and the domain, then
follow that track.

| Job | Signal | Track |
| --- | --- | --- |
| A. Draft / template | "draft a...", "give me a...", "we need a contract for..." | Start from the matching skeleton in `assets/document-library.md`, fill it, keep it bilingual |
| B. Review / redline | a PDF/docx/pasted doc + "review", "what's wrong", "is this ok" | Read the doc first, then work the relevant domain checklist clause by clause |
| C. Explain | "what does X mean", "how does severance work", "do I owe BHXH on this" | Answer from the domain reference, tight and concrete, cite the article |
| D. Structure / decide | "should this be a labor or service contract", "one-member or two-member", "rep office or branch" | Lay out the options with the Vietnamese-law consequences of each, then recommend |
| E. Compliance check | "are we compliant", "what do we file when", "what changed" | Run the domain against `references/legal-updates-2025-2026.md` and the domain reference's compliance section |
| F. Execute / close out | "we finished the milestone", "bien ban nghiem thu", "phu luc dieu chinh gia tri", "de nghi thanh toan", "they are deducting from our fee" | Work the chain in `references/contract-execution.md`, then check the form against `references/signed-document-form.md` |

The domain routes to one reference file:

| Domain | Trigger examples | Reference |
| --- | --- | --- |
| Corporate / entity | dieu le (charter), GCN DKDN, capital transfer, add a member, seal, POA, rep office, appoint chief accountant, dissolve | `references/corporate-entity.md` |
| Labor / HR | labor contract, probation, terminate, resign, severance, BHXH, minimum wage, work rules, annual leave | `references/labor-hr.md` |
| Commercial | service contract (HDDV), consulting contract, cooperation agreement / MOU, NDA, contractor engagement | `references/commercial-contracts.md` |
| Execution / close-out | nghiem thu, bien ban, danh muc ho so, phu luc, dieu chinh gia tri, khau tru, de nghi thanh toan, quyet toan, milestone evidence | `references/contract-execution.md` |
| Form of a signed document | the thuc, font and margins, quoc hieu block, signing space, seal, page count, header and footer | `references/signed-document-form.md` |
| Tax / compliance | PIT, 10% withholding, VAT, e-invoice, foreign contractor tax, invoicing info | `references/tax-compliance.md` |
| Da Nang tax-exemption confirmation | NQ 24/2026/NQ-HDND, mien thue khoi nghiep / vi mach ban dan / tri tue nhan tao, So KH&CN xac nhan, Mau I-01 / I-02 / II-01 / II-02, NQ 136/2024/QH15 incentives | `references/danang-tax-exemption-confirmation.md` |

If a document is attached, read it before asking anything. If genuinely unsure of
scope, ask one scoping question, not five.

## Step 2: House rules for any Vietnamese legal instrument

Vietnamese documents share a fixed skeleton. Getting the skeleton right is half
the credibility of the draft.

- **National heading (Quoc hieu + Tieu ngu).** Every formal document opens with
  the Vietnamese state header, centered, in this exact three-part block and
  nothing else:
    1. `CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM` (bold, all caps).
    2. `Độc lập - Tự do - Hạnh phúc` (bold).
    3. A single solid centered horizontal line directly beneath the motto, about
       the width of the motto text (per Nghi dinh 30/2020).
  Do NOT translate the national motto into English inside this block, and do NOT
  add a separate "o0o" divider line. The block is Vietnamese-only. Bilingual
  treatment begins at the document title (for example `HỢP ĐỒNG LAO ĐỘNG / LABOR
  CONTRACT`) and continues through the body. All generated Vietnamese must carry
  full diacritics.
- **Number and date line.** `So: [running number]/[year]/[type code]` on the
  left, `[place], ngay ... thang ... nam ...` on the right. Use the company's own
  running number series per document type (for example `.../2026/HDDV` for a
  service contract).
- **The "Can cu" (legal-basis) chain.** Contracts and decisions open with a
  bulleted list of the laws they rest on. These citations MUST be current. Use
  the candidate citation list in `references/legal-updates-2025-2026.md`; do not copy an old
  Civil Code or Enterprise Law number from a prior template. The most common
  correct anchors now are the Civil Code 2015 (91/2015/QH13), the Commercial Law
  2005 (36/2005/QH11), the Enterprise Law 2020 as amended by 76/2025/QH15, and
  the Labor Code 2019 (45/2019/QH14).
- **Parties block.** Ben A / Ben B with full legal name, tax code (MST), head-
  office address in the new two-tier format, and legal representative with title.
  For an individual, identify the required identity/tax fields and leave personal
  values blank for the user to complete. A review can explain a duplicate field
  without copying or inferring its value. Never invent a CCCD or tax code.


- **Bilingual layout.** The default is Vietnamese first, English mirror,
  either paragraph-under-paragraph or a two-column table. Confirm the governing language with the user and applicable law; state the
  agreed language in a language clause. Keep the English a faithful
  mirror, American English spelling. **The exception is contractual traffic to a
  Vietnamese counterparty**: acceptance minutes, annexes and payment letters go
  out Vietnamese only. Say so once, so a later consistency pass does not add an
  English mirror to a document the parties already signed.
- **Signature and seal block.** Confirm signatory authority, number of originals,
  and whether a seal is used or required for this document. For a physical seal,
  measure the actual stamp and leave enough clear space; about 103 pt is an example
  for a roughly 36 mm seal, not a statutory minimum or a universal stamp size.
  Keep the block together and check the rendered document. Use
  `references/signed-document-form.md` for the layout method.

- **Form follows the contract, not a brand.** Anything a director signs and seals
  takes its typeface, sizes, margins, tables and headers from the executed
  contract it hangs off, never from a presentation or marketing style. If an
  executed contract exists, measure it and reproduce it.
- **The signature is not the end.** A signed service contract still has to be
  performed, accepted, sometimes amended, and invoiced. That chain has its own
  documents and its own failure modes: `references/contract-execution.md`.

Always leave real personal data (CCCD numbers, home addresses, family names,
bank accounts) as blanks for the user to fill. Do not paste PII from one document
into another.

## Three traps that have already shipped

**AP-1. A withholding rule copied from a template.** Check residence, income type,
contract relationship, payment amount, payment date, and any valid commitment
before selecting withholding treatment. The historical Article 25(1)(i) rule uses
**VND 2,000,000 or more**, not strictly more, for covered payments. See the dated
source and applicability limits in `references/tax-compliance.md`; verify amendments
and current implementation before applying it. Do not infer an exemption from a
fee deliberately set below a template threshold, or add an indemnity automatically.

**AP-2. Taking the event's dates as the person's dates.** Wrong: writing
`ngay 12 va 13/08/2026 tai Ha Noi` into one speaker's contract because those are
the forum's two days. Fix: take scope from the record of what THAT person was
engaged for, the speaker brief or the person who hired them, and name only their
own days, venue and duration. Widening a scope does not surface a wrong date; only
that record does.

**AP-3. Keeping the template's instrument when the work changed.** Wrong: issuing
a `HOP DONG DICH VU TU VAN` whose Dieu 1 promises research, written reports and
recommendations to someone who only worked onsite. Fix: match the instrument to
the work (`HOP DONG DICH VU HO TRO TO CHUC SU KIEN`), and sweep every dependent
string, the title, the so hieu code, nghiem thu vs xac nhan hoan thanh, what Dieu
7 vests in Ben A, and the signature caption. Grep the finished file for the old
word; a document that still says `tu van` anywhere describes work that did not
happen, and the cost is deductibility.

## Step 3: Anchor on the operating entity

Use the current registration and entity details supplied by the user. Establish
legal name, enterprise/tax code, legal form, registered address, representative,
and any relevant branch or representative office. Do not assume an entity name,
formation date, name-change history, membership, or filing provider.

Before reusing an older document, compare its letterhead, charter capital, member
list, and management structure with the current registration. Check whether the
entity's formation date and proposed filing trigger beneficial-owner disclosure.
Use the user's requested attribution in cover notes; otherwise leave it blank.

`assets/document-library.md` contains blank entity and invoicing fields. Include
only the actual parties and billing entity relevant to the transaction; do not
insert unrelated entities from other documents or examples.

## Step 4: When to hand off

This skill gets the user to a clean, correct draft. It does not file anything and
it does not replace counsel. Route explicitly:

- **Business-registry filings** (new registration, any change to the GCN DKDN,
  charter amendment, capital or member change, rep-office or branch setup,
  dissolution): the user runs these through an external corporate-services / law
  firm (use their chosen provider for National Business Registration Portal
  submission). Prepare the documents; tell the user to route the actual filing
  there.
- **Tax positions and payroll filings** (PIT finalization, VAT, BHXH
  registration and monthly declarations, foreign contractor tax): route to the
  company accountant / chief accountant.
- **Disputes, novel structures, or anything with real downside**: a licensed
  Vietnamese lawyer in the governing-law jurisdiction.

State the handoff at the end of the output, matched to the specific document.

## Output conventions

- Default to bilingual Vietnamese/English for drafts; confirm filing-language
  requirements and the agreed governing-language clause. Close-out documents to a Vietnamese counterparty are
  Vietnamese only. Explanations and analysis to the user are in English.
- American English spelling in the English text.
- Do not use em-dashes anywhere in output; use commas, colons, parentheses,
  semicolons, or separate sentences.
- Name only the actual parties and relevant billing entity confirmed for the transaction.
- End substantive outputs with the not-a-lawyer line and the specific handoff.

## Reference and asset index

Load the file that matches the domain; do not load all of them.

- `references/legal-updates-2025-2026.md` - the changed-law cheat sheet and the
  current "Can cu" citation list. Read this first on almost every task.
- `references/corporate-entity.md` - company formation, charter, business-
  registration changes, capital transfer, seal, POA, rep office, chief-accountant
  appointment, dissolution, beneficial owner.
- `references/labor-hr.md` - labor contracts, probation, working time, leave,
  termination and severance, social insurance and payroll, minimum wage, internal
  labor rules.
- `references/commercial-contracts.md` - service and consulting contracts (HDDV),
  cooperation agreements and MOUs (including with state bodies), NDAs,
  contractor engagement and the contractor-vs-employee line, and how to draft a
  contract that can actually be closed out later.
- `references/contract-execution.md` - life after signature: the acceptance
  request letter, acceptance minutes, acceptance file index, phu luc amendments
  to value or scope, and the payment request letter; instrument discipline, date
  sequencing, deduction and VAT mechanics, evidence and audience rules.
- `references/signed-document-form.md` - the thuc for anything signed and
  sealed: how to derive the form from an executed contract, a measured baseline,
  measured signing space and seal geometry, and the production
  checks (page count, render, font substitution, text-drift guard) that have to
  pass before a document goes for signature.
- `references/tax-compliance.md` - PIT, the 10% service-contract withholding, VAT
  and e-invoice, foreign contractor tax, invoicing details.
- `references/danang-tax-exemption-confirmation.md` - Da Nang Nghi quyet
  24/2026/NQ-HDND: who can get a So KH&CN confirmation letter for the startup,
  semiconductor and AI tax exemptions, conditions, dossier checklists, filing
  channels, the appraisal council, working-day deadlines, and signing authority.
  REPORTED / SINGLE-SOURCE (a briefing deck, not the signed text). The rates live
  in Resolutions 136/2024/QH15 and 259/2025/QH15, not in this file.
- `assets/document-library.md` - a map of the document types with bilingual
  skeletons and blank entity fields; adapt examples from the user's archive only when
  the user supplies or authorizes access to it.
