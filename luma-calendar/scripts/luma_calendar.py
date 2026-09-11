#!/usr/bin/env python3
"""
Luma calendar management via the Luma public API.
Requires LUMA_API_KEY environment variable.
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

BASE_URL = "https://public-api.luma.com"


def get_api_key():
    key = os.environ.get("LUMA_API_KEY", "").strip()
    if not key:
        print(json.dumps({"ok": False, "error": "LUMA_API_KEY environment variable is not set"}))
        sys.exit(1)
    return key


def api_get(path, params=None):
    key = get_api_key()
    url = BASE_URL + path
    if params:
        url += "?" + urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
    req = urllib.request.Request(url, headers={"x-luma-api-key": key})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError) as e:
        if isinstance(e, urllib.error.HTTPError):
            body = e.read().decode(errors="replace")
            try:
                err = json.loads(body)
            except Exception:
                err = {"error": body or str(e)}
        else:
            err = {"error": str(e)}
        print(json.dumps({"ok": False, "error": err}, ensure_ascii=False))
        sys.exit(1)


def api_post(path, body):
    key = get_api_key()
    url = BASE_URL + path
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        url,
        data=data,
        headers={"x-luma-api-key": key, "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError) as e:
        if isinstance(e, urllib.error.HTTPError):
            err_body = e.read().decode(errors="replace")
            try:
                err = json.loads(err_body)
            except Exception:
                err = {"error": err_body or str(e)}
        else:
            err = {"error": str(e)}
        print(json.dumps({"ok": False, "error": err}, ensure_ascii=False))
        sys.exit(1)


def cmd_get_self(args):
    result = api_get("/v1/users/get-self")
    print(json.dumps(result, indent=2))


def cmd_get_calendar(args):
    result = api_get("/v1/calendars/get")
    print(json.dumps(result, indent=2))


def cmd_list_events(args):
    params = {}
    if args.after:
        params["after"] = args.after
    if args.before:
        params["before"] = args.before
    if args.pagination_cursor:
        params["pagination_cursor"] = args.pagination_cursor
    result = api_get("/v1/calendars/events/list", params or None)
    print(json.dumps(result, indent=2))


def cmd_get_event(args):
    result = api_get("/v1/events/get", {"event_id": args.api_id})
    print(json.dumps(result, indent=2))


def cmd_create_event(args):
    body = {"name": args.name, "start_at": args.start_at, "timezone": args.timezone}
    if args.end_at:
        body["end_at"] = args.end_at
    if args.description:
        body["description_md"] = args.description
    if args.geo_address_json:
        try:
            body["geo_address_json"] = json.loads(args.geo_address_json)
        except json.JSONDecodeError as e:
            print(f"Error: --geo-address-json is not valid JSON: {e}", file=sys.stderr)
            sys.exit(1)
    if args.url:
        body["slug"] = args.url
    result = api_post("/v1/events/create", body)
    print(json.dumps(result, indent=2))


def cmd_get_guests(args):
    params = {"event_id": args.event_api_id}
    if args.pagination_cursor:
        params["pagination_cursor"] = args.pagination_cursor
    result = api_get("/v1/events/guests/list", params)
    print(json.dumps(result, indent=2))


def cmd_add_guests(args):
    try:
        guests = json.loads(args.guests)
    except json.JSONDecodeError as e:
        print(f"Error: --guests is not valid JSON: {e}", file=sys.stderr)
        sys.exit(1)
    body = {"event_id": args.event_api_id, "guests": guests}
    result = api_post("/v1/events/guests/add", body)
    print(json.dumps(result, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Luma calendar API client")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("get-self", help="Get authenticated user profile")
    sub.add_parser("get-calendar", help="Get calendar details")

    p = sub.add_parser("list-events", help="List events on the calendar")
    p.add_argument("--after", help="ISO 8601 datetime — return events starting after this time")
    p.add_argument("--before", help="ISO 8601 datetime — return events starting before this time")
    p.add_argument("--pagination-cursor", help="Cursor for next page of results")

    p = sub.add_parser("get-event", help="Get event details by API ID")
    p.add_argument("--api-id", required=True, help="Event API ID (e.g. evt-abc123)")

    p = sub.add_parser("create-event", help="Create a new event")
    p.add_argument("--name", required=True, help="Event name")
    p.add_argument("--start-at", required=True, help="Start time (ISO 8601, e.g. 2026-06-01T10:00:00Z)")
    p.add_argument("--end-at", help="End time (ISO 8601)")
    p.add_argument("--timezone", required=True, help="IANA timezone (e.g. Asia/Ho_Chi_Minh, America/New_York)")
    p.add_argument("--description", help="Event description (plain text or HTML)")
    p.add_argument(
        "--geo-address-json",
        help='Venue address as JSON object, e.g. \'{"type":"manual","address":"123 Main St, Hanoi, VN"}\'',
    )
    p.add_argument("--url", help="Custom URL slug for the event page")

    p = sub.add_parser("get-guests", help="List registered guests for an event")
    p.add_argument("--event-api-id", required=True, help="Event API ID")
    p.add_argument("--pagination-cursor", help="Cursor for next page")

    p = sub.add_parser("add-guests", help="Add guests to an event")
    p.add_argument("--event-api-id", required=True, help="Event API ID")
    p.add_argument(
        "--guests",
        required=True,
        help='JSON array of guest objects, e.g. \'[{"email":"alice@example.com","name":"Alice"}]\'',
    )

    args = parser.parse_args()

    dispatch = {
        "get-self": cmd_get_self,
        "get-calendar": cmd_get_calendar,
        "list-events": cmd_list_events,
        "get-event": cmd_get_event,
        "create-event": cmd_create_event,
        "get-guests": cmd_get_guests,
        "add-guests": cmd_add_guests,
    }
    dispatch[args.command](args)


if __name__ == "__main__":
    main()
