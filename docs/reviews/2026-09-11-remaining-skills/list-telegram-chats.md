# list-telegram-chats 0.1.1 — audit

Read: `SKILL.md` and `scripts/list_chats.py`. Verdict: small targeted corrections,
plus an explicit supported-runtime contract.

## Confirmed findings

1. **P2 — Nanobot last-updated metadata is silently omitted.**
   `scripts/list_chats.py:81` reads `last_updated` or `timestamp`; Nanobot's
   metadata record writes `updated_at`. A fixture containing a valid metadata
   header and updated_at is returned with chat_id only. This prevents recency
   information from reaching the agent even when available. Fix: recognize
   updated_at as the canonical metadata field, retaining documented legacy
   variants where useful. [Nanobot writer and reader](https://raw.githubusercontent.com/HKUDS/nanobot/a2e33893e1ca95f5a06af86ec2438ef3c5958540/nanobot/session/manager.py) (retrieved 2026-09-11).

2. **P3 — Results depend on directory enumeration order.**
   `scripts/list_chats.py:58` obtains unsorted names, and `_merge` at line 161
   preserves insertion order through the final result. Two identical session
   sets produce opposite group orders in the fixture. Fix: define a total final
   order, with chat_id as a tie-break if sorting by recency/name.

## Further improvements

- `scripts/list_chats.py:99` hardcodes `agents/main` and a deployment-specific
  default. The helper supports a particular legacy JSON layout, not every
  OpenClaw agent or installation. Current [OpenClaw storage documentation](https://docs.openclaw.ai/concepts/session)
  describes SQLite. Add versioned adapters or explicitly narrow support; test
  migrations against exported fixtures before claiming compatibility.
- `SKILL.md:43` lists sources as checked in order, but the script merges both
  local sources before backend fallback (`scripts/list_chats.py:210`). Explain
  merging and source precedence instead of implying first-hit lookup.
- A config path beginning with `~` is not expanded in this helper (line 35),
  unlike send.py. Normalize user-configured paths consistently.
- Empty results cannot distinguish no known chats from missing/incompatible
  state. Expose source/status metadata so an agent can avoid a false “no chats”
  conclusion. Prompt changes remain UNGATED.
- Review the broad “what groups am I in” wording: this discovers the bot's
  recorded contacts, not the user's full Telegram account membership.

## Common rubric

| Dimension | /5 | Evidence |
|---|---:|---|
| Anti-patterns | 2 | `SKILL.md:7` clarifies that this is a helper, not an MCP tool |
| Actionability | 4 | `SKILL.md:24` includes a credential-free --no-names command |
| Triggering | 3 | `SKILL.md:5` overlaps personal-account membership language |
| Progressive disclosure | 4 | `SKILL.md:24` reaches the single bundled helper |
| Gating readiness | 2 | `scripts/list_chats.py:44` is locally fixtureable; live names need mocks |
| Structural correctness | 2 | `scripts/list_chats.py:81` misses the writer's metadata field |

Verification: offline `chat_order` evidence includes both ordering reversal and
missing timestamps. No real session files or bot names were read.
