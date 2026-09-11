# luma-calendar 0.1.1 — audit

Read: `SKILL.md` and `scripts/luma_calendar.py`, current public OpenAPI schema
and documentation. Verdict: improve error handling; investigate contract drift
without declaring legacy routes broken based only on renamed documentation.

## Confirmed finding

**P2 — Transport errors bypass the promised structured error interface.**
`scripts/luma_calendar.py:35` and `:58` catch HTTPError only. A DNS/connectivity
URLError escapes; main does not catch it and exits with a traceback rather than
JSON. The mocked outage reproduces the uncaught URLError. Missing credentials
also only print stderr (line 21). Fix: one structured error envelope with exit 1
for transport, HTTP, credential, and decoding failures. Do not automatically
retry a write when its completion is unknown.

## API compatibility work — not a confirmed live outage

The helper uses `/v1/user/*`, `/v1/calendar/*`, `/v1/event/*`, `api_id`,
`event_api_id`, `description`, and `url` (script lines 68–132). Current
[OpenAPI](https://public-api.luma.com/openapi.json) documents plural resources;
event retrieval uses `event_id`, and creation uses `description_md` and `slug`.
Creation requires `name`, `start_at`, and `timezone`; the CLI requires only name.
The documented venue example also differs from the current typed manual/Google
address alternatives. [Current creation contract](https://docs.luma.com/reference/post_v1-events-create).

However, [Luma API conventions](https://docs.luma.com/reference/api-conventions)
explicitly preserve some older routes for compatibility. No authenticated
request was made, so neither missing fields nor rejected legacy paths are
claimed as reproduced production failures. Before migration, verify the legacy
contract or use the published current one with recorded request/response fixtures.
Change routes, payload keys, and response interpretation together.

## Further improvements

- `SKILL.md:58` labels an unfiltered list command “upcoming”; the probe confirms
  `cmd_list_events` supplies no after parameter. Make the example use an explicit
  current cutoff rather than relying on unspecified legacy server defaults.
- `SKILL.md:110` exposes pagination flags, but the workflow never instructs the
  agent to consume all pages before answering “how many people signed up”. Add
  pagination/completeness handling; this is an UNGATED agent-behavior proposal.
- The Hanoi event example supplies 18:00Z alongside Vietnam's display timezone;
  that instant is 01:00 the next day locally. Explain offset conversion so the
  example does not encourage interpreting Z as local time.
- The trigger “or get calendar information” is broader than Luma. Explicitly
  scope generic calendar requests when another calendar skill is installed.
- Document the current Luma Plus requirement. [API prerequisites](https://docs.luma.com/reference/getting-started-with-your-api).

## Common rubric

| Dimension | /5 | Evidence |
|---|---:|---|
| Anti-patterns | 1 | `SKILL.md:121` covers errors but not incomplete lists or ambiguous times |
| Actionability | 3 | `SKILL.md:35` gives commands, but creation requirements need reconciliation |
| Triggering | 3 | `SKILL.md:5` includes an unqualified calendar trigger |
| Progressive disclosure | 4 | `SKILL.md:35` links the single helper; command table is compact |
| Gating readiness | 1 | `scripts/luma_calendar.py:26` needs contract fixtures and account checks |
| Structural correctness | 2 | `scripts/luma_calendar.py:35` leaves transport failures unstructured |

Verification: offline keys `luma_*`; primary docs and schema read on 2026-09-11.
No event was created and no guest was added or notified. Pagination, legacy
compatibility, and live calendar behavior remain unverified.
