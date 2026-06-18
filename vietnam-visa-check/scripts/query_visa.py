#!/usr/bin/env python3
"""Query Vietnam visa and entry requirements for a given nationality.

Usage:
    python3 query_visa.py --nationality <ISO2 or country name> [--duration_days N] [--phu_quoc_only]

Output:
    JSON: {nationality, iso_alpha2, duration_days, recommended_pathway, visa_free?, evisa_option, phu_quoc?, notes[], data_as_of}
"""
import argparse
import json
import os
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
}


def load_policy(data_path: str) -> dict:
    with open(data_path, encoding="utf-8") as f:
        return json.load(f)


def build_country_index(policy: dict) -> dict[str, str]:
    """Return a dict mapping lowercase country name / ISO2 → uppercase ISO2."""
    index: dict[str, str] = {}
    for entry in policy["visa_exemption_by_country"]["entries"]:
        iso2 = entry["iso_alpha2"].upper()
        index[iso2.lower()] = iso2
        index[entry["country"].lower()] = iso2
    for entry in policy.get("no_visa_exemption_notable_countries", {}).get("entries", []):
        iso2 = entry["iso_alpha2"].upper()
        index[iso2.lower()] = iso2
        index[entry["country"].lower()] = iso2
    # Merge hardcoded aliases (they win on conflict)
    for alias, iso2 in _ALIASES.items():
        index[alias] = iso2.upper()
    return index


def resolve_nationality(raw: str, index: dict[str, str]) -> str | None:
    """Return uppercase ISO2 for raw nationality string, or None if not found.

    Accepts:
    - 2-letter ISO alpha-2 codes directly (any case), e.g. "US", "us"
    - Full country names present in the exemption list, e.g. "Germany"
    - Hardcoded aliases, e.g. "USA", "UK", "South Korea"
    """
    raw = raw.strip()
    # If it looks like an ISO2 code (1-3 letters), accept it directly
    if len(raw) <= 3 and raw.isalpha():
        return raw.upper()
    key = raw.lower()
    return index.get(key)


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
    iso2 = resolve_nationality(args.nationality, index)

    if iso2 is None:
        print(json.dumps({
            "error": f"Nationality '{args.nationality}' not recognised. Use an ISO alpha-2 code (e.g. 'US', 'DE') or a full country name.",
            "hint": "Try an ISO 3166-1 alpha-2 code from https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2",
        }))
        sys.exit(1)

    duration = args.duration_days
    notes: list[str] = []
    evisa_option = build_evisa_option(policy)

    # Phu Quoc-only query
    if args.phu_quoc_only:
        result = {
            "nationality": args.nationality.title(),
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

    # Resolve display name from exemption data or no-exemption list, fallback to input
    if exemption:
        display_name = exemption["country"]
    elif no_exemption_entry:
        display_name = no_exemption_entry["country"]
    else:
        display_name = args.nationality.title()

    result = {
        "nationality": display_name,
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
