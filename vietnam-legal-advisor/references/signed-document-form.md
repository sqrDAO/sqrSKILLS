# The Form (The Thuc) of Anything That Gets Signed and Sealed

> UNVERIFIED imported reference/template. Legal claims, figures, dates, and
> citations require current primary-source verification before use, as described
> in SKILL.md. Examples and document-style defaults are not universal legal rules.

A Vietnamese instrument is judged on its face before it is read. This file covers
the form rules for documents that a director signs and stamps, and the production
checks that have to pass before one is sent for signature.

Read this before producing any contract, annex, minutes, decision, power of
attorney, or official letter. It applies on top of the national-header rules in
`SKILL.md` Step 2.

## Table of contents
1. The governing rule: follow the executed contract, not a house style
2. How to derive the form from an executed document
3. A measured baseline
4. Order of elements on the first page
5. Running header and footer
6. The signature block and the physical seal
7. Language and typography inside the corpus
8. Production checks before a document goes for signature
9. Pre-send checklist

---

## 1. The governing rule: follow the executed contract, not a house style

**A brand style belongs on presentation material. An instrument follows the
executed contract it hangs off.** Coloured kickers, logo bands, display typefaces
and decorative rules make a document read as marketing collateral, and a
counterparty's legal team reads collateral as non-binding. The moment a document
will be signed and sealed, drop the identity system and adopt the contract's own
the thuc.

This is a client-visible decision, so it is worth stating once to the user and
then applying silently: everything in the signed set looks like the contract.

## 2. How to derive the form from an executed document

Open the executed contract and measure, do not guess:

- page size, orientation, and the four margins;
- the typeface, and the point sizes of body, heading, title, and signature block;
- alignment of body text (Vietnamese instruments are justified);
- the header and footer text, if any;
- table styling: header fill, grid weight and colour, body fill;
- **the vertical clear space between the signature caption and the printed name.**

Then reproduce those numbers rather than approximating them. Where the source
contains an obvious defect, fix it and say so: a navy header row with black text
is unreadable, and copying it faithfully is not fidelity, it is a bug.

## 3. A measured baseline

Numbers below come from measuring a real executed Vietnamese service contract.
They are a sane default when no executed contract is available, and they are the
right order of magnitude to check a draft against.

| Element | Value |
| --- | --- |
| Page | A4 portrait |
| Margins | about 1.9 cm top, 1.8 cm bottom, 2.0 cm left and right |
| Typeface | Times New Roman throughout, no second face |
| Body | 12 pt, justified |
| Heading (Dieu) | 13 pt bold |
| Title | bold, centred, all caps |
| Signature caption | 11.5 pt bold, centred |
| Signatory name | 11 pt bold, all caps |
| Role under the name | 10.5 pt |
| Table header row | solid dark fill with white text, 0.5 pt grey grid, no body fill |

## 4. Order of elements on the first page

```
[optional running header]

CONG HOA XA HOI CHU NGHIA VIET NAM        (bold, caps, centred)
Doc lap - Tu do - Hanh phuc               (bold, centred)
--------------------                      (solid rule under the motto)

[TITLE IN CAPS]                           (bold, centred)
[one-line subject, if the title needs it]
[contract or clause context line]
So: [...] · Ngay lap: dd/mm/yyyy

- Can cu ...;
- Can cu ...;

Hom nay, ngay ...... thang ...... nam ......, tai [place], chung toi gom:
```

A letter (cong van) differs: it uses a **two-column masthead**, issuer block on
the left with `So:` and `V/v:`, the national header on the right with the place
and date, then `Kinh gui:`.

## 5. Running header and footer

Match the instrument family rather than applying one rule everywhere.

- Contracts, annexes, minutes and file indexes: a confidentiality and parties
  header, and a footer with the document name and `Trang N/M`.
- **A cong van that follows an executed original carries whatever that original
  carries, which is often nothing.** Adding a header to match the rest of the set
  is a change to a form the client has already paid against. Leave it alone.

## 6. The signature block and the physical seal

**The signing space is a physical constraint, not a layout preference.**

- A Vietnamese round company seal is about 36 mm across, which is roughly 102 pt.
  That width is the floor: under it the stamp cannot physically sit clear of the
  printed name.
- **Use about 103 pt of clear space** between the signature caption and the
  printed name, and never go below the seal's own 102 pt. Keep the number in one
  place in whatever builds the document, so it cannot drift per file.
- **Derive that number by measuring the executed contract, and measure it again
  before you defend it.** One engagement carried 115 pt for five days on a note
  recording the contract's signature page as "about 4 cm". Re-measured directly
  off the PDF, the contract left **102.7 pt = 3.62 cm** from the caption to the
  printed name - and carried no `(Ky, ghi ro ho ten va dong dau)` line at all,
  while the derived forms inserted one *and* left 117-122 pt below it. The forms
  were more generous than the instrument they were copied from, in both places.
  *A constant everyone calls "measured" is worth measuring once more.*
- **The rendered gap is not the spacer you set.** It comes out larger by an
  amount fixed by the font sizes in that particular block - observed from +2.3 pt
  to +7.3 pt across one document set. Calibrate per document off its own render
  and record the values; do not assume one spacer gives one gap everywhere.
- **Never trade signing space for page count.** If a document will not fit,
  shorten the body or accept the extra page. Offered the choice between a
  one-page letter with a cramped block and a two-page letter with a proper one,
  take the two pages.

### Carry the space as row height, not as trailing paragraph space

A large `space_after` on the caption paragraph **splits across a page break even
when the row is marked as non-splitting**: the rule protects a table row from
splitting, and a single paragraph carrying that much trailing space straddles the
break by itself. The structure that holds is:

