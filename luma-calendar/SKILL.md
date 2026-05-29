---
name: luma-calendar
description: |
  Manage Luma events and guests via the Luma public API. Use this skill whenever
  the user asks to list, create, or view Luma events; check who registered for an
  event; add a guest or attendee to a Luma event; or get calendar information.
  Trigger phrases: "list my Luma events", "create a Luma event", "who registered
  for my event", "add guest to Luma", "get my Luma calendar", "show Luma attendees",
  "how many people signed up for", "invite someone to my Luma event".
  Requires LUMA_API_KEY environment variable.
allowed-tools:
  - Bash(python3 *)
---

# Luma Calendar

Manage Luma events and guests using the [Luma public API](https://docs.luma.com/reference). Requires a `LUMA_API_KEY` environment variable — get yours from your Luma calendar settings.

## When to Use

Use this skill whenever the user wants to:
- View their Luma calendar or upcoming events
- Create a new Luma event
- Check who has registered for an event
- Add guests to an event
- Look up details of a specific event

## Usage

```bash
python3 "$SKILL_DIR/scripts/luma_calendar.py" <subcommand> [options]
```

### Subcommands

| Subcommand | Description |
|---|---|
| `get-self` | Verify credentials and get authenticated user profile |
| `get-calendar` | Get calendar details (name, slug, description) |
| `list-events` | List events on the calendar |
| `get-event` | Get full details of a specific event |
| `create-event` | Create a new event |
| `get-guests` | List registered guests for an event |
| `add-guests` | Add one or more guests to an event |

### Examples

```bash
# Verify your API key
python3 "$SKILL_DIR/scripts/luma_calendar.py" get-self

# List upcoming events
python3 "$SKILL_DIR/scripts/luma_calendar.py" list-events

# List events after a specific date
python3 "$SKILL_DIR/scripts/luma_calendar.py" list-events --after 2026-06-01T00:00:00Z

# Get details for a specific event
python3 "$SKILL_DIR/scripts/luma_calendar.py" get-event --api-id evt-abc123

# Create an event
python3 "$SKILL_DIR/scripts/luma_calendar.py" create-event \
  --name "Builder Night Hanoi" \
  --start-at "2026-07-10T18:00:00Z" \
  --end-at "2026-07-10T21:00:00Z" \
  --timezone "Asia/Ho_Chi_Minh" \
  --description "Monthly builder meetup in Hanoi."

# List guests for an event
python3 "$SKILL_DIR/scripts/luma_calendar.py" get-guests --event-api-id evt-abc123

# Add guests to an event
python3 "$SKILL_DIR/scripts/luma_calendar.py" add-guests \
  --event-api-id evt-abc123 \
  --guests '[{"email":"alice@example.com","name":"Alice"},{"email":"bob@example.com","name":"Bob"}]'
```

### Parameters: `list-events`

| Flag | Description |
|---|---|
| `--after` | ISO 8601 datetime — only return events starting after this time |
| `--before` | ISO 8601 datetime — only return events starting before this time |
| `--pagination-cursor` | Cursor string from a previous response for the next page |

### Parameters: `create-event`

| Flag | Required | Description |
|---|---|---|
| `--name` | Yes | Event name |
| `--start-at` | No | Start time (ISO 8601, e.g. `2026-06-01T10:00:00Z`) |
| `--end-at` | No | End time (ISO 8601) |
| `--timezone` | No | Timezone name (e.g. `Asia/Ho_Chi_Minh`, `America/New_York`) |
| `--description` | No | Event description (plain text or HTML) |
| `--geo-address-json` | No | Venue address as a JSON object, e.g. `{"city":"Hanoi","country":"VN","full_address":"123 Main St"}` |
| `--url` | No | Custom URL slug for the event page |

### Parameters: `get-guests` / `add-guests`

| Flag | Required | Description |
|---|---|---|
| `--event-api-id` | Yes | The event's API ID (e.g. `evt-abc123`) |
| `--guests` | Yes (`add-guests` only) | JSON array of `{"email":"...","name":"..."}` objects |
| `--pagination-cursor` | No | Cursor for next page of results (`get-guests` only) |

## Output

All subcommands print a JSON object to stdout. Key fields:

- `get-calendar` / `get-event`: returns the object directly with fields like `api_id`, `name`, `start_at`, `url`
- `list-events`: returns `{"entries": [...], "has_more": bool, "next_cursor": "..."}`
- `get-guests`: returns `{"entries": [...], "has_more": bool, "next_cursor": "..."}`
- `add-guests` / `create-event`: returns the created/updated resource

On error, prints the API error JSON and exits with code 1.

## Prerequisites

`LUMA_API_KEY` must be set as an environment variable. API keys are scoped to a single calendar — get yours from your Luma calendar's API settings page.
