"""Thin client for the aviationweather.gov data API."""

import requests

API_BASE = "https://aviationweather.gov/api/data"
TIMEOUT = 10

_session = requests.Session()


class AviationAPIError(Exception):
    """A problem to show the user as a friendly message."""


class StationNotFound(AviationAPIError):
    """The service has no current report for this code."""


def _get_json(endpoint, ids):
    try:
        response = _session.get(
            f"{API_BASE}/{endpoint}",
            params={"ids": ids, "format": "json"},
            timeout=TIMEOUT,
        )
        response.raise_for_status()
    except requests.Timeout:
        raise AviationAPIError("The weather service took too long to respond. Please try again.")
    except requests.RequestException:
        raise AviationAPIError("Couldn't reach the weather service. Please try again later.")

    # An unknown station comes back as an empty body, not as JSON.
    if not response.text.strip():
        return []
    try:
        return response.json()
    except ValueError:
        raise AviationAPIError("The weather service sent an unexpected response.")


def fetch_metars(codes):
    """Latest METAR (as decoded JSON) for each code, keyed by ICAO id."""
    data = _get_json("metar", ",".join(codes))
    latest = {}
    for item in data:
        code = item.get("icaoId")
        # The API returns newest first; keep only the first report per station.
        if code and code not in latest:
            latest[code] = item
    return latest


def fetch_metar(code):
    metar = fetch_metars([code]).get(code)
    if not metar:
        raise StationNotFound(f"No METAR report found for {code}. Check the airport code.")
    return metar


def fetch_airport(code):
    """Airport details (IATA id, runways). None if unavailable, since it's optional."""
    try:
        data = _get_json("airport", code)
    except AviationAPIError:
        return None
    return data[0] if data else None
