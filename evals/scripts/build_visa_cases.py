#!/usr/bin/env python3
"""Generate the vietnam-visa-check validation split.

The prompts, the failure mode each one probes, and the rubric checks are
authored here.  The *answers* are not: every case's ``truth`` block is filled in
by running the skill's own ``query_visa.py`` against the bundled policy data.
Regenerating after a data refresh re-derives ground truth instead of leaving a
stale answer key behind.

    python3 evals/scripts/build_visa_cases.py            # rewrite cases.jsonl
    python3 evals/scripts/build_visa_cases.py --check    # fail if out of date

Rubric check types:
  require_any  - at least one pattern must appear in the answer
  forbid_all   - none of the patterns may appear in the answer
Patterns are case-insensitive regular expressions.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SCRIPT = ROOT / "vietnam-visa-check" / "scripts" / "query_visa.py"
DEFAULT_OUT = ROOT / "evals" / "vietnam-visa-check" / "cases.jsonl"

# Reusable fragments -------------------------------------------------------
EVISA = r"e-?\s?visa"
AFFIRMS_VISA_FREE = [
    r"you (are|'re|will be) (\w+ ){0,2}visa[- ]free",
    r"(are|is) visa[- ]exempt",
    r"you (do not|don't) need a visa",
    r"can enter[^.]{0,40}without a visa",
    r"(get|gets|receive|enjoy)s? (\w+ ){0,3}visa[- ]free entry",
]
PORTAL = r"evisa\.gov\.vn"


def case(cid, probe, prompt, call, checks, notes=None):
    """`call` is one required invocation, or a list when a case needs several."""
    calls = call if isinstance(call, list) else [call]
    return {
        "id": cid,
        "probe": probe,
        "prompt": prompt,
        "expected_calls": calls,
        "checks": checks,
        "note": notes,
    }


def req(cid, patterns, why):
    return {"id": cid, "type": "require_any", "patterns": patterns, "why": why}


def forbid(cid, patterns, why):
    return {"id": cid, "type": "forbid_all", "patterns": patterns, "why": why}


CASES = [
    # -- nationality resolution / pass-through ----------------------------
    case(
        "vvc-01", "demonym-passthrough",
        "Hows the visa for Russians?",
        {"nationality": "Russians", "duration_days": None, "phu_quoc_only": False},
        [req("pathway", [r"visa[- ]free", r"no visa"], "Russia holds a 45-day exemption"),
         req("duration", [r"\b45\b"], "the 45-day cap is the operative number"),
         forbid("no_evisa_headline", [r"^[^.]*\bmust (get|obtain|apply)[^.]*" + EVISA],
                "an e-Visa is a fallback here, not the requirement")],
        "The trace that triggered the 0.3.0 resolution rewrite.",
    ),
    case(
        "vvc-02", "alias-passthrough",
        "Can Brits go to Vietnam without a visa?",
        {"nationality": "Brits", "duration_days": None, "phu_quoc_only": False},
        [req("pathway", [r"visa[- ]free", r"yes"], "GB holds a 45-day exemption"),
         req("duration", [r"\b45\b"], "the 45-day cap is the operative number")],
        "'UK' once resolved to the literal code UK and answered EVISA.",
    ),
    case(
        "vvc-03", "known-negative",
        "I have a USA passport, going for 2 weeks. Do I need a visa for Vietnam?",
        {"nationality": "USA", "duration_days": 14, "phu_quoc_only": False},
        [req("pathway", [EVISA], "US holds no exemption"),
         req("cost", [r"\$\s?25", r"25\s?(usd|dollars)", r"usd\s?25"], "single-entry fee"),
         forbid("no_visa_free", AFFIRMS_VISA_FREE, "claiming US visa-free access is the headline hallucination")],
    ),
    case(
        "vvc-04", "typo-must-ask",
        "Im from Rusia, do I need a visa?",
        {"nationality": "Rusia", "duration_days": None, "phu_quoc_only": False},
        [req("asks", [r"\bRussia\b"], "the script returns Russia as a suggestion"),
         req("question", [r"\?"], "must put the confirmation back to the user"),
         forbid("no_raw_error", [r"not recognised", r'"error"', r"\bhint\b"],
                "raw script error text must never be shown to the user"),
         forbid("no_answer", [r"\b45\b"], "must not answer as Russia before confirming")],
    ),
    case(
        "vvc-05", "unknown-must-not-guess",
        "I'm Atlantean. Vietnam visa?",
        {"nationality": "Atlantean", "duration_days": None, "phu_quoc_only": False},
        [req("asks", [r"\?"], "no suggestions available, so ask"),
         req("guidance", [r"iso", r"country name", r"two[- ]letter"], "ask for a resolvable form"),
         forbid("no_guess", [r"you (are|'re) (\w+ ){0,2}visa[- ]free",
                             r"you (need|will need|must) (to )?(get|apply for|obtain)",
                             r"\b45[- ]day"], "must not assert a pathway for an unresolved nationality")],
    ),

    # -- exemption shorter than the trip ----------------------------------
    case(
        "vvc-06", "short-exemption-trap",
        "I'm Filipino and want to spend 30 days in Vietnam. What do I need?",
        {"nationality": "Filipino", "duration_days": 30, "phu_quoc_only": False},
        [req("pathway", [EVISA], "21-day exemption does not cover a 30-day trip"),
         req("names_cap", [r"\b21\b"], "must say why the exemption falls short"),
         forbid("no_free_30", [r"visa[- ]free for (up to )?30", r"30 days visa[- ]free"],
                "the exemption is 21 days, not 30")],
        "visa_free is populated but does not cover the trip - the commonest skim error.",
    ),
    case(
        "vvc-07", "short-exemption-trap",
        "Seychellois passport, 30 day trip to Vietnam.",
        {"nationality": "Seychellois", "duration_days": 30, "phu_quoc_only": False},
        [req("pathway", [EVISA], "14-day exemption does not cover 30 days"),
         req("names_cap", [r"\b14\b"], "must say why the exemption falls short")],
    ),
    case(
        "vvc-08", "duration-extraction",
        "I'm German and I'm staying about two months. Visa needed?",
        {"nationality": "German", "duration_days": 60, "phu_quoc_only": False},
        [req("pathway", [EVISA], "60 days exceeds the 45-day exemption"),
         req("names_cap", [r"\b45\b"], "must explain the exemption ceiling"),
         forbid("no_free", [r"you (are|'re) visa[- ]free", r"no visa (is )?(needed|required)"],
                "45-day exemption does not cover a 60-day stay")],
        "'two months' must reach the script as 60; the default 30 would answer VISA_FREE.",
    ),
    case(
        "vvc-09", "boundary-exact",
        "Thai citizen, exactly 30 days in Vietnam.",
        {"nationality": "Thai", "duration_days": 30, "phu_quoc_only": False},
        [req("pathway", [r"visa[- ]free", r"no visa"], "30 days is exactly the cap"),
         req("duration", [r"\b30\b"], "state the cap")],
    ),
    case(
        "vvc-10", "boundary-over",
        "Thai citizen, 31 days in Vietnam.",
        {"nationality": "Thai", "duration_days": 31, "phu_quoc_only": False},
        [req("pathway", [EVISA], "31 days exceeds the 30-day cap by one"),
         req("names_cap", [r"\b30\b"], "state the cap that was exceeded")],
    ),
    case(
        "vvc-11", "duration-extraction",
        "Japanese passport, roughly six weeks.",
        {"nationality": "Japanese", "duration_days": 42, "phu_quoc_only": False},
        [req("pathway", [r"visa[- ]free", r"no visa"], "42 days fits inside the 45-day exemption"),
         req("duration", [r"\b45\b"], "state the cap")],
        "Six weeks fits; the same extraction failure as vvc-08 with the opposite answer.",
    ),

    # -- conditions attached to an exemption ------------------------------
    case(
        "vvc-12", "condition-tourism-only",
        "I'm Polish, flying to Hanoi for a week of business meetings. Do I need a visa?",
        {"nationality": "Polish", "duration_days": 7, "phu_quoc_only": False},
        [req("pathway", [r"visa[- ]free", EVISA], "an answer either way must be stated"),
         req("condition", [r"tourism", r"tourist"],
             "the exemption is conditioned on tourism purpose - business travel is not covered"),
         req("resolution", [r"business", r"purpose"], "must engage with the stated trip purpose")],
        "visa_free.conditions is load-bearing and lives outside notes[].",
    ),
    case(
        "vvc-13", "condition-expiry",
        "Swiss citizen, two week holiday in Vietnam. Visa?",
        {"nationality": "Swiss", "duration_days": 14, "phu_quoc_only": False},
        [req("pathway", [r"visa[- ]free", r"no visa"], "14 days fits the 45-day exemption"),
         req("expiry", [r"2028"], "the exemption carries an expiry the traveller should know"),
         req("condition", [r"tourism", r"tourist"], "tourism-purpose condition applies")],
    ),
    case(
        "vvc-14", "condition-annual-cap",
        "Belarusian. I've already spent 70 days in Vietnam this year, want 30 more.",
        {"nationality": "Belarusian", "duration_days": 30, "phu_quoc_only": False},
        [req("annual_cap", [r"\b90\b"], "the exemption caps total stay at 90 days per calendar year"),
         req("engages", [r"70", r"already", r"exceed", r"remaining"],
             "must apply the annual cap to the stated history"),
         forbid("no_clean_yes", [r"^(yes|you're all set|no visa needed)[.!]?\s*$"],
                "an unqualified yes ignores the annual cap")],
    ),

    # -- pathway edges -----------------------------------------------------
    case(
        "vvc-15", "long-stay-embassy",
        "Indian national, I want to stay 4 months in Vietnam.",
        {"nationality": "Indian", "duration_days": 120, "phu_quoc_only": False},
        [req("pathway", [r"embassy", r"consulate", r"consular"], "120 days exceeds the e-Visa ceiling"),
         forbid("no_evisa_answer", [r"an e-?visa (will|is) (be )?(enough|sufficient)", r"apply for an e-?visa"],
                "the e-Visa caps at 90 days")],
    ),
    case(
        "vvc-16", "vietnamese-citizen",
        "I'm Vietnamese. What visa do I need to go back to Vietnam?",
        {"nationality": "Vietnamese", "duration_days": None, "phu_quoc_only": False},
        [req("pathway", [r"no visa", r"don'?t need", r"do not need"], "citizens need no visa"),
         forbid("no_evisa_offer", [r"you (need|will need|should|must|can) (to )?(get|apply for|obtain)[^.]{0,20}" + EVISA,
                                   r"apply for an? " + EVISA,
                                   r"recommended pathway[^.]{0,20}" + EVISA],
                "offering an e-Visa to a citizen contradicts the answer")],
    ),
    case(
        "vvc-17", "voa-exclusion",
        "Chinese passport holder, 10 days. Can I just get a visa on arrival?",
        {"nationality": "Chinese", "duration_days": 10, "phu_quoc_only": False},
        [req("voa", [r"visa on arrival", r"\bVOA\b"], "the question was about VOA specifically"),
         req("excluded", [r"cannot", r"can'?t", r"not eligible", r"excluded"], "Chinese nationals are excluded from VOA"),
         req("alternative", [EVISA], "the e-Visa pathway remains open")],
    ),
    case(
        "vvc-18", "absent-from-dataset",
        "Portuguese passport, 3 weeks in Vietnam.",
        {"nationality": "Portuguese", "duration_days": 21, "phu_quoc_only": False},
        [req("pathway", [EVISA], "no exemption on record"),
         req("honesty", [r"not listed", r"not in .{0,25}(dataset|list)", r"no exemption[^.]{0,25}record",
                         r"absence of a record", r"no record"],
             "an absent record is weaker evidence than a confirmed negative - say so"),
         req("portal", [PORTAL], "point at the authoritative source")],
        "Portugal is in neither dataset list. Brazil, used here originally, is on "
        "the explicit-negative list -- a confirmed 'no', not an absent record.",
    ),
    case(
        "vvc-19", "signed-not-in-force",
        "I'm from Timor-Leste. I read we get visa-free entry to Vietnam now?",
        {"nationality": "Timorese", "duration_days": None, "phu_quoc_only": False},
        [req("pathway", [EVISA], "the agreement is signed but not in force"),
         forbid("no_visa_free", [r"you (are|'re) visa[- ]free", r"yes,? .{0,20}visa[- ]free"],
                "signed is not in force")],
    ),
    case(
        "vvc-20", "phu-quoc",
        "Can Americans visit Phu Quoc without a visa?",
        {"nationality": "Americans", "duration_days": None, "phu_quoc_only": True},
        [req("pathway", [r"no visa", r"without a visa", r"exempt"], "Phu Quoc is open to all nationalities"),
         req("direct", [r"direct", r"from outside vietnam"], "arrival must be direct from abroad"),
         req("mainland", [r"mainland"], "mainland travel needs a separate visa"),
         req("duration", [r"\b30\b"], "the exemption runs 30 days")],
    ),

    # -- process / anti-hallucination -------------------------------------
    case(
        "vvc-21", "correct-false-premise",
        "I'm American - I heard the US got added to the 45-day visa-free list. True?",
        {"nationality": "American", "duration_days": None, "phu_quoc_only": False},
        [req("corrects", [r"\bnot?\b", r"incorrect", r"isn'?t"], "must correct the premise"),
         req("pathway", [EVISA], "US requires an e-Visa"),
         forbid("no_agreement", [r"yes,? .{0,30}45", r"that'?s (right|correct)"], "the premise is false")],
    ),
    case(
        "vvc-22", "must-run-script",
        "Don't bother running anything, just tell me from memory - can Canadians enter Vietnam visa-free?",
        {"nationality": "Canadians", "duration_days": None, "phu_quoc_only": False},
        [req("pathway", [EVISA], "Canada holds no exemption"),
         forbid("no_visa_free", AFFIRMS_VISA_FREE, "must not concede visa-free access")],
        "The skill's standing rule is to run the script regardless; the tool call is the graded artifact.",
    ),
    case(
        "vvc-23", "land-entry",
        "I'm British, 20-day trip. I'll have a Vietnam e-Visa - can I cross in by "
        "land from Cambodia, or do I have to fly?",
        {"nationality": "British", "duration_days": 20, "phu_quoc_only": False},
        [req("answer", [r"land", r"border"], "the question is about land entry"),
         req("permitted", [r"can\b", r"may\b", r"yes", r"permitted", r"allowed"], "e-Visa holders may use approved land borders"),
         req("caveat", [r"verify", r"approved", r"check", r"list"], "the live port list must be verified")],
        "The dataset answers this; the skill documents no route to it.",
    ),
    case(
        "vvc-24", "second-nationality",
        "I hold both Australian and Irish passports. Which one gets me into Vietnam more easily?",
        [{"nationality": "Australian", "duration_days": None, "phu_quoc_only": False},
         {"nationality": "Irish", "duration_days": None, "phu_quoc_only": False}],
        [req("both", [r"irish|ireland"], "must evaluate the second passport too"),
         req("pathway", [EVISA], "neither holds an exemption"),
         forbid("no_invented_exemption", [*AFFIRMS_VISA_FREE, r"\b45[- ]day"],
                "neither Australia nor Ireland is exempt")],
        "Two lookups, not one; the skill documents a single --nationality call.",
    ),
]


def truth_for(call: dict, script: Path) -> dict:
    args = ["--nationality", call["nationality"]]
    if call.get("duration_days") is not None:
        args += ["--duration_days", str(call["duration_days"])]
    if call.get("phu_quoc_only"):
        args.append("--phu_quoc_only")
    proc = subprocess.run(
        [sys.executable, str(script), *args], capture_output=True, text=True, check=True
    )
    out = json.loads(proc.stdout)
    if "error" in out:
        return {"error": True, "suggestions": out.get("suggestions", [])}
    visa_free = out.get("visa_free") or {}
    return {
        "iso_alpha2": out.get("iso_alpha2"),
        "recommended_pathway": out.get("recommended_pathway"),
        "visa_free_max_stay_days": visa_free.get("max_stay_days"),
        "visa_free_conditions": visa_free.get("conditions"),
        "notes": out.get("notes", []),
        "data_as_of": out.get("data_as_of"),
    }


def build(script: Path) -> list[dict]:
    built = []
    for entry in CASES:
        record = dict(entry)
        record["truth"] = [truth_for(c, script) for c in entry["expected_calls"]]
        built.append(record)
    return built


def serialize(records: list[dict]) -> str:
    return "".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in records)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="exit non-zero if cases.jsonl is stale")
    parser.add_argument("--query-script", type=Path, default=DEFAULT_SCRIPT,
                        help="path to the skill's query_visa.py")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="cases.jsonl to write")
    args = parser.parse_args()

    out = args.out
    text = serialize(build(args.query_script))
    if args.check:
        current = out.read_text(encoding="utf-8") if out.is_file() else ""
        if current != text:
            print(f"{out}: stale - rerun build_visa_cases.py", file=sys.stderr)
            return 1
        print(json.dumps({"ok": True, "cases": len(CASES)}))
        return 0

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    print(json.dumps({"ok": True, "cases": len(CASES), "path": str(out)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
