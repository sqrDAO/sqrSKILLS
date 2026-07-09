---
name: gtm-playbook
version: 0.1.0
description: |
  Build, fill in, audit, and operationalize a go-to-market plan end to end, from picking
  which idea to pursue through to closing deals: opportunity brainstorms and weighted
  decision matrices, company mission, ICP and buyer persona mapping (must-win plus
  tiers 1-3), qualifying questions, sales methodology selection (BANT/PNUB,
  MEDDIC/MEDDPICC, Value Selling, Challenger), the 8-stage sales cycle, cold outreach,
  objection handling, and Web3 partnership goal matrices. Use it whenever the user
  mentions GTM, go-to-market, ICP, buyer persona, sales playbook, qualification,
  pipeline stages, cold email, objection handling, BD, business development, or
  partnership strategy, even if they never say go-to-market. Also use it when they are
  choosing between ideas, scoring options against weighted criteria, building a
  decision matrix, running an idea brainstorm, or writing a problem statement,
  including blockchain opportunity assessment.
allowed-tools:
  - Bash(python3 *)
  - Read
  - Write
---

# GTM Playbook

A working system for taking a company from "we have a product" to "we have a repeatable motion." It covers two halves that most teams treat separately but that share the same underlying logic:

0. **Opportunity selection** (decide what to build at all): idea brainstorm, weighted decision matrix.
1. **Direct GTM** (sell to a buyer): mission, ICP, personas, qualification, sales cycle, outreach, objections.
3. **Partnership GTM** (grow through a partner): goal-typed partner matrices, common in Web3 and platform businesses.

All three ask the same three questions. Who is the counterparty, what do they get, and how will you know it worked. Keep that in view and the frameworks below stop feeling like paperwork.

Stage 0 is optional. Most teams arrive with an idea already chosen, and forcing them back through a brainstorm is a way of avoiding the harder work downstream. Run it when the user is genuinely comparing options, or when a stated problem turns out to have a solution baked into it.

## Choosing what to do

| The user wants | Do this |
|---|---|
| Choose between several product or venture ideas | Read `references/opportunity-ideation.md` (brainstorm, then decision matrix) |
| Start a GTM plan from nothing | Run the **Full build** below, in order |
| Fill in one section (personas, cold email, etc.) | Jump to that section's reference file, ask only the questions that section needs |
| Review or critique an existing plan | Run the **Audit** flow |
| Plan partnerships or BD targets | Read `references/partnership-goals.md` |
| Produce a spreadsheet deliverable | Use `$SKILL_DIR/scripts/build_gtm_workbook.py` |

Do not silently invent answers to fill blanks. The value of this artifact comes from the founder's own knowledge. Where an answer is unknown, write `TBD` and flag it, because an honest gap is more useful than a plausible fabrication and it tells the team where the next customer conversation needs to go.

## Full build

Work through the stages in order. Each stage depends on the one before it: personas without a mission produce a target list nobody can defend, and outreach without personas produces spam.

**Stage 0. Opportunity selection (skip if the idea is already chosen).** Diverge with the brainstorm table, converge with the weighted decision matrix. See `references/opportunity-ideation.md`. Never run both in one session. The output of this stage, one idea plus a written problem statement plus a named audience, is exactly the input Stage 1 and Stage 2 need.

**Stage 1. Company profile.** Vision, mission, values, culture, corporate objective, mission-critical priority, milestones. Keep the mission-critical priority to exactly one item. If the user names three, the plan has no priority.

**Stage 2. Offer definition.** Before any persona work, get crisp answers to: what problem does the solution solve, what is the solution, do existing solutions solve the same problem, and if so how is this different (and if not, why does the user think nobody has built it). "No competition" is nearly always a research failure or a market that does not exist. Push gently on it.

**Stage 3. ICP and personas.** One must-win persona (Persona A) plus tiers 1-3 (Personas B, C, D). Each has a company layer and a human layer. See `references/icp-personas.md`, which also holds the full qualifying-question set: target market economics, buyer pain and motivation, decision maker vs purse holder, and the route to each.

**Stage 4. Attention.** For each persona: interaction preferences, preferred content types, and the content sources they actually read. This is what makes the channel plan non-arbitrary.

