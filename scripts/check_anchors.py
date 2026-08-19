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
import ipaddress
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


def is_web_url(value: object) -> bool:
    """Only http(s) values are anchors. urlopen also speaks file:, so filter here."""
    return isinstance(value, str) and urllib.parse.urlsplit(value).scheme in ALLOWED_SCHEMES


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
    urls: list[str] = [url for url in meta.get("sources", []) if is_web_url(url)]
    registry = meta.get("source_registry", {})
    if isinstance(registry, dict):
        for entry in registry.values():
            if isinstance(entry, dict) and is_web_url(entry.get("url")):
                urls.append(entry["url"])
    return [(url, str(path)) for url in dict.fromkeys(urls)]


def collect_web3(path: Path) -> list[tuple[str, str]]:
    if not path.is_file():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    urls = [
        entry["url"]
        for entry in data.get("opportunities", [])
        if isinstance(entry, dict) and is_web_url(entry.get("url"))
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

ALLOWED_SCHEMES = ("http", "https")


class UnsafeTarget(Exception):
    """A URL we decline to fetch, with the reason as its message."""


def resolved_addresses(host: str) -> list[str]:
    return [info[4][0] for info in socket.getaddrinfo(host, None)]


def check_target(url: str) -> None:
    """Raise UnsafeTarget unless this is a public http(s) URL we may fetch.

    The URLs come from data files an unattended agent writes from web pages it
    fetched, so they are not trusted input. Two things matter: urlopen speaks
    more than http (a `file:` URL would happily read the CI filesystem), and a
    checker that follows arbitrary hosts is a way to probe whatever the runner
    can reach.
    """
    parts = urllib.parse.urlsplit(url)
    if parts.scheme not in ALLOWED_SCHEMES:
        raise UnsafeTarget(f"unsupported-scheme:{parts.scheme or 'none'}")
    if not parts.hostname:
        raise UnsafeTarget("no-host")
    try:
        addresses = resolved_addresses(parts.hostname)
    except socket.gaierror:
        raise UnsafeTarget("NXDOMAIN") from None
    except OSError:
        return  # transport trouble, not a naming answer; let the fetch decide
    for address in addresses:
        ip = ipaddress.ip_address(address)
        if ip.is_loopback or ip.is_private or ip.is_link_local or ip.is_reserved:
            raise UnsafeTarget(f"non-public-address:{address}")


class ValidatingRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Apply the same rules to redirect targets as to the original URL."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: D102
        check_target(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def build_opener() -> urllib.request.OpenerDirector:
    return urllib.request.build_opener(ValidatingRedirectHandler)


def hostname_resolves(url: str) -> bool:
    host = urllib.parse.urlsplit(url).hostname
    if not host:
        return False
    try:
        resolved_addresses(host)
    except socket.gaierror:
        return False
    except OSError:
        return True  # some other transport problem; not a naming answer
    return True


def classify(url: str, timeout: float, attempts: int) -> tuple[str, object]:
    """Return (verdict, status) where verdict is ok, dead, or unverified."""
    try:
        check_target(url)
    except UnsafeTarget as exc:
        # A citation we may not fetch is not a working citation. NXDOMAIN is the
        # ordinary shape of link rot; the rest means the data file is wrong.
        return "dead", str(exc)

    # TLS verification stays on. An anchor we could not validate is reported as
    # unverified rather than ok, so a broken or intercepted chain never passes
    # for a live citation -- but it does not fail the run either, since that is
    # a transport problem and not evidence the document is gone.
    opener = build_opener()
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})

    status: object = "unknown"
    for attempt in range(attempts):
        try:
            with opener.open(request, timeout=timeout) as response:
                return "ok", response.status
        except urllib.error.HTTPError as exc:
            status = exc.code
            if exc.code in DEFINITIVELY_GONE:
                return "dead", exc.code
            # 401/403/429 and 5xx: the host answered, but not about the document.
        except UnsafeTarget as exc:
            return "dead", f"redirect-to-{exc}"
        except urllib.error.URLError as exc:
            reason = exc.reason
            status = (
                f"TLS:{type(reason).__name__}"
                if isinstance(reason, ssl.SSLError)
                else type(reason).__name__
            )
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
