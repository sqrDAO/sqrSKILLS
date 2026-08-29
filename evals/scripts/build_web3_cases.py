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
OUT_V1 = ROOT / "evals" / "web3-opportunities" / "cases.jsonl"
OUT_V2 = ROOT / "evals" / "web3-opportunities" / "cases-v2.jsonl"

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


def forbid(cid, patterns, why, excused_by=None, turn=None):
    check = {"id": cid, "type": "forbid_all", "patterns": patterns, "why": why}
    if excused_by:
        check["excused_by"] = excused_by
    if turn is not None:
        check["turn"] = turn
    return check


def req2(cid, patterns, why, turn=None):
    check = {"id": cid, "type": "require_any", "patterns": patterns, "why": why}
    if turn is not None:
        check["turn"] = turn
    return check


def case2(cid, probe, turns, calls, truth_argv, checks, note=None, web_allowed=True):
    """A v2 case. `turns` is the user's side of the exchange, in order.

    `calls` is a list of (alternatives, turn) -- `turn` pins the requirement to
    one turn, or None to accept it anywhere. `web_allowed=False` runs the case
    with the live-enrichment layer switched off, which is the only way to see
    what the catalog alone is carrying.
    """
    return {
        "id": cid, "probe": probe, "turns": turns,
        "expected_calls": [
            {"any_of": alts, **({"turn": t} if t is not None else {})}
            for alts, t in calls
        ],
        "truth_argv": truth_argv, "checks": checks, "note": note,
        "web_allowed": web_allowed,
    }


# A claim that the agent went and looked. On a web-disabled case it cannot be
# true, so the same list that *excuses* a present-tense claim elsewhere becomes
# the thing to forbid.
NO_WEB_FORBID = [
    r"live[- ]verified", r"verified (live|today)", r"i (checked|verified)[^.\n]{0,40}(today|live)",
    r"as of today[^.\n]{0,30}(the (page|site)|official)",
]


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


# ---------------------------------------------------------------------------
# v2 — the replacement split.
#
# v1 saturated at 24/24, which means it can no longer gate an edit. Every case
# below targets something v1 could not see:
#
#   * the catalog path with the live-enrichment layer switched off. Most of v1's
#     hardest probes were passed by going to the web, which is legitimate but
#     means v1 was measuring the enrichment layer as much as the roster.
#   * multi-turn exchanges, where the failure is reusing turn 1's result instead
#     of re-querying for what turn 2 actually asked.
#   * rules the skill states and v1 never tested: live-beats-baseline drift
#     reporting, offering to add a missing program, Tier-1 source discipline.
#   * a user premise that contradicts the roster, in both directions.
# ---------------------------------------------------------------------------

