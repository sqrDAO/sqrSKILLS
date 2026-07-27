# Vietnam visa nationality resolution

**Deps**: —

## Goal
Make `vietnam-visa-check` resolve the nationality strings users actually type —
demonyms ("Russians"), qualified forms ("Russian citizens"), abbreviations
("UK", "USA") — and never return a hard failure or a silently wrong pathway.
Triggered by a chat transcript where "Hows the visa for Russians?" produced a
raw `run … query_visa.py failed` bubble in the user's own conversation.

## Defects
1. Demonyms unresolvable — `resolve_nationality()` matches only ISO2, dataset
   country names, and 17 aliases. `Russians` → error.
2. `sys.exit(1)` on unrecognised input (`query_visa.py:152`) renders as a
   tool-failure bubble to the user; the agent already gets JSON on stdout.
3. The "looks like ISO2" shortcut (`scripts/query_visa.py:73`) runs *before* the
   alias index and accepts 1–3 letters, so aliases never apply: `UK`→`UK`
   (`EVISA`) instead of `GB` (`VISA_FREE`, 45 days) — a confident, silent, wrong
   answer telling a British traveller to buy a USD 25 e-Visa. `USA`→`USA`
   (name "Usa"). `XYZ`→`XYZ` (`EVISA`, no error).
4. Unknown 2-letter codes answer `EVISA` with no note that nothing matched.
5. `--nationality VN` returns `EVISA`; Vietnamese citizens need no visa. A note
   alone will not do — `recommended_pathway`/`evisa_option` must not contradict
   it (raised in review of PR #20).

## Files
- `vietnam-visa-check/scripts/query_visa.py` (edited) — resolution rewrite
- `vietnam-visa-check/SKILL.md` (edited) — inputs, error contract, bump `0.3.0`
- `tests/test_vietnam_visa_check.py` (new) — resolution regression tests
- `docs/backlog/PRIORITY.md` (edited) — queue entry
- `docs/backlog/todo.vietnam-visa-nationality-resolution.md` (new) — this spec

## Design
Resolution order, first match wins: (1) normalize — casefold, collapse
whitespace, strip punctuation, drop a leading `the` and trailing qualifiers
(`citizens`, `nationals`, `passport holders`, …); (2) exact lookup in the
combined index of dataset names + dataset ISO2 + `_ALIASES` + `_DEMONYMS`;
(3) retry with a trailing `s` stripped (`russians`→`russian`) — plural country
names (`laos`, `philippines`) already matched at step 2; (4) exactly two alpha
characters → accept as ISO2; (5) otherwise unresolved.

Tables, stdlib only: `_DEMONYMS` (demonym → ISO2 for all 50 dataset countries
plus ~30 common travel nationalities absent from it, several forms per country —
`british`/`briton`/`brit`/`english`/`scottish`/`welsh` → `GB`); `_COUNTRY_NAMES`
(ISO2 → display name, so output reads "United States", not `str.title()`'s
"Usa"); `_ALIASES` plus `burma`, `holland`, `uae`, `slovak republic`.

Error contract: unresolved input prints `{error, hint, suggestions}` and exits
**0**; `suggestions` from `difflib.get_close_matches`. `OSError` on data load
keeps exit 1 — an install fault, not user input.

New note for an unmatched 2-letter code: "`<XX>` is not in this dataset's
exemption list; the e-Visa pathway shown applies to all nationalities." `VN`
short-circuits ahead of all pathway logic and the `--phu_quoc_only` branch,
returning a new `recommended_pathway: "NOT_REQUIRED"` with null `visa_free`
and `evisa_option`, plus the no-visa note.

## Acceptance
- [x] `Russians`/`Russian`/`"Russian citizens"` → `RU`, `VISA_FREE`, 45 days
- [x] `UK` → `GB`, `VISA_FREE`, 45 days; `USA` → `US`, "United States"
- [x] Every country in both dataset country lists is reachable by ≥1 demonym
- [x] `XYZ` → structured error with `suggestions`, exit 0
- [x] No input path exits non-zero except an unreadable/invalid data file
- [x] Unmatched 2-letter codes carry the "not in dataset" note
- [x] `VN` → `NOT_REQUIRED`, null `visa_free`/`evisa_option`, under every flag
- [x] `--phu_quoc_only` unchanged for every resolvable nationality except `VN`
- [x] SKILL.md documents demonym input, `NOT_REQUIRED`, and the exit-0 contract
- [x] NOT: a bundled full ISO 3166 table, fuzzy matches applied silently
      (suggestions are returned, never auto-accepted), or a non-stdlib dependency

## Verify
- `Russians` → `RU`/`VISA_FREE`; `UK` → `GB`/`VISA_FREE`; `VN` → `NOT_REQUIRED`
- `… --nationality XYZ; echo $?` → JSON with `suggestions`, then `0`
- `python3 scripts/validate_skills.py` → `"ok": true`
- `python3 -m unittest discover -s tests -v` → all tests pass

## Notes
Defect 3, not the reported symptom, is the real risk — it silently misadvises
anyone who types "UK".
