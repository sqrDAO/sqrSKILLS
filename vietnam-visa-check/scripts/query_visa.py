#!/usr/bin/env python3
"""Query Vietnam visa and entry requirements for a given nationality.

Usage:
    python3 query_visa.py --nationality <ISO2 or country name> [--duration_days N] [--phu_quoc_only]

Output:
    JSON: {nationality, iso_alpha2, duration_days, recommended_pathway, visa_free?, evisa_option, phu_quoc?, notes[], data_as_of}
"""
import argparse
import difflib
import json
import os
import re
import sys
from datetime import date


# Hardcoded aliases: common name / abbreviation → ISO alpha-2
_ALIASES = {
    "usa": "US",
    "united states of america": "US",
    "united states": "US",
    "america": "US",
    "uk": "GB",
    "great britain": "GB",
    "britain": "GB",
    "england": "GB",
    "scotland": "GB",
    "wales": "GB",
    "south korea": "KR",
    "korea": "KR",
    "north korea": "KP",
    "czech republic": "CZ",
    "czechia": "CZ",
    "russia": "RU",
    "russian federation": "RU",
    "taiwan": "TW",
    "hong kong": "HK",
    "vietnam": "VN",
    "viet nam": "VN",
    "burma": "MM",
    "holland": "NL",
    "uae": "AE",
    "emirates": "AE",
    "slovak republic": "SK",
    "the philippines": "PH",
}


# Demonyms → ISO alpha-2. Covers every country in the bundled dataset plus common
# travel nationalities absent from it (those still get a correct e-Visa answer and
# a proper display name).
_DEMONYMS = {
    # Dataset: visa-exempt countries
    "cambodian": "KH", "khmer": "KH",
    "indonesian": "ID",
    "lao": "LA", "laotian": "LA",
    "malaysian": "MY",
    "singaporean": "SG",
    "thai": "TH",
    "burmese": "MM", "myanmarese": "MM",
    "filipino": "PH", "filipina": "PH", "philippine": "PH", "pinoy": "PH",
    "bruneian": "BN",
    "german": "DE",
    "french": "FR", "frenchman": "FR", "frenchwoman": "FR",
    "italian": "IT",
    "spanish": "ES", "spaniard": "ES",
    "british": "GB", "briton": "GB", "brit": "GB", "english": "GB",
    "scottish": "GB", "scot": "GB", "welsh": "GB", "northern irish": "GB",
    "russian": "RU",
    "japanese": "JP",
    "korean": "KR", "south korean": "KR",
    "danish": "DK", "dane": "DK",
    "swedish": "SE", "swede": "SE",
    "norwegian": "NO",
    "finnish": "FI", "finn": "FI",
    "belarusian": "BY", "belarussian": "BY",
    "belgian": "BE",
    "bulgarian": "BG",
    "croatian": "HR", "croat": "HR",
    "czech": "CZ",
    "swiss": "CH",
    "luxembourgish": "LU", "luxembourger": "LU",
    "hungarian": "HU", "magyar": "HU",
    "dutch": "NL", "dutchman": "NL", "netherlander": "NL",
    "polish": "PL", "pole": "PL",
    "romanian": "RO", "rumanian": "RO",
    "slovak": "SK", "slovakian": "SK",
    "slovenian": "SI", "slovene": "SI",
    "chilean": "CL",
    "panamanian": "PA",
    "kazakh": "KZ", "kazakhstani": "KZ",
    "kyrgyz": "KG", "kyrgyzstani": "KG",
    "mongolian": "MN",
    "seychellois": "SC",
    # Dataset: notable countries with no exemption
    "american": "US",
    "canadian": "CA",
    "australian": "AU", "aussie": "AU",
    "new zealander": "NZ", "kiwi": "NZ",
    "indian": "IN",
    "chinese": "CN",
    "emirati": "AE",
    "south african": "ZA",
    "mexican": "MX",
    "brazilian": "BR",
    # Common nationalities absent from the dataset
    "vietnamese": "VN",
    "irish": "IE",
    "austrian": "AT",
    "portuguese": "PT",
    "greek": "GR",
    "turkish": "TR", "turk": "TR",
    "ukrainian": "UA",
    "israeli": "IL",
    "taiwanese": "TW",
    "hongkonger": "HK",
    "estonian": "EE",
    "latvian": "LV",
    "lithuanian": "LT",
    "icelandic": "IS", "icelander": "IS",
    "serbian": "RS", "serb": "RS",
    "maltese": "MT",
    "cypriot": "CY",
    "argentine": "AR", "argentinian": "AR",
    "colombian": "CO",
    "peruvian": "PE",
    "nigerian": "NG",
    "egyptian": "EG",
    "pakistani": "PK",
    "bangladeshi": "BD",
    "sri lankan": "LK",
    "nepali": "NP", "nepalese": "NP",
    "iranian": "IR",
    "saudi": "SA", "saudi arabian": "SA",
    "qatari": "QA",
}


