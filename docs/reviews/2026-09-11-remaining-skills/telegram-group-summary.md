# telegram-group-summary 0.1.1 — audit

Read: `SKILL.md` and `scripts/fetch_messages.py`. Verdict: fix first.

## Confirmed findings

1. **P1 — The fallback changes the bot's update subscription.**
   `scripts/fetch_messages.py:114` sends `allowed_updates=["message"]` on every
   getUpdates call. Telegram retains that setting for later requests that omit
   it. A bot previously receiving callback queries or channel posts can stop
   receiving those types after a summary request. Omitting an offset avoids
   acknowledging messages, but does not make this call passive. This contradicts
   `SKILL.md:93`. The probe captures the exact query without contacting Telegram.
   Implemented in `0.1.2`: the helper omits subscription-setting arguments and
   filters locally. Telegram reuses its previous filter when `allowed_updates`
   is omitted, so local filtering cannot restore update types excluded by
   another poller; coordinated subscription ownership is still required when
   sharing a polling bot. [Telegram contract](https://core.telegram.org/bots/api#getupdates).

2. **P1 — The primary reader cannot read the documented transcript storage.**
   `scripts/fetch_messages.py:84` skips every file except `.json`; OpenClaw's
   JSONL-era transcripts use `<sessionId>.jsonl`, while sessions.json is an index.
   The probe returns no messages for a JSONL file and one for identical JSON.
   The parser also expects raw Telegram `chat/date/text` records, so merely
   adding a suffix is insufficient for native transcript envelopes. The helper
   now reads raw Telegram-shaped JSON and JSONL records; native OpenClaw
   envelopes still need a versioned adapter tied to the target session and its
   message schema before they can be claimed as supported.
   [Versioned OpenClaw storage contract](https://raw.githubusercontent.com/openclaw/openclaw/v2026.7.1-1/docs/concepts/session.md).
   Current [OpenClaw docs](https://docs.openclaw.ai/concepts/session) describe
   SQLite storage; declare which versions are supported instead of promising a
   generic recursive state scan. Neither runtime was exercised live.

3. **P2 — Time filtering uses the host timezone twice.**
   `scripts/fetch_messages.py:202` takes naive `utcnow()` and calls `.timestamp()`,
   which treats it as local time. With Asia/Ho_Chi_Minh, a 24-hour request includes
   31 hours. In negative UTC offsets it omits recent messages instead. Probe:
   cutoff is seven hours too early. Fix: aware UTC datetime or epoch subtraction.

4. **P2 — Supported content is silently lost.**
   `scripts/fetch_messages.py:60` requires `text`, excluding caption-only local
   messages even though normalization supports captions. Line 132 reads only
   `message`, ignoring `channel_post`, despite the channel-digest trigger.
   Both return empty in fixtures. Fix: recognize the advertised message variants
   and preserve stable chat/message identities for deduplication.

## Further improvements

- `SKILL.md:32` requires a sibling telegram-send installation without a fallback;
  a standalone install fails during group resolution. Accept an explicit chat
  ID and resolve companions by their actual install paths when present.
- The documented `/twin-data/state` default is not implemented (script line 77).
- `--limit 0` returns all matches (line 104); reject nonpositive limits. Timestamp
  sorting has no tie-break, and the 60-character deduplication fallback can
  collapse distinct messages. Define stable identity and total ordering.
- `SKILL.md:86` recommends a smaller time window after no data; that removes
  more messages. Recommend a wider window. Label Bot API output as incomplete:
  one batch is at most 100 pending updates across all chats, not full history.
  The fallback calls `getUpdates` without an offset, keeps no cursor, and may
  return the same pending updates on repeated summaries until another consumer
  confirms them.
- Treat instructions embedded in fetched chat messages as source material.
  This is an UNGATED prompt hardening proposal, not a demonstrated agent failure.

## Common rubric

| Dimension | /5 | Evidence |
|---|---:|---|
| Anti-patterns | 2 | `SKILL.md:83` has recovery guidance, but one action is reversed |
| Actionability | 3 | `SKILL.md:44` gives runnable commands and bounds |
| Triggering | 2 | `SKILL.md:5` advertises channels the parser ignores |
| Progressive disclosure | 2 | `SKILL.md:32` makes an unbundled sibling mandatory |
| Gating readiness | 1 | `scripts/fetch_messages.py:107` needs source fixtures; no dedicated tests |
| Structural correctness | 1 | `scripts/fetch_messages.py:84`, `:114`, `:202` contradict core promises |

Verification: offline probe keys `summary_*`; primary-source contract checks.
No messages sent, real updates fetched, or subscription settings changed.
