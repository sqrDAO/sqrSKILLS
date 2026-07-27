# Vietnam visa nationality resolution

**Deps**: —

## Goal
Make `vietnam-visa-check` resolve the nationality strings users actually type —
demonyms ("Russians"), qualified forms ("Russian citizens"), abbreviations
("UK", "USA") — and never return a hard failure or a silently wrong pathway.
Triggered by a chat transcript where "Hows the visa for Russians?" produced a
raw `run … query_visa.py failed` bubble in the user's conversation.

## Defects
1. Demonyms unresolvable — `resolve_nationality()` matches only ISO2, dataset
   country names, and 17 aliases. `Russians` → error.
2. `sys.exit(1)` on unrecognised input (`scripts/query_visa.py:152`) renders as a
   tool-failure bubble to the end user; the agent already gets JSON on stdout.
3. The "looks like ISO2" shortcut (`scripts/query_visa.py:73`) runs *before* the
   alias index and accepts 1–3 letters, so aliases never apply: `UK`→`UK`
   (`EVISA`) instead of `GB` (`VISA_FREE`, 45 days) — a confident, silent, wrong
   answer telling a British traveller to buy a USD 25 e-Visa. `USA`→`USA`
   (display name "Usa"). `XYZ`→`XYZ` (`EVISA`, no error).
4. Unknown 2-letter codes answer `EVISA` with no note that nothing matched.
5. `--nationality VN` returns `EVISA`; Vietnamese citizens need no visa.

## Files
- `vietnam-visa-check/scripts/query_visa.py` (edited) — resolution rewrite
- `vietnam-visa-check/SKILL.md` (edited) — inputs, error contract, bump `0.3.0`
- `tests/test_vietnam_visa_check.py` (new) — resolution regression tests
- `docs/backlog/PRIORITY.md` (edited) — queue entry
- `docs/backlog/todo.vietnam-visa-nationality-resolution.md` (new) — this spec

## Design
Resolution order, first match wins: (1) normalize — casefold, collapse
whitespace, strip punctuation, drop leading `the`, drop trailing
`citizen(s)`/`national(s)`/`passport holder(s)`/`passport`/`nationality`/
`people`/`tourist(s)`/`traveller(s)`; (2) exact lookup in the combined index of
dataset names + dataset ISO2 + `_ALIASES` + `_DEMONYMS`; (3) retry with a
trailing `s` stripped (`russians`→`russian`) — plural country names (`laos`,
`philippines`, `netherlands`) already matched at step 2; (4) exactly two alpha
characters → accept as ISO2; (5) otherwise unresolved.

Tables, stdlib only: `_DEMONYMS` (demonym → ISO2 for all 50 dataset countries
plus ~30 common travel nationalities absent from it; several per country where
they exist — `british`/`briton`/`brit`/`english`/`scottish`/`welsh` → `GB`);
`_COUNTRY_NAMES` (ISO2 → display name, so output reads "United States", not
`str.title()`'s "Usa"); `_ALIASES` extended with `burma`, `holland`, `uae`,
`the philippines`, `slovak republic`.

Error contract: unresolved input prints `{error, hint, suggestions}` and exits
**0**; `suggestions` from `difflib.get_close_matches` over index keys. `OSError`
on data load keeps exit 1 — an install fault, not user input.

New `notes[]`: unmatched 2-letter code → "`<XX>` is not in this dataset's
exemption list; the e-Visa pathway shown applies to all nationalities."
`iso2 == "VN"` → "Vietnamese citizens do not need a visa to enter Vietnam."

## Acceptance
- [ ] `Russians`, `Russian`, `russians`, `"Russian citizens"` → `RU`,
      `VISA_FREE`, 45 days
- [ ] `UK` → `GB`, `VISA_FREE`, 45 days; `USA` → `US`, "United States"
- [ ] Every country in both dataset country lists is reachable by ≥1 demonym
- [ ] `XYZ` → structured error with `suggestions`, exit 0
- [ ] No input path exits non-zero except an unreadable/invalid data file
- [ ] Unmatched 2-letter codes carry the "not in dataset" note; `VN` carries the
      Vietnamese-citizen note
- [ ] `--phu_quoc_only` unchanged for every resolvable nationality
- [ ] SKILL.md documents demonym input and the exit-0 error contract
- [ ] NOT: a bundled full ISO 3166 table, fuzzy matches applied silently
      (suggestions are returned, never auto-accepted), or a non-stdlib dependency

## Verify
- `… --nationality Russians` → `iso_alpha2: "RU"`, `VISA_FREE`, exit 0
- `… --nationality UK` → `"GB"`, `"VISA_FREE"`
- `… --nationality XYZ; echo $?` → JSON with `suggestions`, then `0`
- `python3 scripts/validate_skills.py` → `"ok": true`
- `python3 -m unittest discover -s tests -v` → all tests pass

## Notes
Defect 3 is why this is more than UX polish: the reported symptom was a visible
error, but the same root cause silently misadvises anyone typing "UK".
