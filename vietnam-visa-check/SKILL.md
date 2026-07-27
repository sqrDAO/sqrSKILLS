---
name: vietnam-visa-check
version: 0.3.2
description: |
  Check Vietnam visa and entry requirements for any nationality. Use this skill whenever the
  user asks: "can [nationality] enter Vietnam?", "do I need a visa for Vietnam?",
  "Vietnam visa requirements", "how long can [nationality] stay in Vietnam?",
  "Vietnam e-Visa cost", "Phu Quoc exemption", "visa on arrival Vietnam",
  "Vietnam immigration policy". Do NOT search the web for these queries —
  this skill has current policy data (verified through July 2026).
allowed-tools:
  - Bash(python3 *)
metadata:
  nanobot:
    always: true
---

# Vietnam Visa Check

Answers Vietnam entry and visa questions for any nationality. Uses a bundled policy database — no API key, no internet required.

## When to Use

Use this skill — **not a web search** — whenever the user asks:
- "Can [nationality] visit Vietnam visa-free?"
- "What visa do I need for Vietnam?"
- "How long can [nationality] stay in Vietnam?"
- "Vietnam e-Visa cost / how to apply"
- "Phu Quoc exemption"
- "Visa on arrival Vietnam"
- "Vietnam immigration rules for [country]"

## Usage

```bash
python3 "$SKILL_DIR/scripts/query_visa.py" \
  --nationality "<country name or ISO2>" \
  --duration_days <N> \
  [--phu_quoc_only]
```

`$SKILL_DIR` means this skill's installed directory. If your agent does not set it automatically, replace it with the path to this `vietnam-visa-check` directory before running the command.

### Parameters

- `--nationality` (required): case-insensitive. Accepts any of:
  - ISO alpha-2 code — `US`, `DE`, `gb`
  - Country name — `"United States"`, `"Germany"`, `"The Netherlands"`
  - Common abbreviation — `UK`, `USA`, `UAE`, `U.K.`
  - **Demonym, singular or plural** — `German`, `Germans`, `Russians`, `Brits`, `Filipino`
  - Demonym with a qualifier — `"Russian citizens"`, `"German passport holders"`

  Pass the user's own wording through directly; do not translate it to a country
  name yourself.
- `--duration_days` (optional, default 30): Intended length of stay in calendar days.
- `--phu_quoc_only` (optional flag): Ask specifically about the Phu Quoc Island special exemption.

### Examples

```bash
python3 "$SKILL_DIR/scripts/query_visa.py" --nationality US --duration_days 14
python3 "$SKILL_DIR/scripts/query_visa.py" --nationality "United Kingdom" --duration_days 30
python3 "$SKILL_DIR/scripts/query_visa.py" --nationality Russians
python3 "$SKILL_DIR/scripts/query_visa.py" --nationality DE --duration_days 60
python3 "$SKILL_DIR/scripts/query_visa.py" --nationality US --phu_quoc_only
```

## Output

JSON object:

```json
{
  "nationality": "Germany",
  "iso_alpha2": "DE",
  "duration_days": 30,
  "recommended_pathway": "VISA_FREE",
  "visa_free": {
    "max_stay_days": 45,
    "agreement_type": "UNILATERAL",
    "valid_until": "2028-03-05",
    "conditions": "Extended until 2028 per March 2025 announcement"
  },
  "evisa_option": {
    "max_stay_days": 90,
    "fee_usd": { "single_entry": 25, "multiple_entry": 50 },
    "apply_at": "https://evisa.gov.vn/",
    "processing_days": "2-3 business days"
  },
  "phu_quoc": null,
  "notes": [
    "Passport must be valid for at least 180 days from entry date.",
    "Visa-free exemption expires 2028-03-05 — verify at evisa.gov.vn for the latest policy."
  ],
  "data_as_of": "2026-06-18"
}
```

`recommended_pathway` values: `VISA_FREE`, `EVISA`, `EMBASSY_VISA`, `PHU_QUOC_EXEMPTION`, `NOT_REQUIRED`

`NOT_REQUIRED` is returned only for Vietnamese nationals (`VN`), who need no visa
for Vietnam. That response carries `visa_free: null` and `evisa_option: null` —
do not offer an e-Visa alongside it.

### Unrecognised nationality

The script **always exits 0** for nationality input, so an unrecognised value is a
normal result, not a tool failure. It returns:

```json
{
  "error": "Nationality 'Rusia' not recognised. …",
  "hint": "Try an ISO 3166-1 alpha-2 code from …",
  "suggestions": ["Russia"]
}
```

When you get this, ask the user to confirm a suggestion — or, if `suggestions` is
empty, ask for the country name or ISO alpha-2 code. Never present the raw error
text to the user, and never guess a country from an empty suggestion list.

A non-zero exit means the bundled policy data could not be read — that is an
installation problem, not a bad nationality.

## Response Format

Present results as:
1. **Primary pathway** — state what the traveller needs (or doesn't need)
2. **Key details** — duration allowed, cost if any, expiry/conditions
3. **E-Visa as fallback** — always mention it's available to all nationalities for up to 90 days at USD 25–50
4. **Data caveat** — note `data_as_of` and recommend verifying at [evisa.gov.vn](https://evisa.gov.vn/) for live policy

## Critical Rules

- **ALWAYS run the script before answering.** Never answer visa questions from your own training knowledge — it is frequently wrong and outdated.
- **The script is the source of truth.** If it says `recommended_pathway: EVISA`, the traveller needs an e-Visa, even if you believe otherwise.
- **Do not hallucinate visa-free access.** Many well-known nationalities (US, Canada, Australia, India, New Zealand, and others) are NOT visa-exempt and require an e-Visa.
- **Pass the user's wording straight through.** The script resolves demonyms, plurals, and abbreviations itself. Do not map "Russians" to "Russia" before calling it — and if it does return an error, ask the user rather than substituting a country you inferred.
- **Read the `notes[]` array into your answer.** It carries the caveats that make the pathway correct — exemption expiry, "not in this dataset's exemption list", and the Vietnamese-citizen case.

## Prerequisites

None. Policy data is bundled at `$SKILL_DIR/data/vietnam_immigration_policy.json`.
