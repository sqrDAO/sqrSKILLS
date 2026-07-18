---
name: business-model-to-market
version: 0.2.0
description: 'Take a venture from a blank page to closed deals: pick which idea to pursue, model the whole business on one page, then build the go-to-market that sells it. Covers idea brainstorms and weighted decision matrices; the nine-block Business Model Canvas (value propositions, segments, channels, relationships, revenue, activities, resources, partners, costs); mission; ICP and buyer persona mapping; qualifying questions; sales methodology selection (BANT/PNUB, MEDDIC/MEDDPICC, Value Selling, Challenger); the 8-stage sales cycle; cold outreach; objection handling; and Web3 partnership matrices. Use it whenever the user mentions business model, business model canvas, BMC, value proposition, revenue model, cost structure, GTM, go-to-market, ICP, buyer persona, sales playbook, qualification, pipeline, cold email, objection handling, BD, or partnership strategy, even if they never say go-to-market, and when choosing between ideas or writing a problem statement, including blockchain opportunity assessment.'
allowed-tools:
  - Bash(python3 *)
  - Read
  - Write
---

# Business Model to Market

A working system for taking a venture from "we have an idea" to "we have a repeatable motion that closes deals." It runs at two zoom levels that most teams treat as separate exercises but that are the same territory:

0. **Opportunity selection** (decide what to build at all): idea brainstorm, weighted decision matrix.
1. **Business model** (map the whole company on one page): the nine-block Business Model Canvas.
2. **Direct GTM** (sell to a buyer): mission, offer, ICP, personas, qualification, sales cycle, outreach, objections.
3. **Partnership GTM** (grow through a partner): goal-typed partner matrices, common in Web3 and platform businesses.

The canvas is the bridge. Five of its nine blocks *are* the go-to-market, and the direct-GTM stages are those blocks zoomed in. The other four are the value-creation machine behind them, the half founders skip and then wonder why a flawless plan loses money. Fill the canvas and the GTM stages stop feeling like separate paperwork; they are the deep dive on its right-hand side.

All of it asks the same three questions. Who is the counterparty, what do they get, and how will you know it worked. Keep that in view and the frameworks below stop feeling like liturgy.

Stages 0 and 1 are optional. Most teams arrive with an idea chosen and forcing them back through a brainstorm avoids the harder work downstream. Run Stage 0 only when the user is genuinely comparing options. Run Stage 1 (the canvas) whenever the business model has never been laid out whole, or when a GTM plan feels internally perfect but nobody can say whether it makes money; that is almost always a missing left-hand side.

## Choosing what to do

| The user wants | Do this |
|---|---|
| Choose between several product or venture ideas | Read `references/opportunity-ideation.md` (brainstorm, then decision matrix) |
| Map or sanity-check the whole business model | Read `references/business-model-canvas.md` |
| Start from nothing | Run the **Full build** below, in order |
| Fill in one section (personas, cold email, etc.) | Jump to that section's reference file, ask only the questions that section needs |
| Review or critique an existing plan or model | Run the **Audit** flow |
| Plan partnerships or BD targets | Read `references/partnership-goals.md` |
| Produce a spreadsheet deliverable | Use `$SKILL_DIR/scripts/build_gtm_workbook.py` |

Do not silently invent answers to fill blanks. The value of this artifact comes from the founder's own knowledge. Where an answer is unknown, write `TBD` and flag it, because an honest gap is more useful than a plausible fabrication and it tells the team where the next customer conversation needs to go.

## Full build

Work through the stages in order. Each depends on the one before it: a canvas without a chosen opportunity models the wrong company, personas without a mission produce a target list nobody can defend, and outreach without personas produces spam.

**Stage 0. Opportunity selection (skip if the idea is already chosen).** Diverge with the brainstorm table, converge with the weighted decision matrix. See `references/opportunity-ideation.md`. Never run both in one session. The output, one idea plus a written problem statement plus a named audience, is exactly the input the canvas and the GTM stages need.

**Stage 1. Business model canvas.** Lay the whole model on one page before drilling into any single part. Fill it in logical order (segments, value propositions, channels, relationships, revenue, then activities, resources, partners, cost) and read it back as one sentence to check it closes. See `references/business-model-canvas.md`. The right half of the canvas hands its blocks directly to Stages 3 through 9; the left half is the cost-and-creation reality check the GTM stages have no other home for. Skip only if a current, coherent model already exists.

**Stage 2. Company profile.** Vision, mission, values, culture, corporate objective, mission-critical priority, milestones. Keep the mission-critical priority to exactly one item. If the user names three, the plan has no priority.

**Stage 3. Offer definition.** This is the canvas's Value Propositions block zoomed in. Get crisp answers to: what problem does the solution solve, what is the solution, do existing solutions solve the same problem, and if so how is this different (and if not, why does the user think nobody has built it). "No competition" is nearly always a research failure or a market that does not exist. Push gently on it.

**Stage 4. ICP and personas.** The canvas's Customer Segments block zoomed in. One must-win persona (Persona A) plus tiers 1-3 (Personas B, C, D). Each has a company layer and a human layer. See `references/icp-personas.md`, which also holds the full qualifying-question set: target market economics (this is where Revenue Streams gets pressure-tested), buyer pain and motivation, decision maker vs purse holder, and the route to each.

**Stage 5. Attention.** The awareness and evaluation phases of the canvas's Channels block. For each persona: interaction preferences, preferred content types, and the content sources they actually read. This is what makes the channel plan non-arbitrary.