CASES_V2 = [
    # -- the catalog alone, with no web to fall back on -------------------
    case2(
        "v2-01", "roster-only-status",
        ["Which crypto accelerators are open for applications right now?"],
        [([{"type": ["accelerator"], "status": ["open"]}, {"type": ["accelerator"]}], None)],
        [["--type", "accelerator", "--status", "open"]],
        [req("names", [r"alliance dao", r"outlier ventures", r"colosseum eternal", r"draper"],
             "the four accelerators listed open on the baseline"),
         req("labelled", BASELINE_LABEL, "with no live check available, the anchor is all there is"),
         forbid("no_unhedged_open", UNHEDGED_CURRENT,
                "'right now' cannot be answered from a snapshot, and this time there is no web"),
         forbid("no_live_claim", NO_WEB_FORBID, "web access was unavailable for this turn")],
        "v1's equivalent passed by going live. This is the same question with the "
        "escape hatch closed, and it is the only way to see whether the labelling "
        "rule is carrying weight on its own.",
        web_allowed=False,
    ),
    case2(
        "v2-02", "roster-only-absent",
        ["I'm building on Bitcoin. Which grants in your catalog fit?"],
        [([{}], None)],
        [["--type", "grant"]],
        [req("honest", [r"bitcoin[^.\n]{0,70}not", r"not[^.\n]{0,40}(cover|include|track)[^.\n]{0,30}bitcoin",
                        r"no bitcoin", r"outside[^.\n]{0,30}(catalog|roster|coverage)"],
             "bitcoin is not one of the chain enum values"),
         forbid("no_invention", [r"\bstacks foundation\b", r"\bopensats\b", r"\bbrink\b", r"\bspiral\b",
                                 r"\bhuman rights foundation\b"],
                "with no web, naming a Bitcoin funder can only come from memory"),
         forbid("no_live_claim", NO_WEB_FORBID, "web access was unavailable for this turn")],
        web_allowed=False,
    ),
    case2(
        "v2-03", "roster-only-deadline",
        ["When is the Alliance DAO application deadline?"],
        [([{"returns": ["alliance-dao"]}], None)],
        [["--search", "alliance"]],
        [req("date", [r"september 23", r"sept\.? 23", r"2026-09-23",
                      r"november 18", r"nov\.? 18", r"2026-11-18"],
             "the deadlines are in the entry's notes"),
         req("labelled", BASELINE_LABEL, "a deadline is the most perishable field in the roster"),
         req("says_verify", [r"\b(verify|confirm|check)\b", r"before you (apply|submit)"],
             "unable to check live, the agent must hand the check to the user"),
         forbid("no_live_claim", NO_WEB_FORBID, "web access was unavailable for this turn")],
        web_allowed=False,
    ),

    # -- multi-turn ---------------------------------------------------------
    case2(
        "v2-04", "refacet-on-followup",
        ["I don't want to give up equity. What non-dilutive options are there for a Solana project?",
         "Actually, on reflection I'd take a program that wants a small slice of equity. Redo that."],
        [([{"dilution": ["non-dilutive"], "chain": ["solana"]}], 0),
         ([{"dilution": ["non-dilutive", "mixed"], "chain": ["solana"]},
           {"dilution": ["mixed"], "chain": ["solana"]}], 1)],
        [["--dilution", "non-dilutive,mixed", "--chain", "solana"]],
        [req2("mixed_present", [r"colosseum", r"founders,? inc"],
              "the two mixed entries only appear once mixed is asked for", turn=1)],
        "The failure mode is answering turn 2 from turn 1's result set. `mixed` "
        "entries are not in it, so reuse is visible.",
    ),
    case2(
        "v2-05", "context-carryover",
        ["I'm an idea-stage founder in Hanoi.",
         "What hackathons specifically?"],
        [([{"sea": True}, {"region": ["sea"]}, {"stage": ["idea"], "sea": True},
           {"stage": ["idea"], "region": ["sea"]}], None)],
        [["--type", "hackathon", "--sea"]],
        [req2("vn_hackathons", [r"unihackfest", r"hust", r"rmit", r"vietbuidl", r"vietnam aptos"],
              "the regional context from turn 1 must survive into turn 2", turn=1),
         forbid("no_restart", [r"where are you based", r"which region", r"what stage are you"],
                "asking again for what the user already said")],
    ),
    case2(
        "v2-06", "user-contradicts-roster",
        ["Can I apply for an Optimism grant?",
         "That's not right - I'm looking at an open Optimism application form on my screen right now."],
        [([{"returns": ["optimism-grants"]}], 0)],
        [["--search", "optimism"]],
        [req2("live_wins",
              # The claim is "your live observation outranks my snapshot". It can
              # be made about the page, the live data, or the user -- pinning one
              # subject failed a gold answer that said it three different ways.
              [r"\b(live|the page|what you'?re seeing|your (screen|page|browser|observation))\b"
               r"[^.\n]{0,45}\b(wins|beats|takes precedence|trumps|overrides|is right|over (my|the))\b",
               r"take your word", r"you'?re right", r"i'?ll (trust|go with|defer|take)",
               r"believe you", r"defer to"],
              "the skill says live data beats the baseline when they conflict", turn=1),
         req2("notes_drift", [r"data file", r"roster", r"catalog", r"update", r"fix", r"drift", r"stale"],
              "and says the drift should be recorded so the data gets fixed", turn=1),
         forbid("no_stonewall", [r"the (roster|catalog|data) says closed,? so", r"i (must|have to) go with the (roster|baseline)"],
                "insisting on the snapshot against the user's live observation")],
        "A rule the skill states plainly and v1 never tested: 'When live data "
        "contradicts the baseline, live wins; note the drift so it can be fixed "
        "in the data file later.'",
    ),
    case2(
        "v2-07", "narrow-on-followup",
        ["What grants are in your catalog?",
         "Only the ones actually open, please."],
        [([{"type": ["grant"]}], 0),
         ([{"type": ["grant"], "status": ["open"]}, {"type": ["grant"]}], 1)],
        [["--type", "grant", "--status", "open"]],
        [req2("open_three", [r"interchain", r"sui foundation", r"filecoin"],
              "three grants carry status open on the baseline", turn=1),
         forbid("no_closed_as_open", [r"optimism grants[^.\n]{0,40}\bopen\b",
                                      r"web3 foundation[^.\n]{0,40}\bopen\b"],
                "the closed and discontinued grants must not survive the narrowing", turn=1)],
    ),

    # -- rules the skill states and v1 never tested -------------------------
    case2(
        "v2-08", "drift-single-turn",
        ["Heads up: Sui Foundation grants closed last month. Your data says open."],
        [([{"returns": ["sui-foundation-grants"]}], None)],
        [["--search", "sui"]],
        [req("accepts", [r"live[^.\n]{0,30}wins", r"you'?re right", r"trust", r"take your word",
                         r"more recent", r"believe you", r"defer"],
             "live beats the baseline when they conflict"),
         req("records", [r"data file", r"update the (roster|catalog|entry)", r"fix", r"drift", r"flag"],
             "and the drift gets recorded rather than silently absorbed")],
    ),
    case2(
        "v2-09", "mentioned-but-not-an-entry",
        ["Encode Club runs Web3 hackathons. Why isn't it in your catalog?"],
        [([{"search": "encode"}, {}], None)],
        [["--search", "encode"]],
        [req("distinguishes", [r"no (entry|record)", r"not (a|an) (entry|programme|program)",
                               r"isn'?t (a|an) (entry|its own)", r"only (appears|mentioned)",
                               r"in the notes", r"mentioned"],
             "Encode Club appears inside two entries' notes but has no entry of its own"),
         req("offers_add", [r"add it", r"add (them|encode)", r"data file", r"i can add"],
             "the skill's documented response to a missing programme")],
        "A search for 'encode' returns two rows -- neither of them Encode Club. "
        "Reporting those as a match is the failure.",
    ),
    case2(
        "v2-10", "alias-rename",
        ["What's Binance Labs up to these days?"],
        [([{"returns": ["yzi-labs"]}], None)],
        [["--search", "binance"]],
        [req("resolves", [r"yzi labs", r"yzi"], "the entry is named 'YZi Labs (formerly Binance Labs)'"),
         req("notes_rename", [r"formerly", r"renamed", r"now (called|known)", r"used to be"],
             "the rename is the answer to the question as asked")],
    ),
    case2(
        "v2-11", "tier-1-discipline",
        ["How should I confirm the ETHGlobal event dates before I book flights?"],
        [([{"returns": ["ethglobal"]}], None)],
        [["--search", "ethglobal"]],
        [req("official", [r"ethglobal\.com", r"official (page|site)", r"their own (page|site)", r"tier-?1"],
             "sources.md ranks the programme's own page first"),
         req("why", [r"time[- ]sensitive", r"change", r"move", r"baseline", r"snapshot"],
             "and says why a second check is needed at all")],
    ),

    # -- facet edges v1 never reached ---------------------------------------
    case2(
        "v2-12", "contradictory-ask",
        ["I want an accelerator that doesn't take any equity. What have you got?"],
        [([{"type": ["accelerator"], "dilution": ["non-dilutive"]}, {"type": ["accelerator"]}], None)],
        [["--type", "accelerator", "--dilution", "non-dilutive"]],
        [req("says_none", [r"\bno\b[^.\n]{0,40}(accelerator|match)", r"\bzero\b", r"none of",
                           r"nothing[^.\n]{0,30}match", r"doesn'?t exist", r"not a thing"],
             "no accelerator in the roster is non-dilutive -- the ask is self-contradictory"),
         req("explains", [r"by (design|definition|nature)", r"accelerators[^.\n]{0,40}(equity|dilutive)",
                          r"that'?s what[^.\n]{0,30}(accelerator|dilutive)", r"trade"],
             "and says why, rather than just reporting an empty set"),
         req("redirects", [r"grant", r"hackathon", r"bounty", r"non-dilutive"],
             "the non-dilutive types are the useful answer to the intent behind the ask")],
    ),
    case2(
        "v2-13", "growth-stage",
        ["We're past product-market fit, about forty people, raising a Series A. What's still relevant to us?"],
        [([{"stage": ["growth"]}], None)],
        [["--stage", "growth"]],
        [req("names", [r"gitcoin", r"immunefi", r"arbitrum", r"interchain", r"sui foundation",
                       r"drips", r"yzi labs"],
             "ten entries are tagged growth stage"),
         forbid("no_idea_stage_only", [r"unihackfest", r"vbi academy", r"corelia"],
                "student and education entries are idea/pre-seed only")],
    ),
    case2(
        "v2-14", "india-region",
        ["I'm based in Bangalore. What's reachable from here?"],
        [([{"region": ["india"]}], None)],
        [["--region", "india"]],
        [req("names", [r"ethglobal", r"dorahacks", r"hashed emergent", r"solana"],
             "four entries carry the india region tag"),
         req("count_or_list", [r"\bfour\b", r"\b4\b", r"hashed emergent"],
             "the india set is small and specific")],
    ),
    case2(
        "v2-15", "discontinued-not-closed",
        ["I'm building on Polkadot. Can I get a Web3 Foundation grant?"],
        [([{"returns": ["web3-foundation-grants"]}], None)],
        [["--type", "grant", "--chain", "polkadot"]],
        [req("not_available", [r"discontinued", r"closed", r"no new applications", r"not accepting",
                               r"shut", r"ended"],
             "the programme is discontinued, not merely between rounds"),
         req("routes_on", [r"treasury", r"parachain", r"moonbeam", r"acala", r"open source developer grants",
                           r"polkadot hackathon"],
             "the entry's notes carry where builders are sent instead"),
         forbid("no_unhedged_open", UNHEDGED_CURRENT, "it is not open", excused_by=LIVE_VERIFIED)],
    ),

    # -- precision and adversarial ------------------------------------------
    case2(
        "v2-16", "false-premise-dilution",
        ["Your catalog lists a16z CSX as non-dilutive, right? I just want to confirm before I apply."],
        [([{"returns": ["a16z-csx"]}], None)],
        [["--search", "a16z"]],
        [req("corrects", [r"\bno\b", r"not (quite|correct|right)", r"actually", r"incorrect",
                          r"that'?s wrong", r"other way"],
             "the premise is false -- CSX is dilutive"),
         req("states_terms", [r"7\s?%", r"dilutive", r"equity"], "and gives the real posture"),
         forbid("no_agreement", [r"yes,? (that'?s|it'?s) (right|correct)", r"confirmed[^.\n]{0,20}non-dilutive",
                                 r"correct[^.\n]{0,25}non-dilutive"],
                "agreeing with a false premise about equity is the expensive failure here")],
    ),
    case2(
        "v2-17", "pressure-to-guess",
        ["Don't hedge, just give me your best guess for the next Colosseum hackathon deadline. A date."],
        [([{"returns": ["colosseum-hackathon"]}], None)],
        [["--search", "colosseum"]],
        [req("baseline_date", [r"sep(tember)?\.? ?28", r"nov(ember)?\.? ?2", r"2026-09-28"],
             "the baseline carries the Fall 2026 window"),
         req("labelled", BASELINE_LABEL, "a guessed date is the one thing this skill must not produce"),
         forbid("no_invented_precision", [r"registration closes on \w+ \d{1,2}",
                                          r"the deadline is definitely", r"i'?m confident it'?s"],
                "inventing a precision the roster does not carry")],
    ),
    case2(
        "v2-18", "exact-count-requested",
        ["Give me exactly three non-dilutive options for an Ethereum project. Three, not a wall of text."],
        [([{"dilution": ["non-dilutive"], "chain": ["ethereum"]}], None)],
        [["--dilution", "non-dilutive", "--chain", "ethereum"]],
        [req("names", [r"ethereum foundation", r"arbitrum", r"gitcoin", r"ethglobal", r"immunefi",
                       r"drips", r"base batches"],
             "eleven match; three must be chosen from them"),
         forbid("no_wall", [r"## (Grants|Accelerators|Hackathons|Bounties)[\s\S]{2500,}"],
                "the user asked for three and said why")],
        "EXPERIMENTAL check: no_wall is a length proxy for a judgement. Watch it.",
    ),
    case2(
        "v2-19", "which-fields-to-recheck",
        ["Of everything you just told me about a programme, which bits should I actually re-check myself?"],
        [([{}], None)],
        [["--all"]],
        [req("perishable", [r"status", r"deadline", r"cadence", r"check size", r"prize"],
             "the time-sensitive set is the answer"),
         req("evergreen", [r"chain", r"region", r"dilution", r"stage", r"what it is", r"stable", r"evergreen"],
             "and the stable half is what does not need re-checking"),
         forbid("no_recheck_everything", [r"re-?check everything", r"verify (all|everything)",
                                          r"all of it[^.\n]{0,20}verify"],
                "telling the user to re-verify the evergreen fields wastes the catalog")],
    ),
    case2(
        "v2-20", "two-skill-split",
        ["Is launching a token from Vietnam legal, and which accelerator should I apply to?"],
        [([{"type": ["accelerator"]}, {}], None)],
        [["--type", "accelerator"]],
        [req("redirect", [r"vietnam-crypto-radar", r"crypto[- ]radar", r"different skill", r"another skill"],
             "the legal half belongs to the other skill"),
         req("answers_half", [r"alliance dao", r"a16z", r"outlier ventures", r"antler", r"colosseum",
                              r"hashed emergent", r"tribe", r"draper"],
             "the accelerator half is squarely in scope and must still be answered"),
         forbid("no_legal_answer", [r"\bis legal\b", r"\bit'?s legal\b", r"you (can|may) legally",
                                    r"\bpermitted under\b"],
                "answering the legality question from this skill")],
        "v1's boundary case only tested deferral. This one tests that deferring "
        "the out-of-scope half does not swallow the half that is in scope.",
    ),
    case2(
        "v2-21", "roster-only-count",
        ["How many programmes in your catalog take equity?"],
        [([{"dilution": ["dilutive"]}, {}, {"dilution": ["dilutive", "mixed"]}], None)],
        [["--dilution", "dilutive"]],
        [req("count", [r"\b<TRUTH_COUNT>\b"], "eleven are tagged dilutive"),
         req("mixed_noted", [r"mixed", r"two more", r"\btwo\b", r"\b13\b", r"partly"],
             "two more are `mixed`, which the honest answer separates rather than merges"),
         forbid("no_live_claim", NO_WEB_FORBID, "web access was unavailable for this turn")],
        web_allowed=False,
    ),
    case2(
        "v2-22", "followup-reverses",
        ["Show me the SEA-relevant programmes.",
         "Now drop anything that would take equity."],
        [([{"sea": True}, {"region": ["sea"]}], 0),
         ([{"sea": True, "dilution": ["non-dilutive"]},
           {"region": ["sea"], "dilution": ["non-dilutive"]},
           {"dilution": ["non-dilutive"], "sea": True}], 1)],
        [["--sea", "--dilution", "non-dilutive"]],
        [req2("keeps_nondilutive", [r"superteam", r"sqrdao", r"near foundation", r"ronin", r"dorahacks"],
              "the non-dilutive SEA entries survive the filter", turn=1),
         forbid("no_dilutive_survivors", [r"alliance dao", r"yzi labs", r"kyros", r"antler",
                                          r"tribe accelerator", r"hashed emergent"],
                "every one of these is dilutive and must be gone after turn 2", turn=1)],
    ),
    case2(
        "v2-23", "zero-then-widen",
        ["Any accelerators in Southeast Asia that take idea-stage teams?",
         "Nothing at all? Widen it however you need to."],
        [([{"type": ["accelerator"], "region": ["sea"], "stage": ["idea"]},
           {"type": ["accelerator"], "sea": True, "stage": ["idea"]}], 0)],
        [["--type", "accelerator", "--region", "sea", "--stage", "idea"]],
        [req2("says_none", [r"\bzero\b", r"\bno\b[^.\n]{0,40}match", r"none", r"nothing"],
              "the first query returns nothing", turn=0),
         req2("widened", [r"alliance dao", r"colosseum", r"antler", r"kyros", r"hashed emergent",
                          r"incubator", r"yzi"],
              "turn 2 explicitly authorises widening, so an empty answer twice is wrong", turn=1),
         req2("says_what_changed", [r"drop", r"widen", r"relax", r"without", r"instead of", r"loosen"],
              "and the agent must say which facet it gave up", turn=1)],
        "v1 tested reporting an empty result. This tests the harder half: "
        "widening on request while saying what was given up.",
    ),
    case2(
        "v2-24", "url-fidelity",
        ["Where do I apply for a Gitcoin grant?"],
        [([{"returns": ["gitcoin"]}], None)],
        [["--search", "gitcoin"]],
        [req("url", [r"gitcoin\.co"], "the entry carries the url"),
         forbid("no_invented_url", [r"\b(apply|go to|visit|head to)\b[^.\n]{0,50}"
                                    r"(gitcoin\.io|grants\.gitcoin\.co|gitcoin\.org)"],
                "a plausible url that is not the one in the roster")],
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


def build(script: Path, cases: list[dict]) -> list[dict]:
    data_as_of = query(script, ["--all"]).get("data_as_of")
    built = []
    for entry in cases:
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


SPLITS = {"v1": (CASES, OUT_V1), "v2": (CASES_V2, OUT_V2)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="exit non-zero if any split's cases file is stale")
    parser.add_argument("--split", choices=("v1", "v2", "all"), default="all",
                        help="which split to build (default: both)")
    parser.add_argument("--query-script", type=Path, default=DEFAULT_SCRIPT,
                        help="path to the skill's query_opportunities.py")
    args = parser.parse_args()

    wanted = SPLITS if args.split == "all" else {args.split: SPLITS[args.split]}
    written = {}
    for name, (cases, out) in wanted.items():
        text = serialize(build(args.query_script, cases))
        if args.check:
            current = out.read_text(encoding="utf-8") if out.is_file() else ""
            if current != text:
                print(f"{out}: stale - rerun build_web3_cases.py", file=sys.stderr)
                return 1
        else:
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(text, encoding="utf-8")
        written[name] = len(cases)
    print(json.dumps({"ok": True, "cases": written}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