- a borderless two-column table for the two parties;
- a dedicated **blank row with an explicit minimum row height** between the
  caption row and the name row;
- non-splitting set on every row;
- keep-with-next on every paragraph except the last.

### Two traps when you adjust the space in bulk

**Set it on both columns.** Where the space lives in a paragraph's trailing space
rather than a row height, it is set in the left cell *and* the right cell. A row
keeps the taller of the two, so patching one column moves nothing at all and
reads as "the edit had no effect".

**A script that adjusts a value by measuring that same value must converge, or
work from absolutes.** One written to compute the new spacer from the currently
measured gap destroyed its own work on the second run: it read the corrected gap
as the baseline and set every document back to the old value. Either skip when
already within tolerance, or carry a calibrated table of absolute values.

**Measure off the render, and distrust the ruler before the document.** Anchor on
the caption text and the printed name, and take the **last** occurrence of each -
a surname that also appears in the body of a longer document will otherwise make
an intact block look split across pages.

Existing documents keep this space in different ways: a blank row, a blank
paragraph, nothing at all, or nothing at all with the caption placed last. Any
helper that adjusts the space has to look for all of those, in that order, or it
silently does nothing to half the set.

### The block must be whole

A signature block that starts on one page and finishes on the next is not
signable-looking. A trailing page holding nothing but the block is acceptable if
the block is whole; a split block is not. This is a page-count question, so it is
settled by rendering, not by reading the text.

## 7. Language and typography inside the corpus

- **Tone-mark style is per corpus, not per company.** One project can hold a
  presentation corpus in old style (`hoa` written `hoá`, `toa` written `toạ`) and
  a contract corpus in modern style (`toạ` written `tọa`). Match the document you
  are editing, not the last convention you read about. An edit that crosses both
  corpora produces a mixed file.
- **Follow the executed original even where it is inconsistent with the rest.**
  If a signed letter's masthead uses an older spelling of the national heading or
  a different dash, reproduce it. Correcting an executed form is a change to it.
- Vietnamese instruments carry full diacritics everywhere. No transliteration in
  a document that will be signed.
- No em dashes in generated text.

## 8. Production checks before a document goes for signature

These are the failures that a text diff does not show. Every one of them has
shipped at least once.

**Transform the finished file, do not replay the build.** When a set of documents
already exists and only the form has to change, convert the finished files.
Replaying a chain of build scripts to change a typeface risks every step of the
chain. Converting the finished file touches appearance only, so the text cannot
drift, which is the property that matters for something about to be signed.

**Guard against text drift.** Any transform of a document you did not author
should compare a multiset of every string in the document, paragraphs and table
cells both, before and after; allow only the specific lines it means to add or
remove; write to a temporary file; and replace the original only once the check
passes. Compare as a multiset, not a list, when the transform deliberately
reorders anything. Make it refuse to run twice on its own output.

**Direct run formatting beats style changes.** Restyling a paragraph style leaves
text where it was if the builder set a size on the run. Set the size and the
alignment on the paragraph itself, walk the document's paragraph list rather than
the body XML so that table cells keep the sizes their own pass gave them, and
when rewriting a table cell put the new string into the first run and blank the
rest so the run's face and size survive.

**Address a cell by index and assert its current text.** A string match over a
document with eight near-identical rows finds the wrong one eventually. Compare
against the expected text before writing, and skip a cell that already carries
the new text, so a re-run is a safe no-op.

**A header or footer holder can legitimately have zero paragraphs.** Add one
before clearing it.

**Check the helper's signature before trusting a call.** A date passed as a
positional argument that the helper treats as an emphasis substring is silently
dropped, and the result is an undated instrument that another document cites by
date. Any helper that accepts a string and ignores it when it does not match is
the kind of API that produces a dateless contract.

**Render, and count the pages, after every edit.** Adding a few words to a signed
form can push it onto another page and strand the signature block there. The page
count is the acceptance test, not the wording. When a wording change has to fit,
the budget is whatever keeps the page count: roughly 85 characters per rendered
line, and removing a duplicated claim usually buys back more room than trimming
adjectives.

**Prove the renderer before trusting it.** Render the unmodified document first
and compare against the version already reviewed or shipped. Matching page count
and matching embedded faces is a pass; a file-size difference alone is a
build-level subsetting difference, not a layout change. Extracted-text column
positions shift by a space or two between renderer builds, so compare
whitespace-insensitively.

**Font substitution: layout yes, identity no.** Times New Roman is generally
absent on Linux, and the substitute is metric compatible, so pagination and line
breaks from such a render are trustworthy. The embedded font identity is not: a
PDF produced that way carries the substitute, not Times New Roman. Re-render on a
machine that has the real font before sending anything for signature.

**Patch every copy.** A client-facing form usually exists in its authoritative
folder and again inside whatever package was sent. A script that fixes one leaves
the other asserting the opposite.

## 9. Pre-send checklist

- [ ] Form matches the executed contract: margins, face, sizes, table styling.
- [ ] National header block correct, Vietnamese only, solid rule under the motto.
- [ ] Number, date, and contract context line present on the face of the document.
- [ ] `Can cu` chain current and complete.
- [ ] Header and footer match the instrument family; a cong van inherits the
      executed original's absence of them.
- [ ] Signing space ~103 pt and never under 102 pt, carried as row height, block
      not split across a page break; measured off the render, not off the source.
- [ ] Rendered and page-counted after the last edit; no stranded signature page.
- [ ] Rendered with the real typeface installed before the PDF is sent.
- [ ] Tone-mark style matches this corpus; full diacritics; no em dashes.
- [ ] Personal data left blank; no internal or cost material inside a
      client-facing document.
- [ ] Every copy of the document in every folder carries the same revision.
