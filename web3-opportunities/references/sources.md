# web3-opportunities — Live-Lookup Source Registry

This registry is for refreshing the **time-sensitive** fields of the bundled roster
(`status`, `cadence`, `typical_check_or_prize`, deadlines) and for discovering programs not
yet in `data/web3_opportunities.json`. STABLE facets (type, stage, dilution, chains,
regions) come from the roster itself and do not need live lookups.

**Verification rule:** a time-sensitive fact is "live-verified" only when confirmed on the
program's official page (Tier 1) OR on two independent aggregators (Tier 2). Otherwise label
it `[bundled baseline · as of <last_verified>]`.

## Tier 1 — Official program pages (authoritative)

The canonical source for a given program's current deadline, cohort window, and prize/check.
Each roster entry's `url` is its Tier-1 source. Key ones:

| Program | URL | Use for |
|---|---|---|
| a16z CSX | https://a16zcrypto.com/csx/ | Next cohort window, terms |
| Alliance DAO | https://alliance.xyz/ | Batch status, application |
| Outlier Ventures | https://outlierventures.io/base-camp/ | Track + cohort status |
| Colosseum (Solana) | https://www.colosseum.com/hackathon | Hackathon dates, prize pool |
| ETHGlobal | https://ethglobal.com/events | Event calendar, prize pools |
| Ethereum Foundation ESP | https://esp.ethereum.foundation/ | Open wishlist / RFPs |
| Arbitrum Foundation Grants | https://arbitrum.foundation/grants | Active tracks, amounts |
| Optimism Grants / Retro Funding | https://app.optimism.io/grants · https://retrofunding.optimism.io/ | Season/round status |
| Base Grants | https://www.base.org/grants | Current round format |
| Web3 Foundation (Polkadot) | https://grants.web3.foundation/ | Open application, milestones |
| Interchain Foundation (Cosmos) | https://interchain.io/ | Funding vehicles, RFPs |
| NEAR funding | https://near.org/ecosystem/get-funding | Program funding |
| Sui Foundation Grants | https://sui.io/grants | Focus areas, rounds |
| Filecoin devgrants | https://github.com/filecoin-project/devgrants | Open proposals/RFPs |
| Gitcoin | https://www.gitcoin.co/ | Grant rounds, bounties |
| Immunefi | https://immunefi.com/ | Live bug bounties |

## Tier 2 — Aggregators / directories (discovery)

Best for finding NEW programs not yet in the roster, and for cross-checking a fact against
a second source.

| Source | URL | Covers |
|---|---|---|
| ETHGlobal calendar | https://ethglobal.com/events | Ethereum hackathon schedule |
| Colosseum | https://www.colosseum.com/ | Solana hackathons + accelerator |
| DoraHacks | https://dorahacks.io/hackathon | Multi-chain hackathons + grant rounds |
| Gitcoin Grants | https://explorer.gitcoin.co/ | Quadratic-funding rounds |
| DappRadar grants | https://dappradar.com/ | Cross-ecosystem grant tracker |
| InnMind | https://innmind.com/ | Web3 grants/opportunities database |
| Immunefi | https://immunefi.com/bug-bounty/ | Security bounty directory |
| Web3 grant roundups | e.g. rocknblock, hashlock, onchain.org listicles | Periodic "grants to apply" lists |

## Tier 3 — Ecosystem / regional signal (fast, noisier)

Early signal; always confirm against Tier 1 before stating a fact. Useful for the SEA
highlight and for fresh announcements.

| Source | Covers |
|---|---|
| Ecosystem foundation blogs / X accounts | New programs, deadline changes, prize announcements |
| sqrDAO (Vietnam/SEA) — https://sqrdao.com/ | Regional bounties, hackathon support |
| Coin98 / Kyros Ventures (Vietnam) | SEA-focused investment + programs |
| Hashed Emergent (India/SEA) | Emerging-markets web3 cohorts |
| Tribe Accelerator (Singapore) | SEA enterprise-backed cohorts |
| Sky Mavis / Ronin (Vietnam) | Gaming/consumer ecosystem grants |

## Query patterns that work

- `"<program name>" application deadline 2026`
- `<chain> ecosystem grants open` (e.g. `Arbitrum ecosystem grants open`)
- `Solana hackathon schedule 2026` · `ETHGlobal 2026 calendar`
- `RetroPGF round status` · `Optimism Retro Funding mission`
- `Web3 grants Southeast Asia Vietnam` · `crypto accelerator Singapore cohort`
