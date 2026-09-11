# Document Library: Skeletons and Fill-In Details

> UNVERIFIED imported reference/template. Legal claims, figures, dates, and
> citations require current primary-source verification before use, as described
> in SKILL.md. Examples and document-style defaults are not universal legal rules.

Starting points for drafting. Fill placeholders, keep bilingual (Vietnamese
governs, English mirror), and run the result against the relevant reference
checklist and `references/legal-updates-2025-2026.md`.

## Entity fill-in block (domestic operating company)

Fill this from the current registration supplied by the user for the relevant company party:

```
[Ten phap ly tieng Viet / English legal name]
Ma so doanh nghiep / Tax code (MST): [MST]
Dia chi tru so chinh / Head office: [registered address]
Nguoi dai dien theo phap luat / Legal representative: [name], Giam doc / Director
Email nhan hoa don / Invoicing email: [invoicing email]
Van phong dai dien / Representative office (if applicable): [registered address]
```

Rules: never paste an individual's CCCD, personal home address, or a family
member's name from one document into another; leave them as blanks. Use only the transaction's confirmed billing entity.
Attribution for cover notes: [name, title, organization, if requested].

## The standard document header (use on every formal document)

The national header (Quoc hieu + Tieu ngu) is Vietnamese-only: the country name,
the motto, and a solid centered line directly under the motto (about the motto's
width). No English translation of the motto, no "o0o" divider. The bilingual
title comes after the block.

```
              CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM     (bold, caps, centered)
                 Độc lập - Tự do - Hạnh phúc         (bold, centered)
                 ─────────────────                   (solid line ~ motto width)

              HỢP ĐỒNG LAO ĐỘNG / LABOR CONTRACT      (title: bold caps VN + italic EN)

So / No.: [nnn]/[YYYY]/[TYPE]              [Place], ngày ... tháng ... năm ...
```

Example type codes: `HDDV` (service contract), `HDDVTV` (consulting
service contract), `HDLD` (labor contract), `PLHD` (contract annex), `HDTK`
(piecework/contractor), `QD-GD` (director's decision), `CP-UQ` (power of
attorney). Close-out documents add `BBNT` (acceptance minutes, numbered
`[nn]/[YYYY]/BBNT/[A]-[B]`) and `DNTT` (payment request letter, numbered
`So: [nn]/DNTT`). An example contract number takes the shape
`[nnnn]/[YYYY]/HDDV/[PARTY-A]-[PARTY-B]`.

**Signature block.** Confirm signatory authority and whether a seal is required or
used. If used, measure it and provide sufficient clearance (about 103 pt is an
example for a roughly 36 mm seal). Keep the block whole; verify the actual render.
See `references/signed-document-form.md`.

## Archive map (patterns to reuse)

If the user supplies or authorizes access to a precedent archive, look for the
following document types. Update the registration, address format, and verified
"Can cu" citations before reuse. No private archive is bundled or required.

- Corporate: GCN DKDN, Dieu le (charter, single- and multi-member versions),
  Giay de nghi dang ky doanh nghiep, Thong bao thay doi DKKD, Thong bao thay doi
  chu so huu, Hop dong chuyen nhuong phan von gop, To khai thue TNCN chuyen nhuong
  von, Giay uy quyen, Danh sach nguoi dai dien theo uy quyen, Thong bao mau con
  dau, GCN van phong dai dien, Quyet dinh bo nhiem Ke toan truong.
- Labor: Hop dong lao dong (bilingual), Phu luc hop dong lao dong (salary change),
  Hop dong thue khoan.
- Commercial: Hop dong dich vu tu van (bilingual consulting template), Hop dong
  dich vu (service), Thoa thuan hop tac (MOU, including with a public partner).

Check inherited templates for obsolete letterhead and superseded legal citations
before treating them as usable precedents.

## Skeleton A: Service contract with an individual (HDDV)

```
[STANDARD HEADER]  Title: HOP DONG DICH VU / SERVICE CONTRACT
So: [nnn]/2026/HDDV

- Can cu Bo luat Dan su so 91/2015/QH13;
- Can cu nhu cau va kha nang cua cac ben.

Hom nay, ngay .../.../2026, tai [place], chung toi gom:

BEN A (Party A): [ENTITY FILL-IN BLOCK]
BEN B (Party B): Ong/Ba [name] / DOB [__] / CCCD [__________] / Dia chi [______]

Dieu 1. Noi dung hop dong / Scope: [tasks, or "theo Phu luc 1 dinh kem"].
Dieu 2. Thu lao va thanh toan / Fee and payment:
  - Muc thu lao: [amount] VND/thang. [state: da bao gom thue TNCN / PIT-inclusive,
    OR net + company grosses up].
  - Phuong thuc: chuyen khoan. Ngay thanh toan: [day].
Dieu 3. Quyen va nghia vu cua hai ben / Obligations of both parties.
Dieu 4. Bao mat thong tin / Confidentiality (survives termination).
Dieu 5. Dieu khoan chung / General: sua doi bang van ban; tranh chap thuong
  luong roi Toa an co tham quyen; 02 ban co gia tri nhu nhau.

[SIGNATURE + SEAL BLOCK]
```
Before finalizing: check the classification line (is this really employment?),
state PIT treatment, cite Civil Code 2015 not 2005.

