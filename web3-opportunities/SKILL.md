---
name: web3-opportunities
version: 0.2.2
description: |
  Catalog and surface funding and launch opportunities for Web3 builders and founders —
  accelerators, incubators, grants, hackathons, bounties, retroactive funding,
  fellowships, and education programs (bootcamps/academies) — filterable by TYPE, STAGE &
  DILUTION (idea/pre-seed/mvp/growth; dilutive
  vs non-dilutive), CHAIN/ECOSYSTEM (Ethereum & L2s, Solana, Polkadot, Cosmos, NEAR, Sui,
  multi-chain), and GEOGRAPHY (global, us, europe, india, sea, latam, africa, remote).
  Coverage is global with an explicit Southeast Asia / Vietnam highlight. Use this skill
  whenever the user asks: "where can I get a Web3 grant", "crypto accelerators for my
  stage", "non-dilutive funding for a Solana project", "hackathons I can enter", "RetroPGF
  / retroactive funding", "ecosystem grants for Arbitrum/Optimism/Base/Polkadot/NEAR/Sui",
  "bounties for builders", "Web3 fellowships", or "funding options for a SEA / Vietnam
  crypto founder". Query the bundled catalog first, then optionally verify time-sensitive
  details (deadlines, open/closed cohort status, prize pools) live and label them clearly.
allowed-tools:
  - Bash(python3 *)
  - Read
  - WebSearch
  - WebFetch
metadata:
  nanobot:
    always: true
---

# web3-opportunities

Answers "where can a Web3 builder/founder get funded or launch?" from a curated, bundled
roster of accelerators, incubators, grants, hackathons, bounties, retroactive funding, and
fellowships. The roster's stable facts (what a program is, who it serves, which chains and
regions, dilutive vs non-dilutive) ship offline. Time-sensitive details (deadlines, open
cohorts, current prize pools) are baseline snapshots that the agent verifies live before
the user acts.

Tool-name note for portability: this skill body uses `python3` for the shell/terminal,
`Read` for file reads, and `WebSearch`/`WebFetch` for live web lookups. Map these to your
runtime's equivalents if they are named differently.

## When to Use

Trigger this skill when the user wants opportunities, not regulation:
- "Where can I get a Web3/crypto grant?" / "non-dilutive funding for [chain] project"
- "Crypto accelerators / incubators for my stage" / "which accelerator should I apply to?"
- "Hackathons I can enter" / "ETHGlobal / Colosseum / Solana hackathon schedule"
- "Ecosystem grants for Arbitrum / Optimism / Base / Polkadot / Cosmos / NEAR / Sui / Filecoin"
- "RetroPGF / retroactive funding" / "bounties for builders" / "Web3 fellowships"
- "Funding options for a Southeast Asia / Vietnam crypto founder"

This skill is about funding and launch ramps. For Vietnam crypto law, tax, and licensing,
use the `vietnam-crypto-radar` skill instead.

## Core method: catalog first, enrich second

1. **Query the bundled roster** with the user's facets:
   ```bash
   python3 "$SKILL_DIR/scripts/query_opportunities.py" --type grant --dilution non-dilutive --region sea
   ```
   The script returns matching entries plus `data_as_of` and `time_sensitive_fields`.
2. **Trust the stable fields as-is**: `type`, `stage`, `dilution`, `chains`, `regions`,
   `url`, `name`. These are evergreen.
3. **Treat the time-sensitive fields as baseline snapshots**: `status`, `cadence`,
   `typical_check_or_prize`, and any deadline. They reflect what was true on the entry's
   `last_verified` date, not necessarily today.
4. **Enrich when the user needs to act** (apply, hit a deadline, confirm a prize). Use
   `WebSearch`/`WebFetch` against the entry's `url` (Tier-1) and `references/sources.md`.
5. **Label every time-sensitive fact**: mark it `[bundled baseline · as of <last_verified>]`
   or `[live-verified · <today>]`. Never present a baseline deadline or "open" status as
   current without checking.

