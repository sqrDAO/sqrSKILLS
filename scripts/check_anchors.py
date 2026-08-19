#!/usr/bin/env python3
"""Check that every source anchor cited by the skills still resolves.

The skills state legal, visa, and funding facts on the authority of a cited
URL. A citation that 404s is not a weak citation, it is no citation: the claim
becomes unverifiable and, going by past refreshes, quietly wrong. This command
fetches every anchor and reports the dead ones.

An anchor is dead only on a definitive answer: HTTP 404/410, or a hostname with
no DNS record at all. Those fail the run. A host that is alive but refuses us
(401/403/429, common behind Cloudflare) and genuine flakiness (5xx, timeouts,
resets) are reported as unverified but do not fail, so a bot-hostile host or an
offline runner cannot block a refresh. Use --strict to fail on those too.

The command prints one JSON result to stdout. Human-readable diagnostics are
written to stderr so CI and other agents can consume the result reliably.
"""

from __future__ import annotations

import argparse
import json
import re
import socket
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

# Anchors are written as `https://...` inside the markdown references.
MARKDOWN_URL = re.compile(r"`(https?://[^`\s]+)`")

# A stock urllib User-Agent is refused by several Vietnamese government portals.
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

TARGETS = ("baseline", "visa", "web3")


def collect_markdown(path: Path) -> list[tuple[str, str]]:
    if not path.is_file():
        return []
    text = path.read_text(encoding="utf-8")
    return [(url, str(path)) for url in dict.fromkeys(MARKDOWN_URL.findall(text))]


def collect_visa(path: Path) -> list[tuple[str, str]]:
    if not path.is_file():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    meta = data.get("_meta", {})
    urls: list[str] = [
        url for url in meta.get("sources", []) if isinstance(url, str) and url.startswith("http")
    ]
    registry = meta.get("source_registry", {})
    if isinstance(registry, dict):
        for entry in registry.values():
            if isinstance(entry, dict) and isinstance(entry.get("url"), str):
                urls.append(entry["url"])
    return [(url, str(path)) for url in dict.fromkeys(urls)]


def collect_web3(path: Path) -> list[tuple[str, str]]:
    if not path.is_file():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    urls = [
        entry["url"]
        for entry in data.get("opportunities", [])
        if isinstance(entry, dict) and isinstance(entry.get("url"), str)
    ]
    return [(url, str(path)) for url in dict.fromkeys(urls)]


def collect(root: Path, targets: tuple[str, ...]) -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []
    if "baseline" in targets:
        references = root / "vietnam-crypto-radar" / "references"
        found += collect_markdown(references / "baseline.md")
        found += collect_markdown(references / "sources.md")
    if "visa" in targets:
        found += collect_visa(root / "vietnam-visa-check" / "data" / "vietnam_immigration_policy.json")
    if "web3" in targets:
        found += collect_web3(root / "web3-opportunities" / "data" / "web3_opportunities.json")

    seen: set[str] = set()
    unique: list[tuple[str, str]] = []
    for url, origin in found:
        if url not in seen:
            seen.add(url)
            unique.append((url, origin))
    return unique


# A document that is gone says so. Everything else 4xx means the host is alive
# and declining to serve us, which is not evidence about the document.
DEFINITIVELY_GONE = (404, 410)


def hostname_resolves(url: str) -> bool:
    host = urllib.parse.urlsplit(url).hostname
    if not host:
        return False
    try:
        socket.getaddrinfo(host, None)
    except socket.gaierror:
        return False
    except OSError:
        return True  # some other transport problem; not a naming answer
    return True


def classify(url: str, timeout: float, attempts: int) -> tuple[str, object]:
    """Return (verdict, status) where verdict is ok, dead, or unverified."""
    # Some of these hosts present incomplete certificate chains; we are checking
    # that a document still exists, not establishing a secure channel.
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})

    status: object = "unknown"
    for attempt in range(attempts):
        try:
            with urllib.request.urlopen(request, timeout=timeout, context=context) as response:
                return "ok", response.status
        except urllib.error.HTTPError as exc:
            status = exc.code
            if exc.code in DEFINITIVELY_GONE:
                return "dead", exc.code
            # 401/403/429 and 5xx: the host answered, but not about the document.
        except Exception as exc:  # noqa: BLE001 - any transport failure
            status = type(exc).__name__
        if attempt + 1 < attempts:
            continue

    # A hostname that no longer exists is as definitive as a 404, and is how
    # link rot usually presents once a project's domain lapses.
    if not hostname_resolves(url):
        return "dead", "NXDOMAIN"
    return "unverified", status


def main() -> int:
    parser = argparse.ArgumentParser(description="Check skill source anchors resolve")
    parser.add_argument(
        "--targets",
        default=",".join(TARGETS),
        help=f"comma-separated subset of {','.join(TARGETS)} (default: all)",
    )
    parser.add_argument("--timeout", type=float, default=25.0, help="per-request timeout seconds")
    parser.add_argument("--attempts", type=int, default=2, help="attempts before calling it transient")
    parser.add_argument(
        "--strict", action="store_true", help="also fail on unverified anchors"
    )
    args = parser.parse_args()

    targets = tuple(t.strip() for t in args.targets.split(",") if t.strip())
    unknown = [t for t in targets if t not in TARGETS]
    if unknown:
        parser.error(f"unknown target(s): {', '.join(unknown)}")

    root = Path(__file__).resolve().parent.parent
    anchors = collect(root, targets)

    dead: list[dict[str, object]] = []
    unverified: list[dict[str, object]] = []
    for url, origin in anchors:
        verdict, status = classify(url, args.timeout, args.attempts)
        record = {"url": url, "status": status, "source": origin}
        if verdict == "dead":
            dead.append(record)
            print(f"DEAD {status} {url}  ({origin})", file=sys.stderr)
        elif verdict == "unverified":
            unverified.append(record)
            print(f"WARN {status} {url}  ({origin})", file=sys.stderr)

    ok = not dead and (not unverified or not args.strict)
    print(
        json.dumps(
            {
                "ok": ok,
                "counts": {
                    "checked": len(anchors),
                    "resolved": len(anchors) - len(dead) - len(unverified),
                    "dead": len(dead),
                    "unverified": len(unverified),
                },
                "dead": dead,
                "unverified": unverified,
            },
            indent=2,
        )
    )
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