# ISO alpha-2 → display name, for countries reachable by alias or demonym but not
# present in the bundled dataset (keeps output off str.title(), e.g. "Usa").
_COUNTRY_NAMES = {
    "US": "United States", "GB": "United Kingdom", "KP": "North Korea",
    "VN": "Vietnam", "TW": "Taiwan", "HK": "Hong Kong", "IE": "Ireland",
    "AT": "Austria", "PT": "Portugal", "GR": "Greece", "TR": "Turkey",
    "UA": "Ukraine", "IL": "Israel", "EE": "Estonia", "LV": "Latvia",
    "LT": "Lithuania", "IS": "Iceland", "RS": "Serbia", "MT": "Malta",
    "CY": "Cyprus", "AR": "Argentina", "CO": "Colombia", "PE": "Peru",
    "NG": "Nigeria", "EG": "Egypt", "PK": "Pakistan", "BD": "Bangladesh",
    "LK": "Sri Lanka", "NP": "Nepal", "IR": "Iran", "SA": "Saudi Arabia",
    "QA": "Qatar",
}


# Trailing words users append that carry no country information.
_QUALIFIERS = {
    "citizen", "citizens", "national", "nationals", "passport", "passports",
    "holder", "holders", "nationality", "people", "person", "tourist",
    "tourists", "traveller", "travellers", "traveler", "travelers",
}


def normalize(raw: str) -> str:
    """Lowercase, strip punctuation and non-informative qualifier words.

    "Russian citizens" → "russian";  "the U.K." → "uk";  "  Germans " → "germans"
    """
    key = re.sub(r"[^a-z0-9\s]", " ", raw.casefold())
    key = re.sub(r"\s+", " ", key).strip()
    if key.startswith("the "):
        key = key[4:].strip()
    words = key.split()
    while len(words) > 1 and words[-1] in _QUALIFIERS:
        words.pop()
    # Dotted abbreviations survive punctuation stripping as single letters: "U.K."
    # becomes ["u", "k"], which only means anything rejoined.
    if len(words) > 1 and all(len(word) == 1 for word in words):
        return "".join(words)
    return " ".join(words)


def load_policy(data_path: str) -> dict:
    with open(data_path, encoding="utf-8") as f:
        return json.load(f)


def build_country_index(policy: dict) -> dict[str, str]:
    """Return a dict mapping normalized country name / ISO2 / alias / demonym → ISO2."""
    index: dict[str, str] = {}
    for section in ("visa_exemption_by_country", "no_visa_exemption_notable_countries"):
        for entry in policy.get(section, {}).get("entries", []):
            iso2 = entry["iso_alpha2"].upper()
            index[iso2.lower()] = iso2
            index[normalize(entry["country"])] = iso2
    # Aliases and demonyms win on conflict
    for table in (_ALIASES, _DEMONYMS):
        for key, iso2 in table.items():
            index[key] = iso2.upper()
    return index


def resolve_nationality(raw: str, index: dict[str, str]) -> str | None:
    """Return uppercase ISO2 for a raw nationality string, or None if unresolved.

    Accepts, in order of precedence:
    - Country names in the dataset, aliases, and demonyms — e.g. "Germany",
      "UK", "Russian", "Russian citizens" (qualifiers are stripped first)
    - Plural demonyms — e.g. "Russians", "Germans"
    - Bare 2-letter ISO alpha-2 codes, e.g. "US", "de"

    The index is consulted before the ISO-code shortcut so that short aliases
    like "UK" resolve to GB rather than being read as a literal country code.
    """
    key = normalize(raw)
    if not key:
        return None
    if key in index:
        return index[key]
    # Plural demonym: "russians" → "russian". Plural country names ("laos",
    # "philippines", "netherlands") already matched above and never reach here.
    if key.endswith("s") and key[:-1] in index:
        return index[key[:-1]]
    # Bare ISO alpha-2 code, including codes absent from the bundled dataset
    if len(key) == 2 and key.isalpha():
        return key.upper()
    return None