## Usage

```bash
# Full roster (default when no filters are given)
python3 "$SKILL_DIR/scripts/query_opportunities.py" --all

# Non-dilutive grants for an idea-stage founder in Southeast Asia
python3 "$SKILL_DIR/scripts/query_opportunities.py" --type grant --dilution non-dilutive --stage idea --region sea

# All Solana hackathons
python3 "$SKILL_DIR/scripts/query_opportunities.py" --type hackathon --chain solana

# SEA / Vietnam highlight surface (curated relevance flag)
python3 "$SKILL_DIR/scripts/query_opportunities.py" --sea

# OR within a facet, AND across facets
python3 "$SKILL_DIR/scripts/query_opportunities.py" --type grant,hackathon --chain ethereum,l2 --region global

# Free-text search over name / id / notes
python3 "$SKILL_DIR/scripts/query_opportunities.py" --search optimism
```

Filtering is AND across facets, OR within a facet. List facets (`--type`, `--stage`,
`--chain`, `--region`, `--status`) accept repeated flags or comma-separated values.
`--dilution` is exact-match: `non-dilutive` does NOT auto-include `mixed` — ask for `mixed`
explicitly when relevant. If `$SKILL_DIR` is not set by the runtime, replace it with the
absolute path to this skill directory.

## Verification discipline

- The roster is the source of truth for a program's EXISTENCE and STABLE facets. Do not
  enumerate programs from memory — run the script.
- Time-sensitive fields carry a per-entry `last_verified` anchor; the set carries
  `data_as_of`. State the baseline date when you quote them unverified.
- A time-sensitive fact counts as "live-verified" only if confirmed on the program's
  official page (Tier-1) or two independent aggregators (Tier-2) — see `references/sources.md`.
- When live data contradicts the baseline, live wins; note the drift so it can be fixed in
  the data file later.
- This is informational, not financial or legal advice.

## Output / presentation template

Present results grouped by type, with a separate SEA/Vietnam highlight when relevant:

```
# Web3 Opportunities — <facet summary>
_Bundled baseline as of <data_as_of>. Verify time-sensitive fields (*) live before applying._

## Grants (non-dilutive)
- **<name>** — <chains> · <regions> · <stage> — <check/prize>* — <status>* — <url>
...

## Accelerators (dilutive)
- ...

## Hackathons / Bounties / Retroactive funding / Fellowships / Education
- ...

## SEA / Vietnam highlight
- <entries where sea_relevant = true; includes VN student/education programs
  (Corelia Academy, UniHackfest, VBI Academy) and community ramps (Superteam Vietnam)>

## Next steps
- The 2-3 best fits to verify live now (deadline / open cohort), and which source to check.
(* = time-sensitive baseline snapshot)
```

## Critical Rules

- ALWAYS run `query_opportunities.py` before listing opportunities. Never invent programs.
- NEVER present `status`, `cadence`, `typical_check_or_prize`, or a deadline as current
  without either labeling it baseline-as-of-`last_verified` or live-verifying it.
- When the query returns zero matches, say so plainly and offer the live-lookup path via
  `references/sources.md` rather than fabricating entries or loosening facts silently.
- When the user is regionally focused (especially SEA / Vietnam), surface the
  `sea_relevant` entries explicitly.
- If the roster is missing a program the user names, find it live via the Tier-2
  aggregators in `references/sources.md` and offer to add it to the data file.

## Reference files

- `data/web3_opportunities.json` — the bundled roster (stable fields + time-sensitive
  baselines + facet enums).
- `references/sources.md` — tiered registry of official program pages and aggregators for
  refreshing time-sensitive fields and discovering programs not yet in the roster.

## Prerequisites

- Python 3.10+. No API key required for the bundled catalog (fully offline).
- The live-enrichment layer needs web access (`WebSearch`/`WebFetch`); it is optional —
  the catalog answers structural questions on its own.
