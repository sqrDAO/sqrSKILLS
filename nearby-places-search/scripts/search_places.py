#!/usr/bin/env python3
"""
Nearby places search using Google Places API (New).
Requires GOOGLE_PLACES_API_KEY environment variable (or workspace .google-places.env file).
"""

import argparse
import json
import os
import re
import sys
import urllib.parse
import urllib.request

PLACES_NEARBY_URL = "https://places.googleapis.com/v1/places:searchNearby"
PLACES_TEXT_URL   = "https://places.googleapis.com/v1/places:searchText"

WORKSPACE_DIR = (
    os.environ.get("OPENCLAW_WORKSPACE_DIR")
    or os.environ.get("NANOBOT_WORKSPACE", os.path.expanduser("~/.nanobot/workspace"))
)

# Load API key from env, falling back to workspace .google-places.env file
GOOGLE_PLACES_API_KEY = os.environ.get("GOOGLE_PLACES_API_KEY", "")
if not GOOGLE_PLACES_API_KEY:
    dotenv_path = os.path.join(WORKSPACE_DIR, ".google-places.env")
    if os.path.isfile(dotenv_path):
        for line in open(dotenv_path):
            if line.startswith("GOOGLE_PLACES_API_KEY="):
                GOOGLE_PLACES_API_KEY = line.split("=", 1)[1].strip()
                break

# Maps common query terms to Google Places primary types
GOOGLE_PLACES_TYPE_MAP = {
    "food": "restaurant",
    "food place": "restaurant",
    "restaurant": "restaurant",
    "cafe": "cafe",
    "coffee": "cafe",
    "coffee shop": "cafe",
    "fast food": "fast_food_restaurant",
    "bar": "bar",
    "pub": "bar",
    "bakery": "bakery",
    "pizza": "pizza_restaurant",
    "sushi": "japanese_restaurant",
    "atm": "atm",
    "bank": "bank",
    "pharmacy": "pharmacy",
    "chemist": "pharmacy",
    "hospital": "hospital",
    "clinic": "doctor",
    "doctor": "doctor",
    "hotel": "lodging",
    "hostel": "lodging",
    "gym": "gym",
    "fitness": "gym",
    "park": "park",
    "museum": "museum",
    "cinema": "movie_theater",
    "theatre": "performing_arts_theater",
    "supermarket": "supermarket",
    "grocery": "grocery_store",
    "parking": "parking",
    "gas station": "gas_station",
    "fuel": "gas_station",
    "petrol": "gas_station",
    "school": "school",
    "library": "library",
    "dentist": "dentist",
    "laundry": "laundry",
}


# ---------------------------------------------------------------------------
# Memory fallback helpers (unchanged from previous version)
# ---------------------------------------------------------------------------

def lookup_coords_in_memory(location):
    """
    Search MEMORY.md and memory/*.md for coordinates stored alongside a known location.
    Looks for lines like 'Coordinates: 16.123, 108.456' in a relevant section.
    Returns (lat, lon) directly without needing a geocoding API call.
    """
    candidates = []
    memory_md = os.path.join(WORKSPACE_DIR, "MEMORY.md")
    if os.path.isfile(memory_md):
        candidates.append(memory_md)
    memory_dir = os.path.join(WORKSPACE_DIR, "memory")
    if os.path.isdir(memory_dir):
        for fname in os.listdir(memory_dir):
            candidates.append(os.path.join(memory_dir, fname))

    search_words = [w.lower() for w in re.split(r"\W+", location) if len(w) > 2]
    coords_pattern = re.compile(
        r"[Cc]oordinates[:\s]+(-?\d+\.\d+)[,\s]+(-?\d+\.\d+)"
    )

    for fpath in candidates:
        try:
            text = open(fpath).read()
        except OSError:
            continue
        if not any(w in text.lower() for w in search_words):
            continue
        match = coords_pattern.search(text)
        if match:
            lat, lon = float(match.group(1)), float(match.group(2))
            print(f"Memory fallback: found coordinates in {os.path.basename(fpath)}: {lat}, {lon}", file=sys.stderr)
            return lat, lon

    return None


# ---------------------------------------------------------------------------
# Geocoding via Google Places Text Search
# ---------------------------------------------------------------------------

def _places_request(url, body, field_mask):
    """POST a JSON request to a Google Places API endpoint."""
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "X-Goog-Api-Key": GOOGLE_PLACES_API_KEY,
            "X-Goog-FieldMask": field_mask,
        },
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


def _geocode_via_places(location):
    """Use Places Text Search to resolve a location string to (lat, lon)."""
    try:
        result = _places_request(
            PLACES_TEXT_URL,
            {"textQuery": location, "pageSize": 1},
            "places.location",
        )
        places = result.get("places", [])
        if places:
            loc = places[0].get("location", {})
            lat = loc.get("latitude")
            lon = loc.get("longitude")
            if lat is not None and lon is not None:
                print(f"Geocoded via Google Places: {lat}, {lon}", file=sys.stderr)
                return float(lat), float(lon)
    except Exception as e:
        print(f"Google Places geocoding error: {e}", file=sys.stderr)
    return None


def geocode_location(location):
    """Convert a location string to (lat, lon)."""
    print(f"Geocoding '{location}'...", file=sys.stderr)

    # 1. Direct coordinates stored in memory (no API call)
    coords = lookup_coords_in_memory(location)
    if coords:
        return coords

    # 2. Google Places Text Search
    print("Checking Google Places for location...", file=sys.stderr)
    return _geocode_via_places(location)


