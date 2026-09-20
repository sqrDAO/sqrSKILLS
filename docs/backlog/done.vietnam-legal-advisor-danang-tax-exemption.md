# vietnam-legal-advisor: Da Nang tax-exemption confirmation (NQ 24/2026)
**Deps**: —

## Goal
The skill had no coverage of how a Da Nang startup, semiconductor or AI company
gets the So KH&CN confirmation letter it needs before claiming the
Resolution 136/2024/QH15 exemptions. Add a reference built from the DSAC briefing
deck on Nghi quyet 24/2026/NQ-HĐND (presented 07/8/2026) and route to it.

## Files
- `vietnam-legal-advisor/references/danang-tax-exemption-confirmation.md` (new) — eligibility, conditions, dossiers, channels, council, deadlines, signing authority, open questions
- `vietnam-legal-advisor/SKILL.md` (edited) — description trigger, domain routing row, reference index; 0.1.1 → 0.2.0
- `vietnam-legal-advisor/references/tax-compliance.md` (edited) — section 8 pointer
- `README.md` (edited) — reference count
- `docs/backlog/PRIORITY.md` (edited) — queue entry

## Acceptance
- [ ] The reference is labelled REPORTED / SINGLE-SOURCE and names the deck as its only detailed source, plus the press anchor for existence
- [ ] It states the output is a confirmation letter, not money or a tax amount, and sends rates to 136/2024/QH15 and 259/2025/QH15
- [ ] It records effective date 10/6/2026 and the replacement of 53/2024 and 59/2024
- [ ] It flags the deck's own inconsistency (Dieu 17.1.c "mau so 04" vs Appendix I forms I-01 to I-03)
- [ ] NOT: press-reported 5-year CIT/PIT figures attributed to NQ 24
- [ ] NOT: third-party vendor contact details from the deck copied into the skill

## Verify
- `python3 scripts/validate_skills.py` → ok
- `python3 -m unittest discover -s tests` → all pass
- `rg -n "24/2026/NQ-H" vietnam-legal-advisor` → SKILL.md, tax-compliance.md and the new reference

## Notes
Signed text not retrieved (congdulieu.vn path 403 on 2026-09-19). When it is,
verify every article number in the reference and drop the SINGLE-SOURCE label.
vietnam-legal-advisor has no eval split, so no split run gates this change.