def build_display_names(policy: dict) -> dict[str, str]:
    """Return ISO2 → country name, from the dataset plus the bundled name table."""
    names = dict(_COUNTRY_NAMES)
    for section in ("visa_exemption_by_country", "no_visa_exemption_notable_countries"):
        for entry in policy.get(section, {}).get("entries", []):
            names[entry["iso_alpha2"].upper()] = entry["country"]
    return names


def suggest_nationalities(
    raw: str, index: dict[str, str], names: dict[str, str], limit: int = 3
) -> list[str]:
    """Return close-matching country names for an unresolved input."""
    key = normalize(raw)
    candidates = [k for k in index if len(k) > 2]
    suggestions: list[str] = []
    for match in difflib.get_close_matches(key, candidates, n=limit * 3, cutoff=0.8):
        name = names.get(index[match], match.title())
        if name not in suggestions:
            suggestions.append(name)
    return suggestions[:limit]


def find_exemption(iso2: str, policy: dict) -> dict | None:
    """Return the visa_exemption_by_country entry for iso2, or None."""
    for entry in policy["visa_exemption_by_country"]["entries"]:
        if entry["iso_alpha2"].upper() == iso2:
            return entry
    return None


def find_no_exemption_entry(iso2: str, policy: dict) -> dict | None:
    """Return the no_visa_exemption_notable_countries entry for iso2, or None."""
    for entry in policy.get("no_visa_exemption_notable_countries", {}).get("entries", []):
        if entry["iso_alpha2"].upper() == iso2:
            return entry
    return None


def is_exemption_valid(entry: dict) -> bool:
    """Return True if exemption has not expired."""
    valid_until = entry.get("valid_until")
    if valid_until is None:
        return True
    try:
        return date.today() <= date.fromisoformat(valid_until)
    except ValueError:
        return True


def build_evisa_option(policy: dict) -> dict:
    evisa = policy["entry_categories"]["EVISA"]
    return {
        "max_stay_days": evisa["max_stay_days"],
        "fee_usd": evisa["fee_usd"],
        "apply_at": policy["policy_framework"]["official_portal"],
        "processing_days": evisa["processing_days"],
        "entry_modes_allowed": evisa["entry_modes_allowed"],
        "approved_ports_count": evisa["approved_ports_count"],
        "entry_port_restriction": evisa["entry_port_restriction"],
        "eligible_nationalities": evisa["eligible_nationalities"],
    }


def build_phu_quoc_option(policy: dict) -> dict:
    pq = policy["entry_categories"]["SPECIAL_ZONE_EXEMPTION"]
    return {
        "max_stay_days": pq["max_stay_days"],
        "restriction": pq["restriction"],
        "entry_modes_allowed": pq["entry_modes_allowed"],
        "passport_validity_required_days": pq["passport_validity_required_days"],
    }


