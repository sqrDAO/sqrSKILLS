# Opportunity Ideation and Selection

This stage sits *upstream* of everything else in the playbook. Before there is an ICP, there is a choice about which opportunity to pursue at all. Two artifacts do the work: a **brainstorm table** that generates candidates, and a **decision matrix** that selects among them.

The pairing matters. Brainstorming alone produces a list nobody can choose from. A decision matrix alone produces a rigorous comparison of three mediocre options. Divergence then convergence, in that order, and never in the same working session.

## Contents
- The brainstorm table
- Writing a good problem statement
- The "opportunity for blockchain" test
- The decision matrix
- Choosing and weighting factors
- Reading the result honestly
- A known bug in the source template

---

## The brainstorm table

Six columns, one row per idea, minimum five ideas. Fewer than five and you have not diverged, you have rationalized the idea you walked in with.

| Column | What goes in it |
|---|---|
| **Idea** | Row id only. Idea 1, Idea 2. |
| **Industry and Market Segment** | Both. "Education" is an industry. "K-12 educational research" is a market segment. The segment is where the work happens. |
| **Problem Statement (Statement of Need)** | What is broken, for whom, and why the current approach fails. No solution words. |
| **Target customers / audience** | Every party touched. Note that the payer, the user, and the beneficiary are often three different parties, and listing all three early prevents a painful discovery in month six. |
| **Opportunity for Blockchain** | Why *this* technology, for *this* problem. Subject to the test below. |
| **Give this idea a name** | A real name, ideally an acronym or a compound that encodes the mechanism. |

The naming column looks like decoration and is not. An idea you cannot name is an idea you cannot describe, and naming forces you to decide what the thing actually is. The template's own example, "Preepare" (Programmatically-Executed Ethics Protocols for Advanced Research in Education), is a decent illustration: the name carries the mechanism, the domain, and the beneficiary.

**Facilitation.** Generate in silence first, individually, then pool. Group brainstorming converges on the loudest person's idea within four minutes. Aim for eight to twelve candidates and cut to five before scoring.

---

## Writing a good problem statement

The statement of need is the column that decides whether the rest of the row is worth anything. Three tests:

1. **No solution smuggled in.** "Schools lack a blockchain-based consent registry" is a solution wearing a problem's clothes. The problem is what happens today without one.
2. **Named sufferer.** Who feels this, in what role, how often. A problem nobody experiences on a Tuesday is a thesis, not a problem.
3. **Why the status quo persists.** If it is this bad and this obvious, something has been holding the current approach in place. Name it. Usually it is switching cost, regulation, or the fact that the person who suffers is not the person who pays.

Note the structure of the template's example: it names the process (ethics review, informed consent for minors), the specific failures (time consuming, lacks transparency), and the structural cause (places a high degree of trust in the integrity of the researcher regarding collection, storage, use, and presentation of student data). Three sentences, no product.

---

## The "opportunity for blockchain" test

This column is where most brainstorms quietly become fiction. Blockchain earns its place when the problem contains at least one of these, and the answer should say which:

- **Multi-party, low trust.** Parties who must coordinate but have no reason to trust each other's records, and no acceptable neutral intermediary.
- **Verifiable history.** Someone later needs to prove what was true at a past moment, and the party holding the record has an incentive to revise it.
- **Programmable settlement.** Value or permission moves automatically when a condition is met, and the delay or discretion of a human check is itself the cost.
- **Credible commitment.** A party needs to make a promise they cannot walk back, and their word is insufficient.
- **Portable identity or ownership.** The asset or credential must move between systems that will never agree on a shared database.

If none of these apply, write "a database would do this" in the column and keep the row anyway. It is a useful row. It calibrates the ones that survive.

A specific failure to watch for: **the audit-log illusion.** Many ideas want an immutable log. Immutability of the log does not make the *inputs* true. If a human types the reading into the chain, you have an immutable record of what somebody typed. Say so when it applies, because it usually does, and it usually shifts the real opportunity toward the oracle problem rather than the ledger.

---

## The decision matrix

A weighted scoring model. Ideas down the rows, factors across the columns.

Layout, mirroring the template:

- **Row: Factor Weighting.** A weight per factor. Convention: weights sum to 100.
- **Rows: one per idea.** For each factor, a raw score.
- **Weighted score** per cell = raw score × factor weight.
- **TOTAL** per idea = sum of weighted scores.

Score raw values on a consistent scale, and say which scale you used. A 1 to 5 scale is enough; 1 to 10 invents a precision nobody possesses. Anchor at least the endpoints in words before scoring anything, for example "5 = we could ship a pilot with the team we have today; 1 = requires a capability we would have to acquire."

---

## Choosing and weighting factors

Between four and seven factors. Ten columns exist in the template; using all ten is a way of refusing to have an opinion, since when everything is weighted, nothing is.

Factors that tend to earn their place:

| Factor | Question it answers |
|---|---|
| Problem severity | How badly does the sufferer want this fixed? |
| Willingness to pay | Is there a budget line, and can we reach it? |
| Blockchain necessity | Would a database do this? |
| Time to first pilot | How fast do we learn whether we are wrong? |
| Regulatory exposure | Does this need permission that we cannot get? |
| Team fit | Do we have an unfair advantage here? |
| Market size | Does winning matter? |

Two rules for weighting. First, weight before you score. Deciding that "market size" matters most *after* seeing which idea wins on market size is not analysis, it is post-hoc rationalization with a spreadsheet. Second, no factor gets zero weight; if it truly does not matter, delete the column.

**Correlated factors double-count.** "Market size" and "revenue potential" are usually the same factor twice, which silently doubles its weight. Check for this before scoring.

---

## Reading the result honestly

The number is an input, not a verdict.

1. **Check the spread.** If the top two totals are within about 5%, the matrix has not decided anything. Do not pretend it has. Either add a tie-break factor you genuinely believe in, or accept that both are viable and choose on grounds the matrix does not capture, such as which one you want to work on for four years.
2. **Run the flip test.** Change the single weight you are least sure about by ±10 points. If the winner changes, the result rests on a judgment you just admitted you are unsure of. That is the finding. Report it.
3. **Ask whether you like the answer.** If the matrix picked an idea and your gut sank, the gut is carrying information the factors did not encode. Find out what it is and add it as a factor, then rescore. Overriding the matrix without doing this is how teams learn nothing from having built it.
4. **Kill politely.** Losing ideas go into a parked list with the reason and the condition that would revive them. "Revisit if custody rules change" is a real asset.

The output of this stage is one idea, a written problem statement, and a named target audience. That is exactly the input the company profile and offer definition stages need.

---

## A known bug in the source template

The distributed `Decision-Matrix-Template.xlsx` has an off-by-one error. In the weighted-score column for **Factor 1 only**, the formulas were copied down without anchoring the weight row:

```
Row 6:  =B6*B5   correct, points at the weighting row
Row 7:  =B7*B6   wrong, points at idea 1's raw score
Row 8:  =B8*B7   wrong, points at idea 2's raw score
```

Every other factor column correctly points at row 5. The result is that Factor 1 is scored correctly for the first idea and nonsensically for the rest, in a way that produces plausible-looking numbers rather than an error. If a user brings you a filled copy of the original template, check this before trusting the totals, and check whether they copied any column sideways.

The correct form anchors the weight row: `=B6*B$5`. The `build_gtm_workbook.py` script in this skill generates the matrix with correct anchoring, a weight-sum check, and a rank column.
