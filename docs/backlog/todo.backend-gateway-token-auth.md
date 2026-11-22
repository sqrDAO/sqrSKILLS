# Authenticate the YouAI backend fallback with the gateway token
**Deps**: —

## Goal
`list_chats.py` and `list_groups.py` call YouAI's `GET /api/twins/{id}/telegram/chats`
with `Authorization: Bearer {YOUAI_TWIN_ID}`. YouAI stopped accepting the public twin
ID as a credential (its `legacy-twin-token` work), so the fallback has returned 401 ever
since and the skills silently list nothing when local sessions are empty. Send the
twin's secret `OPENCLAW_GATEWAY_TOKEN` instead, and fail clearly when it is missing.

## Files
- `list-telegram-chats/scripts/list_chats.py` (edited) — bearer = `OPENCLAW_GATEWAY_TOKEN`;
  missing token with the backend configured → JSON error, exit 1.
- `telegram-send/scripts/list_groups.py` (edited) — same fix (same endpoint, same bug);
  `use_backend` flag.
- `telegram-send/scripts/send.py` (edited) — `--keyword` matches local sessions only.
- `list-telegram-chats/SKILL.md`, `telegram-send/SKILL.md` (edited) — document the
  variable; PATCH bumps.
- `README.md`, `AGENTS.md` (edited) — env var tables.
- `tests/test_remaining_skills.py` (edited) — header and missing-token regression tests.

## Acceptance
- [ ] The backend request carries `Authorization: Bearer <OPENCLAW_GATEWAY_TOKEN>` and
      never the twin ID.
- [ ] `YOUAI_API_URL` + `YOUAI_TWIN_ID` set, token unset, no local sessions → stdout is
      `{"error": ...}` naming `OPENCLAW_GATEWAY_TOKEN`, exit status 1.
- [ ] Backend answers 401/403 → `{"error": ...}`, exit 1 (not a silent empty list).
- [ ] `send.py --keyword` never calls the backend, so the token can't leave via it.
- [ ] Backend not configured (no `YOUAI_API_URL`) → unchanged: empty result, exit 0.
- [ ] NOT: the token is ever printed, logged, or sent to any host but `YOUAI_API_URL`.
- [ ] NOT: changing the local-session sources or their priority.

## Verify
- `python3 scripts/validate_skills.py` → passes
- `python3 -m unittest discover -s tests -v` → passes
- YouAI staging: Telegram twin with empty `sessions.json` runs `list_chats.py` → backend 200, chats listed

## Notes
YouAI injects `OPENCLAW_GATEWAY_TOKEN` in every twin container (fail-closed in
`twin_provisioner._build_openclaw_env`) and sets `YOUAI_API_URL`/`YOUAI_TWIN_ID` only
for Telegram twins. The endpoint compares the bearer with the token via `hmac.compare_digest`.
The destination comes from `YOUAI_API_URL`, which an agent can override per run (OpenClaw's
exec `env` parameter). Because the scripts now send a secret there, YouAI takes them off its
no-prompt exec allowlist, so the user approves each run.
