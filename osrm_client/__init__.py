import json
import urllib.error
import urllib.request


class OSRMError(Exception):
    pass


def get_driving_distances(
    base_url: str, origin_lat: float, origin_lon: float, destinations: list[tuple[float, float]]
) -> list[tuple[float, int] | None]:
    """Real driving (distance_m, duration_minutes) from one origin to each of the given
    destinations, via a single OSRM /table request against a self-hosted instance at
    base_url (no trailing slash) - sources=0 pins the first coordinate as the only
    source, every other coordinate is a destination. One entry per destination, in
    order; None where OSRM found no route - same shape as a Google Routes API
    computeRouteMatrix client, so callers can swap providers without caring which one
    answered.

    base_url is passed in rather than read from a settings object here, since this
    package has no opinion on how a given app configures itself - each caller (e.g.
    TGSRTCEngine, MetroEngine) resolves its own OSRM_BASE_URL and passes it through."""
    if not base_url:
        raise OSRMError("No OSRM base_url configured")
    if not destinations:
        return []

    coords = ";".join(f"{lon},{lat}" for lat, lon in [(origin_lat, origin_lon)] + destinations)
    url = f"{base_url}/table/v1/driving/{coords}?sources=0&annotations=distance,duration"

    req = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            parsed = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        raise OSRMError(f"OSRM error ({e.code}): {e.read().decode(errors='replace')[:300]}") from None
    except Exception as e:
        raise OSRMError(f"OSRM request failed: {e}") from None

    if parsed.get("code") != "Ok":
        raise OSRMError(f"OSRM error: {parsed.get('code')} - {parsed.get('message', '')}")

    # Row 0 (the only source) has one entry per coordinate passed, including the origin
    # itself at index 0 (self-distance 0) - drop that to line up 1:1 with destinations.
    distances = parsed["distances"][0][1:]
    durations = parsed["durations"][0][1:]

    results: list[tuple[float, int] | None] = []
    for distance_m, duration_s in zip(distances, durations):
        if distance_m is None or duration_s is None:
            results.append(None)
        else:
            results.append((float(distance_m), round(duration_s / 60)))
    return results
