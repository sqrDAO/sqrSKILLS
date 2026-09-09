# Adopt the full-text rule and Resolution 05's load-bearing provisions
**Deps**: —

## Goal
An exported copy of `vietnam-crypto-radar` (`vietnam-crypto-radar.skill`, authored
2026-09-05 outside this repo) carries SKILL.md hardening that never landed here:
`git log -S "Load-bearing provisions"` returns nothing. Three legal errors reached a
report sent to Da Nang city leadership, all from citing summaries instead of opening
the provision — a real 6-month clause denied as rumour, a nationality condition
invented inside a capital requirement, and a licensing ceiling read as closing a
province permanently. Bring that prose in.

Take the prose only. The export's `references/baseline.md` is the 2026-08-31
snapshot, a week behind `main`, and it contradicts its own SKILL.md: it still calls
the 6-month trigger UNVERIFIED while the SKILL.md asserts the clause is real. The
2026-09-07 sweep (#51) already resolved that in the baseline's favour. Its
frontmatter is also stripped by the export round-trip (no `version`, no
`allowed-tools`, no `metadata.nanobot`, description cut 1999 -> 317 chars).

## Files
- `vietnam-crypto-radar/SKILL.md` (edited) — full-text rule, load-bearing
  provisions of Resolution 05, `CONFLICTING` status, issue-vs-effective dates,
  sharpened triggers; version 0.5.1 -> 0.6.0
- `docs/backlog/PRIORITY.md` (edited) — track this spec

## Acceptance
- [ ] The verification section states the full-text rule and that it overrides the
      two existing rules, including that absence of confirmation in the wrong
      document is not disproof.
- [ ] A "Load-bearing provisions of Resolution 05/2025/NQ-CP" section quotes Dieu 7
      khoan 2, Dieu 8 khoan 3 diem a, and Dieu 11, and states the 05-provider ceiling.
- [ ] Dieu 8 khoan 3 diem a is recorded as carrying no nationality condition, with
      the 49% foreign cap named as the separate diem d.
- [ ] `CONFLICTING` appears in the step-5 status list and has a stated usage rule.
- [ ] The instrument tracker asks for `Issued` and `Effective` as separate columns.
- [ ] NOT: any change to `references/baseline.md` or the other four reference files.
- [ ] NOT: any frontmatter loss — `version`, `allowed-tools` and `metadata.nanobot`
      survive, and the 1999-char description is unchanged.
- [ ] NOT: a new legal instrument asserted without an anchor.

## Verify
- `python3 scripts/validate_skills.py` -> exit 0
- `python3 -m unittest discover -s tests` -> all pass
- `python3 scripts/check_unanchored.py --since origin/main` -> no new unanchored
  instrument
- `git diff --stat origin/main -- vietnam-crypto-radar/` -> `SKILL.md` only
- `grep -c "nanobot" vietnam-crypto-radar/SKILL.md` -> 1

## Notes
The export's factual claims about Decision 2895's conflicting issue date and the
IFC instrument dates are already consistent with the current baseline; they enter
as trigger guidance, not as new baseline facts, so no anchor is added.
