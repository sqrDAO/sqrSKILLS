# telegram-send 0.1.1 — audit

Read: `SKILL.md`, `scripts/send.py`, `scripts/list_groups.py`. Verdict: retain the
lookup-before-send workflow; correct serialization and literal-text handling.

## Confirmed findings

1. **P2 — Formatting is applied inside code spans and fenced blocks.**
   `scripts/send.py:28` converts code first, then lines 39–48 run formatting
   regexes across the resulting HTML. The input `` `user_name_here` `` becomes
   `<code>user<i>name</i>here</code>`; a Python block containing `a_b_c` is also
   changed. Literal underscores are removed and unsupported nested markup can
   trigger the plain-text fallback. Fix: tokenize/protect code regions before
   formatting prose, then HTML-escape and render each region once. Preserve
   intentional literals through both normal and fallback requests.

2. **P2 — Successful sends break the repository's JSON stdout contract.**
   `scripts/send.py:173` prints `Message sent to chat -1001`, reproduced with
   the send function mocked. Keyword fan-out emits prose at lines 146–153, with
   failures only on stderr. Structured callers cannot reliably associate partial
   success with each recipient or avoid retrying already-successful recipients.
   Fix: one JSON result with per-chat success/error records and message IDs;
   keep progress and diagnostics on stderr. The lower-level send discards the
   returned message ID at lines 77–79, so preserve it as part of that change.

## Further improvements

- `scripts/list_groups.py:60` inherits filesystem order; the opposite-order
  fixtures return opposite group orders. Sort the final deduplicated results by
  a stable unique key such as chat_id (P3).
- `scripts/list_groups.py:83` requires OPENCLAW_STATE_DIR; the sibling chat-list
  helper defaults to `/twin-data/state`. Unify the documented source contract,
  including supported runtime versions and agents. The current generic
  OpenClaw compatibility claim needs review as storage formats evolve.
- README's environment table incorrectly requires YouAI variables even though
  they are an optional discovery fallback in `SKILL.md:29` (P3).
- Ambiguous names need explicit disambiguation before selecting a single target;
  the existing prohibition on invented IDs does not define this (`SKILL.md:83`).
  Proposed prompt behavior is UNGATED; no real wrong-recipient send was observed.
- A known exact chat ID should remain usable even if local discovery is empty.
  No-match does not prove the bot has never interacted with the group: the
  configured source may be absent, stale, or unavailable.

## Common rubric

| Dimension | /5 | Evidence |
|---|---:|---|
| Anti-patterns | 3 | `SKILL.md:89` explicitly prohibits invented chat IDs |
| Actionability | 4 | `SKILL.md:54` and `:68` document both send modes |
| Triggering | 4 | `SKILL.md:5` targets sending; related list skill is linked |
| Progressive disclosure | 4 | `SKILL.md:37` and `:59` reach both bundled scripts |
| Gating readiness | 1 | `scripts/send.py:53` needs transport fixtures, not real sends |
| Structural correctness | 2 | `scripts/send.py:39` and `:173` violate text/output contracts |

Verification: offline probe keys `send_*` and `group_order`. Basic bold conversion
is a positive control. Actual Telegram delivery and HTML acceptance were not tested.