**Stage 5. Methodology.** Pick one primary qualification framework and one primary sales philosophy. See `references/sales-methodologies.md`. Match the framework to deal size and complexity rather than to fashion.

**Stage 6. Sales cycle.** Define exit criteria for each of the 8 stages. See `references/sales-cycle.md`.

**Stage 7. Outreach and objections.** BASHO/WYWYN cold email, the 20-second cold call pitch, and the touch cadence; then the objection library. See `references/outreach-and-objections.md`.

**Stage 8. Partnerships (if relevant).** See `references/partnership-goals.md`.

### How to run the interview

Ask in small batches, three to five questions at a time, grouped by stage. Reflect the answers back in the user's own words before moving on. Founders frequently answer the question they wish you had asked, so listen for the drift and name it: "You described what the product does, but the question was what breaks for the buyer if they do nothing."

Two heuristics that catch most bad GTM plans:

- **The "so what" test.** Every persona attribute should change something downstream. If "Education Background: MBA" changes no message, no channel, and no qualification question, delete it.
- **The pain-to-budget chain.** Pain leads to initiative leads to decision maker leads to purse holder leads to budget. If you cannot trace a persona along the full chain, you have a user, not a buyer. Say so.

## Audit

When reviewing an existing plan, check in this order and report findings with severity (blocker, gap, nit):

1. **Solution smuggled into the problem statement.** "They lack a blockchain consent registry" is a solution, not a problem. Also check the decision matrix for correlated factors (market size and revenue potential are one factor counted twice), for weights assigned after scoring, and for a top-two spread under 5%, which means the matrix decided nothing.
2. **Priority collapse.** More than one mission-critical priority. More than one must-win persona.
3. **Persona without a chain.** Decision maker and purse holder unidentified, or the route to them undefined.
4. **Unfalsifiable metrics.** "Awareness" with no counted number attached. "Better engagement." Anything without a denominator.
5. **Stage criteria missing.** Sales stages defined by seller activity ("sent proposal") rather than buyer evidence ("buyer confirmed budget owner and timeline").
6. **Message drift.** Cold outreach copy that talks about the product rather than the persona's pain.
7. **Offer symmetry (partnerships).** A partner row with a goal and a metric but a blank Offer column. You have written down what you want, not what they get.

Lead with what is working. Then the blockers. Founders discard critiques that open with a list of failures.

## Output formats

Default to markdown in the conversation for discussion, and a spreadsheet when the user wants something the team can fill in and track.

**Spreadsheet.** The script emits a 10-tab workbook: Opportunity Brainstorm, Decision Matrix, Mission, B2B ICP Mapping, Personas Mapping, Sales Methodologies, Sales Cycle, Cold Outreach, Objection Handling, Partnership Goals. To produce a filled copy, write the answers to a JSON file and run:

```bash
python3 "$SKILL_DIR/scripts/build_gtm_workbook.py" answers.json -o GTM_filled.xlsx
```

The script needs the `openpyxl` package (the one documented non-stdlib dependency of this skill). If it is missing, install it with `pip install openpyxl` or fall back to the markdown output.

Run `python3 "$SKILL_DIR/scripts/build_gtm_workbook.py" --schema` to print the exact JSON shape it expects, including the `partnership_goals` tab. The script preserves the template's layout and only writes into the answer cells, so a partially filled `answers.json` produces a partially filled workbook with the rest left blank for the team.

**Subsets.** `--partnership-only` emits just the Partnership Goals tab. `--ideation-only` emits just the Opportunity Brainstorm and Decision Matrix tabs, which is the usual starting point for a workshop.

**Decision matrix arithmetic.** The script anchors the weighting row (`=B6*B$5`), sums the weights with a "must be 100" check, and adds a RANK column. This matters because the widely circulated `Decision-Matrix-Template.xlsx` does not anchor the Factor 1 column: rows below the first idea multiply by the previous idea's raw score instead of the weight, producing wrong totals that look plausible. If a user brings a filled copy of that original, check it before trusting the numbers. Both original templates ship in `assets/` for reference.

## Notes on tone

The frameworks below are tools, not liturgy. MEDDPICC on a $2,000 self-serve deal is malpractice. Challenger on a buyer who already knows exactly what they want is condescending. When a user's situation clearly does not fit a framework, say which one to drop rather than helping them fill out a form that will not close a deal.
