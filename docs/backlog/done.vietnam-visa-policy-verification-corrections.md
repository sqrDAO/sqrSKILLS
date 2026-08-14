# Correct Vietnam arrival-policy verification

**Deps**: vietnam-visa-nationality-resolution

## Goal
Correct the arrival-declaration and Timor-Leste facts left in `vietnam-visa-check`
after PR #25, and bind them to primary Vietnamese government sources so a later
refresh cannot restore the disproven claims.

## Files
- `vietnam-visa-check/data/vietnam_immigration_policy.json` (edited) — correct policy facts and source registry
- `vietnam-visa-check/SKILL.md` (edited) — bump patch version and verification date
- `tests/test_vietnam_visa_check.py` (edited) — guard corrected policy facts
- `README.md` (edited) — synchronize the public verification date
- `docs/backlog/PRIORITY.md` (edited) — track this open spec
- `docs/backlog/todo.vietnam-visa-policy-verification-corrections.md` (new) — implementation spec

## Acceptance
- [x] Health declarations are described as conditional, not routinely mandatory for all travelers
- [x] Pre-arrival Information is described as an optional Tan Son Nhat pilot, not mandatory at five airports
- [x] The Digital Arrival Card fields agree with the policy summary and name the official portal
- [x] Timor-Leste remains routed to e-Visa until entry into force is confirmed
- [x] Timor-Leste's signing/exchange date is 9 June 2026; the unsupported 23 July date is absent
- [x] Corrected claims cite Tier-1 Government, Ministry of Public Security, or Foreign Ministry sources
- [x] Regression tests fail if the blanket requirements or wrong signing date return
- [x] `vietnam-visa-check` version is bumped from `0.3.4` to `0.3.5`
- [x] README inventory reflects the 14 August 2026 arrival-policy verification
- [x] NOT: infer a nationwide PAI rollout or an in-force ordinary-passport exemption without a primary source

## Verify
- `python3 scripts/validate_skills.py` → JSON with `"ok": true`
- `python3 -m unittest discover -s tests -v` → all tests pass
- `python3 vietnam-visa-check/scripts/query_visa.py --nationality TL` → `EVISA`
- `rg -n "five international airports|reported signed 23 July|mandatory health declaration for all" vietnam-visa-check` → no matches
- `git diff --check` → no whitespace errors

## Notes
Primary anchors: Government health clarification (1 Jul 2026), Ministry of Public
Security PAI notice (13 May 2026), and Government/MOFA reporting from 9 Jun 2026.
Completion approved by the user on 14 August 2026 after local verification.
