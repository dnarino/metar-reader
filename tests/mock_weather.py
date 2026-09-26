"""Mock aviationweather.gov for tests.

SCENARIOS is a catalog of fake METAR readings, each with the results the app should show.
To test a new weather situation, add an entry here. The parametrized tests in test_app.py
pick it up automatically.

FakeAviationWeather replaces the HTTP session in aviation_api, so tests run the real code
path (route -> API client -> decoder -> briefing -> template) with no internet access.
"""

import json

import requests

OBS_TIME = 1790427180  # 2026-09-26 18:53 UTC


def metar(raw, **fields):
    """A METAR in the shape the API returns (format=json). Fields left out are absent, like the real API."""
    code = raw.split()[1] if raw.split()[0] in ("METAR", "SPECI") else raw.split()[0]
    return {"icaoId": code, "rawOb": raw, "metarType": raw.split()[0], **fields}


def airport(code, iata=None, runways=()):
    return {"icaoId": code, "iataId": iata, "runways": list(runways)}


def runway(ident, alignment, length=8000, surface="A"):
    return {"id": ident, "alignment": alignment, "dimension": f"{length}x150", "surface": surface}


# Each scenario: the mock API data, plus what the station page must show.
#   category  - flight category badge
#   summary   - the plain-English headline sentence (exact)
#   shows     - other text that must appear on the page
SCENARIOS = {
    "KAAA": {
        "about": "Clear, calm, warm day",
        "metar": metar(
            "METAR KAAA 261853Z 00000KT 10SM CLR 21/12 A2992 RMK AO2",
            name="Alpha Field, OR, US", obsTime=OBS_TIME, lat=45.0, lon=-122.5, elev=60,
            temp=21, dewp=12, wdir=0, wspd=0, visib="10+", altim=1013.2,
            cover="CLR", clouds=[{"cover": "CLR"}], fltCat="VFR",
        ),
        "airport": airport("KAAA", "AAA", [runway("09/27", 90)]),
        "category": "VFR",
        "summary": "Clear skies, 70°F, calm winds.",
        "shows": ["Alpha Field", "OR, US", "AAA · IATA", "No ceiling", "Unrestricted",
                  "70°F / 54°F", "Calm", "CALM", "Automated observation with precipitation sensor (AO2)"],
    },
    "KFOG": {
        "about": "Dense fog, sky obscured (LIFR)",
        "metar": metar(
            "SPECI KFOG 261347Z 00000KT 1/4SM FG VV001 06/05 A3019 RMK AO2",
            name="Foggy Bottom Arpt, WA, US", obsTime=OBS_TIME, elev=20,
            temp=6, dewp=5, wdir=0, wspd=0, visib=0.25, altim=1022.4,
            cover="OVX", clouds=[{"cover": "OVX", "base": 100}], fltCat="LIFR",
        ),
        "category": "LIFR",
        "summary": "Overcast with fog, 43°F, calm winds.",
        "shows": ["SPECI issued", "VV", "Ceiling at 100 ft · Fog", "VV 100' (sky obscured)",
                  "0.25", "Low visibility", "High pressure"],
    },
    "KTSM": {
        "about": "Thunderstorm, gusty crosswind (IFR)",
        "metar": metar(
            "METAR KTSM 261853Z 23025G40KT 2SM +TSRA BKN008CB 22/20 A2970 RMK AO2",
            name="Stormy Muni, TX, US", obsTime=OBS_TIME, elev=150,
            temp=22, dewp=20, wdir=230, wspd=25, wgst=40, visib=2, altim=1005.8,
            cover="BKN", clouds=[{"cover": "BKN", "base": 800}], fltCat="IFR",
        ),
        "airport": airport("KTSM", "TSM", [runway("18/36", 180)]),
        "category": "IFR",
        "summary": "Mostly cloudy with heavy thunderstorm with rain, 72°F, "
                   "wind 29 mph from the southwest, gusting to 46 mph.",
        "shows": ["G40 KT", "From 230° (Southwest)", "Ceiling at 800 ft", "Low visibility",
                  "Runway 18 ", "(18/36)", "STRONG CROSSWIND", "Headwind: 16 kts", "Xwind: 19 kts right",
                  "Gust crosswind up to 31 kts", "29.70", "1005.8 hPa", "Near standard"],
    },
    "EGXX": {
        "about": "Non-US report: metric visibility, pressure in hPa",
        "metar": metar(
            "METAR EGXX 261850Z 24012KT 9999 FEW035 15/09 Q1015",
            name="Example Intl, EN, GB", obsTime=OBS_TIME, elev=25,
            temp=15, dewp=9, wdir=240, wspd=12, visib="6+", altim=1015,
            cover="FEW", clouds=[{"cover": "FEW", "base": 3500}], fltCat="VFR",
        ),
        "category": "VFR",
        "summary": "Mostly clear, 59°F, wind 14 mph from the west-southwest.",
        "shows": ["EN, GB", "FEW", "No ceiling", "6+", "29.97", "1015.0 hPa",
                  "No runway data available for this station."],
    },
    "KVRB": {
        "about": "Light variable wind, below freezing, high pressure",
        "metar": metar(
            "METAR KVRB 261853Z VRB03KT 10SM SCT050 M02/M08 A3035",
            name="Variable Rgnl, MN, US", obsTime=OBS_TIME, elev=300,
            temp=-2, dewp=-8, wdir="VRB", wspd=3, visib="10+", altim=1027.8,
            cover="SCT", clouds=[{"cover": "SCT", "base": 5000}], fltCat="VFR",
        ),
        "airport": airport("KVRB", "VRB", [runway("13/31", 130)]),
        "category": "VFR",
        "summary": "Partly cloudy, 28°F, wind 3 mph from variable directions.",
        "shows": ["Variable", "-2°", "28°F", "No ceiling", "30.35", "High pressure",
                  "Wind direction is variable, so runway components can't be calculated."],
    },
    "KMIN": {
        "about": "Sparse report: no temperature, pressure, category or station name",
        "metar": metar(
            "METAR KMIN 261853Z 18005KT 5SM OVC015",
            wdir=180, wspd=5, visib=5, clouds=[{"cover": "OVC", "base": 1500}],
        ),
        "category": "MVFR",  # not sent by the API, so the app must work it out
        "summary": "Overcast, wind 6 mph from the south.",
        "shows": ["Ceiling at 1,500 ft", "Reduced visibility", "Not reported", "Not enough data"],
    },
}