# ---------------------------------------------------------------------------
# Place type resolution
# ---------------------------------------------------------------------------

def get_place_type(query):
    """Return a Google Places primary type for the query string."""
    q = query.lower().strip()
    if q in GOOGLE_PLACES_TYPE_MAP:
        return GOOGLE_PLACES_TYPE_MAP[q]
    # Partial / substring match — longest wins
    best = None
    for term, ptype in GOOGLE_PLACES_TYPE_MAP.items():
        if term in q and (best is None or len(term) > len(best[0])):
            best = (term, ptype)
    if best:
        return best[1]
    # Default: pass the query as-is (Google Places accepts many type strings)
    return q.replace(" ", "_")


# ---------------------------------------------------------------------------
# Nearby search
# ---------------------------------------------------------------------------

def _haversine_meters(lat1, lon1, lat2, lon2):
    """Return the great-circle distance in metres between two coordinates."""
    import math
    R = 6_371_000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _rank_places(raw_places, center_lat, center_lon, top_n=10):
    """
    Re-rank raw API places by a blended score (50% proximity, 50% rating)
    and return the top_n results, each annotated with distance_meters.
    Places with no rating are treated as rating=0.
    """
    annotated = []
    for p in raw_places:
        loc = p.get("location", {})
        plat = loc.get("latitude", center_lat)
        plon = loc.get("longitude", center_lon)
        dist = _haversine_meters(center_lat, center_lon, plat, plon)
        rating = p.get("rating", 0) or 0
        annotated.append((dist, rating, p))

    if not annotated:
        return []

    max_dist = max(d for d, _, _ in annotated) or 1
    max_rating = max(r for _, r, _ in annotated) or 1

    scored = []
    for dist, rating, p in annotated:
        proximity_score = 1 - (dist / max_dist)
        rating_score = rating / max_rating
        score = 0.5 * proximity_score + 0.5 * rating_score
        scored.append((score, dist, p))

    scored.sort(key=lambda x: x[0], reverse=True)

    result = []
    for _, dist, p in scored[:top_n]:
        p = dict(p)
        p["_distance_meters"] = round(dist)
        result.append(p)
    return result


def _google_nearby_search(lat, lon, place_type, radius_meters, limit=20):
    """Call Google Places Nearby Search and return raw place dicts."""
    body = {
        "locationRestriction": {
            "circle": {
                "center": {"latitude": lat, "longitude": lon},
                "radius": float(radius_meters),
            }
        },
        "includedTypes": [place_type],
        "maxResultCount": limit,
        "rankPreference": "DISTANCE",
    }
    field_mask = ",".join([
        "places.displayName",
        "places.formattedAddress",
        "places.location",
        "places.googleMapsUri",
        "places.rating",
        "places.priceLevel",
        "places.businessStatus",
    ])
    try:
        result = _places_request(PLACES_NEARBY_URL, body, field_mask)
        return result.get("places", [])
    except Exception as e:
        print(f"Google Places nearby search error: {e}", file=sys.stderr)
        return []


def place_to_dict(place):
    """Normalise a Google Places API place object into the output schema."""
    name = place.get("displayName", {}).get("text", "Unknown")
    loc = place.get("location", {})
    lat = loc.get("latitude", 0)
    lon = loc.get("longitude", 0)
    address = place.get("formattedAddress", "")
    maps_url = place.get("googleMapsUri", "")

    result = {
        "displayName": {"text": name},
        "formattedAddress": address,
        "googleMapsUrl": maps_url,
        "location": {"lat": lat, "lng": lon},
    }
    if "rating" in place:
        result["rating"] = place["rating"]
    if "priceLevel" in place:
        result["priceLevel"] = place["priceLevel"]
    if "_distance_meters" in place:
        result["distance_meters"] = place["_distance_meters"]
    return result


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def search_nearby_places(query, location, radius_meters=1000):
    if not GOOGLE_PLACES_API_KEY:
        return {"error": "GOOGLE_PLACES_API_KEY is not set. Add it to the container environment or to workspace/.google-places.env"}

    coords = geocode_location(location)
    if not coords:
        return {"error": f"Could not geocode location: {location}"}

    lat, lon = coords
    print(f"Coordinates: {lat}, {lon}", file=sys.stderr)

    place_type = get_place_type(query)
    print(f"Google Places type: {place_type}", file=sys.stderr)

    raw_places = _google_nearby_search(lat, lon, place_type, radius_meters)

    if not raw_places:
        print(f"No results at {radius_meters}m, widening to {radius_meters * 3}m...", file=sys.stderr)
        raw_places = _google_nearby_search(lat, lon, place_type, radius_meters * 3)

    ranked = _rank_places(raw_places, lat, lon, top_n=10)
    places = [place_to_dict(p) for p in ranked]

    return {
        "successful": True,
        "data": {
            "results": [
                {
                    "response": {
                        "successful": True,
                        "data": {"places": places},
                    },
                    "tool_slug": "NEARBY_PLACES_SEARCH",
                    "index": 0,
                }
            ],
            "total_count": len(places),
            "success_count": len(places),
            "error_count": 0,
        },
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Search for nearby places using Google Places API."
    )
    parser.add_argument("query", help="Type of place (e.g., 'coffee shop', 'restaurant').")
    parser.add_argument("location", help="Address or place name (e.g., 'London', 'Da Nang Blockchain Hub').")
    parser.add_argument("--radius_meters", type=int, default=1000,
                        help="Search radius in metres (default: 1000).")
    args = parser.parse_args()
    result = search_nearby_places(args.query, args.location, args.radius_meters)
    print(json.dumps(result, indent=2))
