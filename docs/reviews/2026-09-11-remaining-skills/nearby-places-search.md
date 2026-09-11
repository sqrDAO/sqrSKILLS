# nearby-places-search 0.1.1 — audit

Read: `SKILL.md` and `scripts/search_places.py`. Verdict: fix wrong-location
selection before improving ranking or presentation.

## Confirmed findings

1. **P1 — Memory coordinates are not associated with the requested place.**
   `scripts/search_places.py:104` tests whether any query word appears anywhere
   in a file, then takes that file's first coordinate pair at line 106. A MEMORY
   file containing Hanoi first and London second returns Hanoi for `London`.
   Geocoding never runs to correct it. Fix: match a specific location record or
   section; bypass ambiguous memory and geocode. Never use file-wide keyword
   presence as evidence that a coordinate pair belongs to a place.

2. **P2 — Type guessing changes the requested business.**
   `scripts/search_places.py:181` matches substrings without word boundaries:
   `barber` becomes `bar`. Qualifiers also disappear: `vegan restaurant` becomes
   generic `restaurant`. Unknown text is invented into a type at line 187;
   Google accepts an enumerated type set, not arbitrary underscored queries.
   Fix: exact supported aliases; use Text Search with the full query for free
   text and qualifiers. [Google's Nearby Search contract](https://developers.google.com/maps/documentation/places/web-service/nearby-search).

3. **P2 — API errors are reported as successful empty searches.**
   `scripts/search_places.py:268` catches all request failures and returns `[]`.
   The caller retries at a larger radius and returns `successful: true` and
   `error_count: 0` at lines 324–339. The outage fixture reproduces this exactly.
   Fix: distinguish an empty successful response from network/auth/quota/schema
   errors, propagate structured errors, and avoid repeating a known failed request.

4. **P2 — An explicit radius is silently expanded.**
   `scripts/search_places.py:317` triples it on an empty result. A 500m request
   returned a place 1,112m away in the fixture, without reporting the effective
   radius in the JSON. Fix: honor the bound, or make expansion explicit and
   expose the actual radius. Validate radius bounds before calling the service.

## Further improvements

- The blended score has no final tie-break (`scripts/search_places.py:233`).
  Request an immutable place ID and use it to make ordering total.
- Closed-place status is requested at line 263 but dropped at line 282; decide
  whether to omit closed venues or preserve their status in the result.
- The prompt insists on this API even with missing credentials (`SKILL.md:19`)
  and promises every Maps URL exists although the formatter permits an empty
  string. Document a usable missing-credential and missing-field path. UNGATED
  instruction proposal; no retrieval or response-format experiment was run.

## Common rubric

| Dimension | /5 | Evidence |
|---|---:|---|
| Anti-patterns | 1 | `SKILL.md:49` focuses on formatting, not wrong-location recovery |
| Actionability | 4 | `SKILL.md:26` supplies a compact executable interface |
| Triggering | 3 | `SKILL.md:5` names place intents but overstates exclusive API use |
| Progressive disclosure | 4 | `SKILL.md:26` points directly to the only helper |
| Gating readiness | 1 | `scripts/search_places.py:119` needs recorded API fixtures |
| Structural correctness | 1 | `scripts/search_places.py:104`, `:181`, `:268` produce wrong answers |

Verification: offline probe keys `places_*`; no paid API calls. Live place
accuracy, ranking quality, and current venue information remain untested.