## Skeleton B: Consulting service contract, bilingual B2B (HDDVTV)

Same header and structure as A, but Ben B is a company (name, MST, rep), add
Commercial Law 2005 (36/2005/QH11) to "Can cu", define the Service Package and
completion, state VAT inclusion and [verified applicable VAT rate], add IP ownership of deliverables
and a governing-language clause (Vietnamese governs). Use the confirmed company letterhead.

## Skeleton C: Cooperation agreement / MOU

```
[STANDARD HEADER]  Title: THOA THUAN HOP TAC / COOPERATION AGREEMENT

Recitals (Can cu): [relevant resolutions/decisions, especially for a public
  partner; confirm the partner's current post-2025 name and address].

BEN A: [partner]        BEN B: [ENTITY FILL-IN BLOCK]

I.  Muc dich hop tac / Purpose.
II. Noi dung hop tac / Scope of cooperation: [concrete activities].
III.Kinh phi / Funding: [each party's lawful sources; no committed figure unless
    intended].
IV. To chuc thuc hien / Implementation: focal points, periodic meetings.
V.  Bao mat / Confidentiality.
VI. Hieu luc / Term: [e.g. 2 years]; 02 ban co gia tri nhu nhau.

[SIGNATURE + SEAL BLOCK]
```
Keep non-binding on money unless the user wants a binding commitment.

## Skeleton D: Labor contract (HDLD), bilingual

Two valid types only (indefinite / definite up to 36 months). Include: parties,
term and job, workplace, working time, wage (>= regional minimum, 2026 figures),
allowances, social/health/unemployment insurance per the 2024 SI Law, leave (12
days baseline), obligations, discipline and material responsibility, confidential-
ity, termination per Labor Code 2019, 02 copies one per party. For a salary change
later, use a Phu luc (annex) that does not alter the term.

## Skeleton E: Power of attorney (Giay uy quyen)

```
[STANDARD HEADER]  Title: GIAY UY QUYEN
So: [nnn]/2026/CP-UQ

Ben uy quyen (Principal): [company or individual, details as blanks].
Ben nhan uy quyen (Attorney): [name, CCCD as blank].

Dieu 1. Noi dung va pham vi uy quyen / Scope: [narrow, specific, e.g. lodge and
  collect enterprise-registration results].
Dieu 2. Thoi han uy quyen / Term: [from ... until replaced/completed].
Dieu 3. Nghia vu cac ben / Obligations.
Dieu 4. Dieu khoan cuoi / Final: voluntary, effective on signing.

[SIGNATURES]
```
Keep scope and duration explicit and narrow.

## Skeleton F: Director's decision (e.g. chief-accountant appointment)

```
[STANDARD HEADER]  Title: QUYET DINH  V/v [subject]
So: [nn]/[YY]/QD-GD

GIAM DOC [TEN CONG TY]
- Can cu Luat Doanh nghiep so 59/2020/QH14 (sua doi boi Luat 76/2025/QH15);
- Can cu Dieu le [ten cong ty];
- Can cu co cau to chuc va tinh hinh thuc te cua Cong ty.

QUYET DINH:
Dieu 1. [Appoint [name], CCCD blank, to [role] from [date]].
Dieu 2. [Duties and reporting line].
Dieu 3. [Who executes this decision].
Dieu 4. Hieu luc ke tu ngay ky.

Noi nhan: ...        GIAM DOC (sign + seal) [name]
```

## Skeleton G: Acceptance minutes (BBNT)