class FakeResponse:
    def __init__(self, text="", status_code=200):
        self.text = text
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"{self.status_code} Server Error")

    def json(self):
        return json.loads(self.text)


class FakeAviationWeather:
    """Stands in for requests.Session.get against aviationweather.gov."""

    FAILURES = ("timeout", "http_500", "bad_json")

    def __init__(self, scenarios=SCENARIOS):
        self.metars = {code: s["metar"] for code, s in scenarios.items()}
        self.airports = {code: s["airport"] for code, s in scenarios.items() if s.get("airport")}
        self.requests = []   # (endpoint, [ids]) for every call, so tests can inspect them
        self._failures = {}

    def fail(self, endpoint, how):
        """Make every call to `endpoint` ("metar" or "airport") fail in the given way."""
        assert how in self.FAILURES, how
        self._failures[endpoint] = how

    def __call__(self, url, params=None, timeout=None):
        endpoint = url.rstrip("/").rsplit("/", 1)[-1]
        if endpoint not in ("metar", "airport"):
            raise AssertionError(f"Unexpected request to {url}")
        ids = params["ids"].split(",")
        self.requests.append((endpoint, ids))

        failure = self._failures.get(endpoint)
        if failure == "timeout":
            raise requests.Timeout("simulated timeout")
        if failure == "http_500":
            return FakeResponse("Internal Server Error", 500)
        if failure == "bad_json":
            return FakeResponse("<html>maintenance</html>")

        source = self.metars if endpoint == "metar" else self.airports
        found = [source[code] for code in ids if code in source]
        # The real API sends an empty body (not "[]") when nothing matches.
        return FakeResponse(json.dumps(found) if found else "")
