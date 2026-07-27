# Refresh Vietnam crypto regulatory baseline
**Deps**: repository-harness

## Goal
Refresh `vietnam-crypto-radar` from current primary Vietnamese government sources so
its dated baseline covers newly enacted enforcement rules and omitted tax,
accounting, and electronic-invoice instruments without presenting drafts as law.

## Files
- `vietnam-crypto-radar/SKILL.md` (edited) — expand triggers and bump patch version
- `vietnam-crypto-radar/references/baseline.md` (edited) — verified instrument tracker
- `vietnam-crypto-radar/references/sources.md` (edited) — primary anchors and queries
- `vietnam-crypto-radar/references/glossary.md` (edited) — Decree 284 terminology
- `docs/backlog/PRIORITY.md` (edited) — rank this open spec
- `docs/backlog/todo.vietnam-crypto-radar-regulatory-refresh.md` (new) — task spec

## Acceptance
- [x] Baseline carries a `LAST VERIFIED` date of 18 July 2026
- [x] Decree 284/2026/NĐ-CP is classified as enacted, effective 1 September 2026
- [x] Enforcement guidance distinguishes organizational and individual fine levels
- [x] Circular 15, Decrees 253 and 254, and Circular 87 appear in their correct roles
- [x] Primary government links support every added instrument
- [x] Skill version is bumped from `0.4.0` to `0.4.1`
- [x] No official pilot license grant is asserted without a primary source
- [x] NOT: present Decree 284 penalties as effective before 1 September 2026
- [x] NOT: treat crypto asset recognition as authorization to use crypto for payment

## Verify
- `python3 scripts/validate_skills.py` → JSON with `"ok": true`
- `python3 -m unittest discover -s tests -v` → all tests pass
- `git diff --check` → no whitespace errors
- `rg -n "284/2026|253/2026|254/2026|87/2026|15/2026" vietnam-crypto-radar` → updated instruments are discoverable

## Notes
Primary-source sweep completed on 18 July 2026. Decree 284 was issued on 16 July;
the other added instruments repair omissions in the prior 6 July baseline.