```
[STANDARD HEADER]  Title: BIEN BAN NGHIEM THU HANG MUC TAI [PLACE]
[programme] · [the contract clause that requires a bien ban]
So: [nn]/[YYYY]/BBNT/[A]-[B] · Ngay lap: dd/mm/yyyy · [milestone, venue, date]

- Can cu Bo luat Dan su so 91/2015/QH13; Luat Thuong mai so 36/2005/QH11;
- Can cu Hop dong dich vu so [...] ngay [...];
- Can cu pham vi, san pham ban giao va tieu chi nghiem thu tai Phu luc 01;
- Can cu ket qua trien khai [milestone] ngay [...].

Hom nay, ngay ...... thang ...... nam ......, tai [place], chung toi gom:

DIEU 1. THONG TIN CAC BEN        (name, MST, address, representative, title)
DIEU 2. PHAM VI DE NGHI NGHIEM THU  (STT | hang muc | khoi luong doi chieu | co so xac nhan,
                                     each row stating its exclusions)
DIEU 3. KET QUA NGHIEM THU       [ ] toan bo  [ ] co dieu kien  [ ] khong nghiem thu
DIEU 4. KHIEM KHUYET VA YEU CAU KHAC PHUC   (item | tinh trang | yeu cau + deadline)
DIEU 5. GIA TRI NGHIEM THU VA NGHIA VU THANH TOAN
        5.1 tranche triggered, percentage and amount incl VAT
        5.2 deduction and the phu luc that authorises it, amount payable, bang chu
        5.3 conditionality: 5.2 applies only once the phu luc is signed by both parties
        5.4 invoice trigger, payment term, where pass-through costs settle
DIEU 6. HIEU LUC VA BAN LUU      (02 ban; signing waives nothing; deemed acceptance)

[SIGNATURE + SEAL BLOCK, both parties]
```

## Skeleton H: Contract annex adjusting value (PLHD)

```
[STANDARD HEADER]  Title: PHU LUC [nn] BO SUNG HOP DONG
[subject: Dieu chinh gia tri Hop dong sau nghiem thu moc ...]
Hop dong dich vu so [...] · Ngay lap: dd/mm/yyyy

- Can cu Hop dong dich vu so [...] ngay [...] va cac Phu luc truoc;
- Can cu Dieu [n] cua Hop dong ve sua doi, bo sung Hop dong;
- Can cu Bien ban nghiem thu ngay [...].

DIEU 1..n   one Dieu per adjusted line:
              n.1 Pham vi thuc te   (facts first)
              n.2 Muc giam          (pre-VAT, VAT, total)
DIEU n+1. GIA TRI HOP DONG SAU DIEU CHINH   (truoc dieu chinh | sau dieu chinh)
DIEU n+2. AP DUNG VAO LICH THANH TOAN
DIEU n+3. HIEU LUC   (bo phan khong tach roi; other terms unchanged; 02 ban)

[SIGNATURE + SEAL BLOCK, both parties]
```

## Skeleton I: Payment request letter (DNTT)

```
[ISSUER NAME, left]                       [QUOC HIEU BLOCK, right]
So:      /DNTT                            [Place], ngay ... thang ... nam ...
V/v: Thanh toan dot [n] gia tri Hop dong dich vu so [...]

Kinh gui: [CLIENT LEGAL NAME IN FULL]

[courtesy opening]
Can cu Hop dong dich vu so [...] ngay [...];
Can cu Bien ban nghiem thu ngay [...];
Can cu Phu luc [nn] bo sung Hop dong ngay [...],
[Issuer] de nghi Quy Cong ty xem xet thanh toan dot [n] theo khoan [...]:

  1. Gia tri Hop dong tam tinh sau dieu chinh:   [amount] dong
     1.1 Phi dich vu co dinh sau dieu chinh:     [amount] dong
     1.2 Chi phi ben thu ba (chi ho):            [amount] dong
  2. Gia tri de nghi thanh toan dot [n]:         [amount] dong
     2.1 Dot [n] theo khoan [...]:               [amount] dong
     2.2 Giam tru theo Phu luc [nn]:           - [amount] dong

Bang chu: [...] dong.
Thoi han thanh toan: ... theo khoan [...].
Ve hoa don: ... theo khoan [...].
Tai khoan so / Tai / Don vi thu huong + MST.
[closing line]
Noi nhan:              [ISSUER]
- Nhu tren;            GIAM DOC
- Luu VP; KT.          (Ky, ghi ro ho ten va dong dau)
                       [NAME]
```
Short by design. It states the net amount and cites the annex; it never argues
its own adjustments. No running header or footer if the executed original for an
earlier tranche has none. See `references/contract-execution.md` section 7.

## Skeleton J: Acceptance request letter and file index

The request letter (`THU DE NGHI NGHIEM THU`) is a field table (`Kinh gui`,
`Ben de nghi`, `Hop dong`, `Hang muc`, `Can cu`), a short request paragraph
carrying the exclusions, an attachments table, the response window quoted from
the contract, and a surviving-obligations sentence. Provider signs alone.

The file index (`DANH MUC HO SO NGHIEM THU`) has four sections: the line-by-line
reconciliation against the scope appendix with a "confirmation still needed"
column, the folder structure and file counts, the limits of the package, and a
tick-box confirmation block. Both are detailed in
`references/contract-execution.md`.

## Closing line to append to any drafted document delivered to the user

State, in the message (not in the document body): this is a working draft for
review, not legal advice; Vietnamese text governs; route any registry filing to
the corporate-services / law firm, any tax/payroll item to the accountant, and any
dispute or novel structure to a licensed Vietnamese lawyer.