def main():
    parser = argparse.ArgumentParser(description="Query Vietnam visa requirements")
    parser.add_argument("--nationality", required=True, help="ISO alpha-2 code or country name")
    parser.add_argument("--duration_days", type=int, default=30, help="Intended stay in days (default: 30)")
    parser.add_argument("--phu_quoc_only", action="store_true", help="Ask about Phu Quoc Island exemption only")
    args = parser.parse_args()

    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "vietnam_immigration_policy.json")
    try:
        policy = load_policy(data_path)
    except OSError as e:
        print(json.dumps({"error": f"Could not load policy data: {e}"}))
        sys.exit(1)

    index = build_country_index(policy)
    names = build_display_names(policy)
    iso2 = resolve_nationality(args.nationality, index)

    if iso2 is None:
        # Exit 0 deliberately: the caller is an agent that already has structured
        # JSON on stdout, and a non-zero exit surfaces as a tool failure to the user.
        print(json.dumps({
            "error": f"Nationality '{args.nationality}' not recognised. Use a country name (e.g. 'Germany'), a demonym (e.g. 'German'), or an ISO alpha-2 code (e.g. 'DE').",
            "hint": "Try an ISO 3166-1 alpha-2 code from https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2",
            "suggestions": suggest_nationalities(args.nationality, index, names),
        }, indent=2))
        return

    duration = args.duration_days
    notes: list[str] = []
    evisa_option = build_evisa_option(policy)

    # Phu Quoc-only query
    if args.phu_quoc_only:
        result = {
            "nationality": names.get(iso2, args.nationality.title()),
            "iso_alpha2": iso2,
            "duration_days": duration,
            "recommended_pathway": "PHU_QUOC_EXEMPTION",
            "phu_quoc": build_phu_quoc_option(policy),
            "evisa_option": evisa_option,
            "notes": [
                "Phu Quoc exemption is open to ALL nationalities — no visa needed.",
                "You must arrive directly from outside Vietnam (air or sea). Traveling to mainland Vietnam requires a separate visa.",
                f"Passport must be valid for at least {policy['entry_categories']['SPECIAL_ZONE_EXEMPTION']['passport_validity_required_days']} days from entry date.",
                f"Data as of {policy['_meta']['last_updated']}. Verify at {policy['policy_framework']['official_portal']}",
            ],
            "data_as_of": policy["_meta"]["last_updated"],
        }
        print(json.dumps(result, indent=2))
        return

    # Standard pathway determination
    exemption = find_exemption(iso2, policy)
    no_exemption_entry = find_no_exemption_entry(iso2, policy)
    visa_free_block = None
    recommended_pathway = None

    # Explicit negative: nationality is on the known-no-exemption list
    if no_exemption_entry and not exemption:
        notes.append(
            f"IMPORTANT: {no_exemption_entry['country']} passport holders do NOT have visa-free "
            f"access to Vietnam. {no_exemption_entry['note']}"
        )

    if exemption and is_exemption_valid(exemption):
        visa_free_block = {
            "max_stay_days": exemption["max_stay_days"],
            "agreement_type": exemption["agreement_type"],
            "valid_until": exemption.get("valid_until"),
            "conditions": exemption.get("conditions"),
            "source_refs": exemption.get("source_refs", []),
        }
        if duration <= exemption["max_stay_days"]:
            recommended_pathway = "VISA_FREE"
        else:
            # Exemption exists but trip is longer than allowed
            notes.append(
                f"{exemption['country']} passport holders are normally exempt for up to "
                f"{exemption['max_stay_days']} days, but your trip ({duration} days) exceeds "
                f"that limit — an e-Visa (up to 90 days) is required instead."
            )

    if recommended_pathway is None:
        if duration <= 90:
            recommended_pathway = "EVISA"
        else:
            recommended_pathway = "EMBASSY_VISA"
            notes.append(
                "Stays longer than 90 days require an embassy/consulate visa in the appropriate "
                "category (e.g. LV work visa, DT investment visa, GD education visa)."
            )

    # Nationality is outside the bundled exemption dataset — say so rather than
    # implying the generic e-Visa answer was a positive match.
    if not exemption and not no_exemption_entry:
        notes.append(
            f"{names.get(iso2, iso2)} ({iso2}) is not listed in this dataset's visa-exemption "
            f"table, so no exemption is on record. The e-Visa pathway below is open to all "
            f"nationalities."
        )

    # Vietnamese citizens do not need a visa for Vietnam.
    if iso2 == "VN":
        notes.append(
            "Vietnamese citizens do not need a visa to enter Vietnam — this skill answers "
            "for foreign passport holders."
        )

    # Special case: Chinese nationals cannot use VOA, but the e-Visa rule remains all-nationalities.
    if iso2 == "CN":
        notes.append(
            "Chinese nationals cannot use Visa on Arrival (VOA). "
            "Use the official e-Visa portal for short stays, unless a consular visa is needed for the trip purpose."
        )

    # Expiry warning
    if visa_free_block and visa_free_block.get("valid_until"):
        notes.append(
            f"Visa-free exemption expires {visa_free_block['valid_until']} — "
            f"verify at {policy['policy_framework']['official_portal']} for the latest policy."
        )

    # Passport validity
    min_days = policy["policy_framework"]["passport_validity_minimum_days"]
    notes.append(f"Passport must be valid for at least {min_days} days from the date of entry.")

    # Data freshness
    notes.append(
        f"Data as of {policy['_meta']['last_updated']}. "
        f"Always verify current policy at {policy['policy_framework']['official_portal']}."
    )

    result = {
        "nationality": names.get(iso2, args.nationality.title()),
        "iso_alpha2": iso2,
        "duration_days": duration,
        "recommended_pathway": recommended_pathway,
        "visa_free": visa_free_block,
        "evisa_option": evisa_option,
        "phu_quoc": None,
        "notes": notes,
        "data_as_of": policy["_meta"]["last_updated"],
    }

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
