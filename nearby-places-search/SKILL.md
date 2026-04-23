---
name: nearby-places-search
description: |
  Real-time place search using Google Places API. Use this skill — instead of web search — whenever the user asks to find a physical place, business, or venue near a location. Trigger phrases: "find cafes near", "coffee shops near", "restaurants near", "ATMs near", "within walking distance", "nearby", "near [place/address]", "close to", "around [location]". Returns live results with addresses, ratings, and direct Maps links. Requires GOOGLE_PLACES_API_KEY. Always prefer this over firecrawl-search for any location-based place discovery query.
allowed-tools:
  - Bash(python3 *)
---

# Nearby Places Search

This skill searches for nearby places using the Google Places API (New). Requires a `GOOGLE_PLACES_API_KEY` environment variable.

## When to Use

Use this skill — **not web search** — whenever the user asks to find a physical place near a location. This skill works for **any location worldwide** (e.g., "Hilton Saigon", "London", "Times Square") — it geocodes addresses and landmark names automatically.

## Usage

Run the script with positional arguments:

```bash
python3 "$SKILL_DIR/scripts/search_places.py" "<query>" "<location>" [--radius_meters <int>]
```

### Parameters

- `query`: Type of place to search for (e.g., "coffee shop", "restaurant", "ATM")
- `location`: Address or place name (e.g., "London", "Times Square")
- `--radius_meters` (optional): Search radius in meters. Default: 1000

### Examples

```bash
python3 "$SKILL_DIR/scripts/search_places.py" "coffee shop" "London"
python3 "$SKILL_DIR/scripts/search_places.py" "restaurant" "Times Square" --radius_meters 500
```

### Output

JSON object with a `data.results` array. Each result contains `response.data.places`, a list of places with `displayName.text`, `formattedAddress`, `googleMapsUrl`, and optionally `rating` and `priceLevel`.

## Response Format

After running the script, present results **exactly once** as a concise numbered list:

```
Here are [type] near [location]:
1. **Name** — Address (price) ⭐ rating — [Maps](googleMapsUrl)
2. **Name** — Address (price) ⭐ rating — [Maps](googleMapsUrl)
```

- Price levels: PRICE_LEVEL_INEXPENSIVE = $, PRICE_LEVEL_MODERATE = $$, PRICE_LEVEL_EXPENSIVE = $$$, PRICE_LEVEL_VERY_EXPENSIVE = $$$$. Omit if not present.
- Omit rating if not present.
- **Always include the Google Maps link** — every place has a `googleMapsUrl` field.

Do not repeat the list or add a second summary paragraph after it.

## Prerequisites

`GOOGLE_PLACES_API_KEY` must be set as an environment variable.