**Stage 6. Methodology.** Pick one primary qualification framework and one primary sales philosophy. See `references/sales-methodologies.md`. Match the framework to deal size and complexity rather than to fashion, and to the relationship mode you chose on the canvas.

**Stage 7. Sales cycle.** Define exit criteria for each of the 8 stages. This is the purchase, delivery, and after-sales phases of the canvas's Channels block made operational. See `references/sales-cycle.md`.

**Stage 8. Outreach and objections.** BASHO/WYWYN cold email, the 20-second cold call pitch, and the touch cadence; then the objection library. See `references/outreach-and-objections.md`.

**Stage 9. Partnerships (if relevant).** The canvas's Key Partners block zoomed in. See `references/partnership-goals.md`.

### How to run the interview

Ask in small batches, three to five questions at a time, grouped by stage. Reflect the answers back in the user's own words before moving on. Founders frequently answer the question they wish you had asked, so listen for the drift and name it: "You described what the product does, but the question was what breaks for the buyer if they do nothing."

Three heuristics that catch most bad plans:

- **The "so what" test.** Every persona attribute should change something downstream. If "Education Background: MBA" changes no message, no channel, and no qualification question, delete it.
- **The pain-to-budget chain.** Pain leads to initiative leads to decision maker leads to purse holder leads to budget. If you cannot trace a persona along the full chain, you have a user, not a buyer. Say so.
- **The sentence-closes test (canvas).** Read the model as one sentence: we deliver [value proposition] to [segment] through [channels], keeping them via [relationship], earning [revenue], by doing [activities] with [resources], partnering for [the rest], at [cost]. Wherever that sentence breaks is the next thing to go learn.

## Audit

When reviewing an existing plan or model, check in this order and report findings with severity (blocker, gap, nit):

1. **Solution smuggled into the problem statement.** "They lack a blockchain consent registry" is a solution, not a problem. Also check the decision matrix for correlated factors (market size and revenue potential are one factor counted twice), for weights assigned after scoring, and for a top-two spread under 5%, which means the matrix decided nothing.
2. **Canvas half-built.** A fully worked right-hand side (segments, value props, channels, revenue) sitting on empty creation blocks (activities, resources, cost). The plan cannot be costed, so it cannot be judged. See the full canvas failure list in `references/business-model-canvas.md`.
3. **Model incoherence.** A persona in the GTM plan with no matching customer segment on the canvas; a revenue stream nobody is qualified against; a premium value proposition on a cost-driven structure; a value proposition claiming five value flavors with no lead.
4. **Priority collapse.** More than one mission-critical priority. More than one must-win persona.
5. **Persona without a chain.** Decision maker and purse holder unidentified, or the route to them undefined.
6. **Unfalsifiable metrics.** "Awareness" with no counted number attached. "Better engagement." Anything without a denominator.
7. **Stage criteria missing.** Sales stages defined by seller activity ("sent proposal") rather than buyer evidence ("buyer confirmed budget owner and timeline"). Channels that stop at evaluation and never define delivery or after-sales.
8. **Message drift.** Cold outreach copy that talks about the product rather than the persona's pain.
9. **Offer symmetry (partnerships).** A partner row with a goal and a metric but a blank Offer column, or a partner mapping to none of the three partnership motivations. You have written down what you want, not what they get.

Lead with what is working. Then the blockers. Founders discard critiques that open with a list of failures.

## Output formats

Default to markdown in the conversation for discussion, and a spreadsheet when the user wants something the team can fill in and track.

**Spreadsheet.** The script emits an 11-tab workbook: Opportunity Brainstorm, Decision Matrix, Business Model Canvas, Mission, B2B ICP Mapping, Personas Mapping, Sales Methodologies, Sales Cycle, Cold Outreach, Objection Handling, Partnership Goals. To produce a filled copy, write the answers to a JSON file and run:

```bash
python3 "$SKILL_DIR/scripts/build_gtm_workbook.py" answers.json -o GTM_filled.xlsx
```

Run `python3 "$SKILL_DIR/scripts/build_gtm_workbook.py" --schema` to print the exact JSON shape it expects, including the `business_model_canvas` and `partnership_goals` tabs. The script preserves the template's layout and only writes into the answer cells, so a partially filled `answers.json` produces a partially filled workbook with the rest left blank for the team.

**Subsets.** `--canvas-only` emits just the Business Model Canvas tab. `--partnership-only` emits just the Partnership Goals tab. `--ideation-only` emits just the Opportunity Brainstorm and Decision Matrix tabs, the usual starting point for a workshop.

**Decision matrix arithmetic.** The script anchors the weighting row (`=B6*B$5`), sums the weights with a "must be 100" check, and adds a RANK column. This matters because the widely circulated `Decision-Matrix-Template.xlsx` does not anchor the Factor 1 column: rows below the first idea multiply by the previous idea's raw score instead of the weight, producing wrong totals that look plausible. If a user brings a filled copy of that original, check it before trusting the numbers. Both original templates ship in `assets/` for reference.

## Notes on tone

The frameworks here are tools, not liturgy. MEDDPICC on a $2,000 self-serve deal is malpractice. Challenger on a buyer who already knows exactly what they want is condescending. A full nine-block canvas for a weekend hackathon project is procrastination in a suit. When a user's situation clearly does not fit a framework, say which one to drop rather than helping them fill out a form that will not close a deal.
