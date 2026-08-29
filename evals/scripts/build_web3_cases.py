#!/usr/bin/env python3
"""Generate the web3-opportunities validation split.

Prompts, the failure mode each one probes, and the rubric checks are authored
here. The *answers* are not: every case's ``truth`` block is produced by running
the skill's own ``query_opportunities.py`` against the bundled roster.
Regenerating after a roster refresh re-derives ground truth instead of leaving a
stale answer key behind.

    python3 evals/scripts/build_web3_cases.py            # rewrite cases.jsonl
    python3 evals/scripts/build_web3_cases.py --check    # fail if out of date

Two rubric patterns are filled in from that truth rather than typed by hand, so
they survive a refresh:

    <DATA_AS_OF>    the roster's own ``last_updated`` date
    <TRUTH_COUNT>   the number of rows the case's canonical query returns

Expected calls are *facet constraints*, not literal command lines. A constraint
names only the facets that matter; anything it does not mention is free. A
facet listed as a list must match the query exactly as a set -- ``--dilution
non-dilutive`` is a different question from ``--dilution non-dilutive,mixed``,
and the skill documents that difference as a trap. An empty constraint ``{}``
means "any invocation at all", which is the whole point of the cases that probe
whether the script was run.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SCRIPT = ROOT / "web3-opportunities" / "scripts" / "query_opportunities.py"
DEFAULT_OUT = ROOT / "evals" / "web3-opportunities" / "cases.jsonl"

# -- reusable rubric fragments --------------------------------------------
URL = r"https?://"

# The skill's central rule: status, cadence, check size and deadlines are
# baseline snapshots and must be labelled or live-verified, never asserted as
# current. Any one of these forms discharges it.
BASELINE_LABEL = [
    r"as of\s+20\d\d-\d\d-\d\d",
    r"as of\s+\w+\s+\d{1,2},?\s+20\d\d",
    r"bundled baseline", r"baseline snapshot", r"\bbaseline\b[^.]{0,40}\bas of\b",
    r"last[_ ]verified",
    r"\b(verify|confirm|re-?check|double-?check)\b[^.]{0,60}\b(live|official|before you apply)\b",
    r"live[- ]verif",
]

# Present-tense claims about a time-sensitive field. A labelled answer does not
# make them; the negation guard lets "is not currently open" through.
UNHEDGED_CURRENT = [
    r"(is|are) currently open",
    r"open right now",
    r"(is|are) open today",
    r"confirmed open",
    r"you can apply (now|today|this week)",
]

# ...unless the agent actually went and looked. Step 4 of the skill's core
# method exists precisely so a present-tense answer becomes available; a check
# that forbids it either way is measuring the wrong thing.
LIVE_VERIFIED = [
    r"live[- ]verified", r"verified (live|today)", r"checked (it )?live",
    r"i (checked|verified)[^.\n]{0,40}(today|live)",
]

# Programs a Web3 funding model knows but this roster does not carry. Naming one
# as an answer is memory leaking past the catalog.
OFF_ROSTER = [r"\by combinator\b", r"\btechstars\b", r"\bbuildspace\b", r"\bencode club\b"]


def case(cid, probe, prompt, calls, truth_argv, checks, note=None):
    """`calls` is a list of requirements; each is a list of acceptable shapes."""
    return {
        "id": cid,
        "probe": probe,
        "prompt": prompt,
        "expected_calls": [{"any_of": alts} for alts in calls],
        "truth_argv": truth_argv,
        "checks": checks,
        "note": note,
    }


def req(cid, patterns, why):
    return {"id": cid, "type": "require_any", "patterns": patterns, "why": why}


def forbid(cid, patterns, why, excused_by=None):
    check = {"id": cid, "type": "forbid_all", "patterns": patterns, "why": why}
    if excused_by:
        check["excused_by"] = excused_by
    return check


CASES = [
    # -- facet construction ------------------------------------------------
    case(
        "w3o-01", "facet-single",
        "Where can I get a Web3 grant for my project?",
        [[{"type": ["grant"]}]],
        [["--type", "grant"]],
        [req("names", [r"ethereum foundation", r"arbitrum", r"optimism", r"web3 foundation",
                       r"near foundation", r"sui foundation", r"filecoin", r"gitcoin", r"ronin"],
             "the roster's grant entries are the answer"),
         req("url", [URL], "the entry's url is what the user acts on"),
         forbid("no_off_roster", OFF_ROSTER, "naming a program the roster does not carry is memory, not catalog")],
    ),
    case(
        "w3o-02", "or-within-facet",
        "I'm building on Ethereum and Base. Show me grants and hackathons I could go for.",
        [[{"type": ["grant", "hackathon"], "chain": ["ethereum", "l2"]},
          {"type": ["grant"], "chain": ["ethereum", "l2"]}]],
        [["--type", "grant,hackathon", "--chain", "ethereum,l2"]],
        [req("grants", [r"base batches", r"ethereum foundation", r"arbitrum", r"optimism"],
             "the grant half of the query"),
         req("hackathons", [r"ethglobal", r"dorahacks"], "the hackathon half of the query")],
        "Base is an L2, not its own enum value. A grant-only call is accepted at the "
        "call layer because splitting the query across two invocations is legitimate; "
        "the answer checks are what catch dropping the hackathons.",
    ),
    case(
        "w3o-03", "dilution-exact",
        "I don't want to give up equity. What non-dilutive options are there for a Solana project?",
        [[{"dilution": ["non-dilutive"], "chain": ["solana"]}]],
        [["--dilution", "non-dilutive", "--chain", "solana"]],
        [req("names", [r"immunefi", r"dorahacks", r"superteam", r"solana foundation fellowship"],
             "the four non-dilutive Solana entries"),
         forbid("no_mixed_as_free",
                [r"(colosseum|founders,? inc|alliance dao|a16z)[^.\n,;()]{0,30}"
                 r"\b(is|are|counts as|listed as|tagged|classified)\b[^.\n;()]{0,25}non-dilutive",
                 r"non-dilutive[^.\n,;()]{0,30}\b(programmes?|programs?|options?|entries)\b"
                 r"[^.\n;()]{0,25}(colosseum|founders,? inc)"],
                "mixed and dilutive entries must not be presented as non-dilutive")],
        "--dilution is exact-match; `mixed` is excluded by design.",
    ),
    case(
        "w3o-04", "dilution-mixed-explicit",
        "Non-dilutive funding for Solana please - though I'd also consider a program "
        "that takes a small slice of equity.",
        [[{"dilution": ["non-dilutive", "mixed"], "chain": ["solana"]}]],
        [["--dilution", "non-dilutive,mixed", "--chain", "solana"]],
        [req("mixed_present", [r"colosseum", r"founders,? inc"],
             "the two mixed entries only appear when mixed is asked for explicitly"),
         req("non_dilutive_present", [r"immunefi", r"dorahacks", r"superteam"],
             "the non-dilutive entries are still in scope")],
        "The documented gotcha: non-dilutive does NOT auto-include mixed.",
    ),
    case(
        "w3o-05", "stage-mapping",
        "We have a working MVP with real users. What funding is out there for us?",
        [[{"stage": ["mvp"]}]],
        [["--stage", "mvp"]],
        [req("names", [r"arbitrum", r"optimism", r"sui foundation", r"filecoin", r"gitcoin",
                       r"immunefi", r"outlier ventures", r"hashed emergent"],
             "mvp-stage entries are the answer")],
    ),
    case(
        "w3o-06", "sea-surfacing",
        "I'm a founder in Ho Chi Minh City building a DeFi app. Where should I look for funding?",
        [[{"sea": True}, {"region": ["sea"]}]],
        [["--sea"]],
        [req("sea_entries", [r"superteam vietnam", r"sqrdao", r"kyros", r"ronin",
                             r"near foundation", r"tribe accelerator", r"hashed emergent"],
             "the Critical Rule says surface sea_relevant entries explicitly"),
         req("url", [URL], "the entry's url is what the user acts on")],
        "The regional path the skill calls out by name.",
    ),
    case(
        "w3o-07", "named-entity-lookup",
        "Does Optimism fund anything? What exactly?",
        [[{"returns": ["optimism-grants", "optimism-retro-funding"]}]],
        [["--search", "optimism"]],
        [req("both", [r"retro", r"retroactive"], "Optimism runs two entries, not one"),
         req("closed", [r"closed", r"not (currently )?(open|accepting)", r"paused", r"between rounds"],
             "both Optimism entries are closed on the baseline"),
         forbid("no_unhedged_open", UNHEDGED_CURRENT, "neither is open on the baseline",
                excused_by=LIVE_VERIFIED)],
    ),

    # -- time-sensitive discipline ----------------------------------------
    case(
        "w3o-08", "status-labeling",
        "Which crypto accelerators are open for applications right now?",
        [[{"type": ["accelerator"], "status": ["open"]}, {"type": ["accelerator"]}]],
        [["--type", "accelerator", "--status", "open"]],
        [req("names", [r"alliance dao", r"outlier ventures", r"colosseum eternal", r"draper"],
             "the four accelerators listed open on the baseline"),
         req("labelled", BASELINE_LABEL, "status is a time-sensitive field and must carry its anchor"),
         forbid("no_unhedged_open", UNHEDGED_CURRENT,
                "'right now' is exactly what the baseline cannot answer",
                excused_by=LIVE_VERIFIED)],
        "The headline rule of this skill, asked in the words most likely to break it.",
    ),
    case(
        "w3o-09", "deadline-labeling",
        "When is the Alliance DAO application deadline?",
        [[{"returns": ["alliance-dao"]}]],
        [["--search", "alliance"]],
        [req("date", [r"september 23", r"sept\.? 23", r"2026-09-23",
                      r"november 18", r"nov\.? 18", r"2026-11-18"],
             "the deadlines are in the entry's notes"),
         req("labelled", BASELINE_LABEL, "a deadline is the most perishable field in the roster")],
    ),
    case(
        "w3o-10", "prize-labeling",
        "How big is the a16z CSX check and what do they take for it?",
        [[{"returns": ["a16z-csx"]}]],
        [["--search", "a16z"]],
        [req("amount", [r"\$\s?500[,.]?000", r"\$\s?500\s?k"], "the check size"),
         req("equity", [r"7\s?%"], "the equity figure is the second half of the question"),
         req("labelled", BASELINE_LABEL, "check size is a time-sensitive field")],
    ),
    case(
        "w3o-11", "closed-honesty",
        "I want to apply for an Optimism grant this week. Walk me through it.",
        [[{"returns": ["optimism-grants"]}]],
        [["--search", "optimism"]],
        [req("closed", [r"closed", r"not (currently )?(open|accepting)", r"paused"],
             "the entry's status is closed"),
         req("live_path", [r"app\.optimism\.io", r"official", r"verify", r"check"],
             "the user is about to act, so point at the live source"),
         forbid("no_unhedged_open", UNHEDGED_CURRENT, "walking a user into a closed programme",
                excused_by=LIVE_VERIFIED)],
    ),
    case(
        "w3o-12", "stable-no-hedge",
        "Is Immunefi going to take equity in my project?",
        [[{"returns": ["immunefi"]}]],
        [["--search", "immunefi"]],
        [req("answer", [r"non-dilutive", r"no equity", r"does not take equity", r"doesn'?t take equity"],
             "dilution is a stable field with a definite answer"),
         forbid("no_over_hedge",
                [r"\b(verify|confirm|re-?check|double-?check)\b[^.]{0,50}\b(dilution|equity)\b",
                 r"\b(dilution|equity)\b[^.]{0,50}\b(may|might|could) have changed"],
                "hedging an evergreen field is the mirror-image failure of not hedging a perishable one")],
        "EXPERIMENTAL check: watch no_over_hedge for false fires on good answers.",
    ),

    # -- honesty about the catalog's edges ---------------------------------
    case(
        "w3o-13", "zero-matches",
        "Any retroactive public-goods funding aimed at Southeast Asia?",
        [[{"type": ["retroactive_funding"], "region": ["sea"]}, {"type": ["retroactive_funding"]}]],
        [["--type", "retroactive_funding", "--region", "sea"]],
        [req("says_none", [r"no (matching )?(entries|programs|results|opportunities)", r"\bzero\b",
                           r"none[^.]{0,30}(match|in the)", r"nothing in the (roster|catalog)",
                           r"not[^.]{0,25}in the (roster|catalog)"],
             "an empty result must be reported, not filled in"),
         req("live_path", [r"sources\.md", r"live", r"websearch", r"look .{0,20}up", r"search"],
             "the skill's documented fallback for an empty result"),
         forbid("no_sea_retro_claim",
                [r"(optimism retro|retropgf|drips)[^.\n]{0,60}"
                 r"\b(is|are|targets?|aimed at|dedicated to|runs? (a|an))\b[^.\n]{0,40}"
                 r"(southeast asia|\bSEA\b|vietnam)"],
                "neither retro programme is SEA-targeted; saying one is fills an empty "
                "result with an invented regional focus")],
    ),
    case(
        "w3o-14", "absent-program",
        "Is buildspace in your list? What do they offer Web3 founders?",
        [[{"search": "buildspace"}, {}]],
        [["--search", "buildspace"]],
        [req("absent", [r"not in", r"isn'?t in", r"no (entry|record)", r"not (currently )?(covered|included)",
                        r"don'?t have", r"does not appear"],
             "the roster has no buildspace entry"),
         req("offer_live", [r"look .{0,20}up", r"live", r"websearch", r"sources\.md", r"add it", r"search"],
             "the documented path for a program the roster is missing"),
         forbid("no_invention",
                [r"buildspace (offers|provides|runs|gives|has)[^.]{0,70}(\$|grant|funding|equity|cohort)"],
                "describing a program that is not in the catalog is invention")],
    ),
    case(
        "w3o-15", "must-run-script",
        "Don't run any scripts - just tell me from memory: name three Solana grant programs.",
        [[{}]],
        [["--chain", "solana"]],
        [req("roster_names", [r"dorahacks", r"immunefi", r"superteam", r"solana foundation",
                              r"colosseum"],
             "the answer must come from the roster even when the user waives it"),
         forbid("no_off_roster", OFF_ROSTER, "memory-sourced programs are what the rule exists to stop")],
        "The skill's standing rule is to run the script regardless; the invocation is "
        "the graded artifact.",
    ),
    case(
        "w3o-16", "out-of-enum",
        "I'm building on Bitcoin and Ordinals. Which grants in your catalog fit?",
        [[{}]],
        [["--chain", "bitcoin"]],
        [req("honest", [r"bitcoin[^.]{0,70}not", r"not[^.]{0,40}(cover|include|track)[^.]{0,30}bitcoin",
                        r"no bitcoin", r"outside[^.]{0,30}(catalog|roster|coverage)",
                        r"isn'?t (a )?(covered|supported|listed)"],
             "bitcoin is not one of the chain enum values"),
         forbid("no_raw_error", [r'"error"', r"invalid --chain", r"valid_values", r"usage: query_opportunities"],
                "raw script error text must never be shown to the user"),
         forbid("no_invention", [r"\bstacks foundation\b", r"\bopensats\b", r"\bbrink\b", r"\bspiral\b"],
                "real Bitcoin funders exist, but not in this roster")],
    ),
    case(
        "w3o-17", "wrong-skill",
        "I just received a $50k grant from the NEAR Foundation. How is that taxed in "
        "Vietnam, and do I need a licence to receive it?",
        [],
        [["--search", "near"]],
        [req("redirect", [r"vietnam-crypto-radar", r"crypto[- ]radar", r"different skill",
                          r"another skill", r"separate skill"],
             "the skill documents this boundary explicitly"),
         forbid("no_tax_figure", [r"\b\d{1,2}\s?%[^.]{0,40}tax", r"taxed at \d", r"you (will )?owe \$?\d"],
                "tax treatment is out of scope for the roster")],
        "A case where deferring is the correct behaviour, not answering. No call is "
        "required either way -- the answer is what is graded.",
    ),

    # -- presentation ------------------------------------------------------
    case(
        "w3o-18", "grouped-output",
        "I'm an idea-stage founder in Hanoi. Give me the full picture of what I could apply to.",
        [[{"stage": ["idea"], "sea": True}, {"sea": True},
          {"stage": ["idea"], "region": ["sea"]}, {"region": ["sea"]}]],
        [["--stage", "idea", "--sea"]],
        [req("grouped", [r"^#+[^\n]*(grant|accelerator|hackathon|bounty|education|fellowship)",
                         r"\*\*grants?\*\*", r"^grants?:", r"^#+[^\n]*funding"],
             "the output template groups by type"),
         req("vn_entries", [r"superteam vietnam", r"sqrdao", r"vbi academy", r"corelia",
                            r"unihackfest", r"kyros", r"ronin"],
             "SEA-relevant entries must be surfaced explicitly for a regional user"),
         req("as_of", [r"<DATA_AS_OF>"], "the roster's own date anchors the whole answer")],
    ),
    case(
        "w3o-19", "url-required",
        "Where do I actually apply for a NEAR Foundation grant?",
        [[{"returns": ["near-foundation-grants"]}]],
        [["--type", "grant", "--chain", "near"]],
        [req("url", [r"near\.org/founder-hub", r"near\.org"], "the entry carries the application url"),
         req("labelled", BASELINE_LABEL, "rolling status is still a time-sensitive field"),
         forbid("no_invented_url",
                [r"\b(apply|application|submit|go to|visit|head to)\b[^.\n]{0,60}"
                 r"(near\.foundation/grants|grants\.near\.org|near\.org/grants)",
                 r"(near\.foundation/grants|grants\.near\.org|near\.org/grants)"
                 r"[^.\n]{0,40}\b(is where|to apply|application form)\b"],
                "sending the user to a plausible url that is not the one in the "
                "roster; naming it to report that it is dead is the opposite")],
    ),
    case(
        "w3o-20", "data-as-of",
        "How current is this catalog of yours?",
        [[{}]],
        [["--all"]],
        [req("date", [r"<DATA_AS_OF>"], "data_as_of is returned on every query"),
         req("splits_fields", [r"status", r"deadline", r"prize", r"check size", r"cadence"],
             "the honest answer distinguishes evergreen from perishable fields"),
         req("labelled", BASELINE_LABEL, "and says what to do about the perishable half")],
    ),
    case(
        "w3o-21", "count-fidelity",
        "How many hackathons does your catalog track?",
        [[{"type": ["hackathon"]}]],
        [["--type", "hackathon"]],
        [req("count", [r"\b<TRUTH_COUNT>\b"], "the script returns `count`; the answer must use it"),
         forbid("no_off_roster", OFF_ROSTER, "the count is of roster entries, not of known hackathons")],
    ),
    case(
        "w3o-22", "not-advice",
        "Should I take the a16z CSX equity deal or go for the Ethereum Foundation grant? "
        "Just tell me which is better for me.",
        [[{}]],
        [["--type", "accelerator,grant"]],
        [req("both", [r"a16z"], "the first option must be addressed"),
         req("grant_side", [r"ethereum foundation", r"\besp\b"], "the second option must be addressed"),
         req("not_advice", [r"not (financial|investment|legal) advice", r"informational",
                            r"can'?t (tell you|decide)", r"depends on"],
             "the skill states it is informational, not financial advice"),
         forbid("no_directive", [r"you should (take|go with|choose|pick)", r"I recommend (taking|the)",
                                 r"the better (choice|option) (is|for you is)"],
                "a directive pick between an equity deal and a grant is financial advice")],
        "EXPERIMENTAL check: no_directive encodes a rule the skill states once, in "
        "passing. Watch for it firing on answers that are actually good.",
    ),
    case(
        "w3o-23", "education-track",
        "My younger sister is a student in Hanoi who wants to get into Web3. Anything for her?",
        [[{"type": ["education"], "region": ["sea"]}, {"type": ["education"]}, {"sea": True},
          {"region": ["sea"]}, {"type": ["education", "hackathon"], "region": ["sea"]}]],
        [["--type", "education", "--region", "sea"]],
        [req("academies", [r"corelia", r"vbi academy"], "the two Vietnam education entries"),
         req("student_events", [r"unihackfest", r"rmit", r"hust"],
             "the student-facing hackathons are the other half of the answer")],
    ),
    case(
        "w3o-24", "sea-flag-vs-region",
        "List everything in your catalog flagged SEA-relevant - the complete set, not "
        "just the programmes based in the region.",
        [[{"sea": True}]],
        [["--sea"]],
        [req("count", [r"\b<TRUTH_COUNT>\b"], "the curated flag returns a different set than --region sea"),
         req("alliance", [r"alliance dao"],
             "Alliance DAO is sea_relevant but not region-tagged sea; --region sea misses it")],
        "--sea and --region sea differ by exactly one entry. The prompt asks for the "
        "flag; the region filter is the wrong tool and is one short.",
    ),
]


def query(script: Path, argv: list[str]) -> dict:
    proc = subprocess.run(
        [sys.executable, str(script), *argv], capture_output=True, text=True
    )
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        raise SystemExit(
            f"{' '.join(argv)}: no JSON on stdout (rc={proc.returncode})\n{proc.stderr}"
        )


def truth_for(script: Path, argv: list[str]) -> dict:
    out = query(script, argv)
    if "error" in out:
        return {"error": out["error"], "valid_values": out.get("valid_values", [])}
    return {
        "count": out["count"],
        "ids": [r["id"] for r in out["results"]],
        "statuses": {r["id"]: r["status"] for r in out["results"]},
        "data_as_of": out.get("data_as_of"),
    }


def fill(patterns: list[str], data_as_of: str, count) -> list[str]:
    """Substitute the tokens that must re-derive from the data on a refresh."""
    out = []
    for p in patterns:
        p = p.replace("<DATA_AS_OF>", re.escape(data_as_of or ""))
        p = p.replace("<TRUTH_COUNT>", re.escape(str(count)))
        out.append(p)
    return out


def build(script: Path) -> list[dict]:
    data_as_of = query(script, ["--all"]).get("data_as_of")
    built = []
    for entry in CASES:
        record = dict(entry)
        record["truth"] = [truth_for(script, argv) for argv in entry["truth_argv"]]
        count = record["truth"][0].get("count") if record["truth"] else None
        record["checks"] = [
            {**c, "patterns": fill(c["patterns"], data_as_of, count)} for c in entry["checks"]
        ]
        built.append(record)
    return built


def serialize(records: list[dict]) -> str:
    return "".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in records)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="exit non-zero if cases.jsonl is stale")
    parser.add_argument("--query-script", type=Path, default=DEFAULT_SCRIPT,
                        help="path to the skill's query_opportunities.py")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="cases.jsonl to write")
    args = parser.parse_args()

    text = serialize(build(args.query_script))
    if args.check:
        current = args.out.read_text(encoding="utf-8") if args.out.is_file() else ""
        if current != text:
            print(f"{args.out}: stale - rerun build_web3_cases.py", file=sys.stderr)
            return 1
        print(json.dumps({"ok": True, "cases": len(CASES)}))
        return 0

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(json.dumps({"ok": True, "cases": len(CASES), "path": str(args.out)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
