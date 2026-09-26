"""Turn API data into the numbers and labels the briefing page shows."""

import math
import re
from datetime import datetime, timezone

from metar_decoder import METARDecoder, degrees_to_compass

M_TO_FT = 3.28084
HPA_TO_INHG = 0.0295300
KT_TO_MPH = 1.15078

CATEGORIES = {
    "VFR": {"name": "Visual Flight Rules", "rule": "Ceiling > 3,000 ft AGL and visibility > 5 SM"},
    "MVFR": {"name": "Marginal VFR", "rule": "Ceiling 1,000 – 3,000 ft or visibility 3 – 5 SM"},
    "IFR": {"name": "Instrument Flight Rules", "rule": "Ceiling 500 – <1,000 ft or visibility 1 – <3 SM"},
    "LIFR": {"name": "Low IFR", "rule": "Ceiling < 500 ft AGL or visibility < 1 SM"},
}

COVER_NAMES = {
    "SKC": "Sky clear", "CLR": "Clear", "NSC": "No significant cloud", "NCD": "No cloud detected",
    "CAVOK": "Ceiling and visibility OK", "FEW": "Few", "SCT": "Scattered",
    "BKN": "Broken", "OVC": "Overcast", "OVX": "Sky obscured", "VV": "Vertical visibility",
}
CEILING_COVERS = {"BKN", "OVC", "OVX", "VV"}

SURFACES = {
    "A": "Asphalt", "C": "Concrete", "G": "Grass", "T": "Turf", "D": "Dirt",
    "H": "Hard surface", "W": "Water", "S": "Sand", "P": "Pierced steel",
}

POPULAR_STATIONS = [
    ("KJFK", "New York"),
    ("KHIO", "Hillsboro"),
    ("EGLL", "Heathrow"),
    ("KLAX", "Los Angeles"),
    ("KORD", "Chicago"),
]


# ---- Pure calculations ---------------------------------------------------

def c_to_f(celsius):
    return round(celsius * 9 / 5 + 32)


def relative_humidity(temp_c, dew_c):
    """Magnus formula, percent."""
    def vapor(t):
        return math.exp(17.625 * t / (243.04 + t))
    return round(100 * vapor(dew_c) / vapor(temp_c))


def density_altitude(elev_ft, temp_c, altim_inhg):
    pressure_alt = elev_ft + (29.92 - altim_inhg) * 1000
    isa_temp = 15 - 2 * elev_ft / 1000
    return round(pressure_alt + 120 * (temp_c - isa_temp))


def parse_visibility(value):
    """API visibility (a number, or a string like '10+' / '6+') -> (miles, text, plus)."""
    if value is None:
        return None, None, False
    text = str(value).strip()
    plus = text.endswith("+")
    try:
        miles = float(text.rstrip("+"))
    except ValueError:
        return None, text, plus
    shown = f"{miles:g}"
    return miles, shown, plus


def ceiling_ft(clouds):
    """Lowest broken/overcast/obscured layer, or None."""
    bases = [c["base"] for c in clouds if c.get("cover") in CEILING_COVERS and c.get("base") is not None]
    return min(bases) if bases else None


def flight_category(ceiling, vis_miles):
    """FAA flight category from ceiling (ft) and visibility (SM)."""
    ceiling = math.inf if ceiling is None else ceiling
    vis = math.inf if vis_miles is None else vis_miles
    if ceiling < 500 or vis < 1:
        return "LIFR"
    if ceiling < 1000 or vis < 3:
        return "IFR"
    if ceiling <= 3000 or vis <= 5:
        return "MVFR"
    return "VFR"


def wind_components(wind_dir, wind_speed, runway_heading):
    """(headwind, crosswind) in knots. Positive crosswind = from the right."""
    angle = math.radians(wind_dir - runway_heading)
    return wind_speed * math.cos(angle), wind_speed * math.sin(angle)


def format_coords(lat, lon):
    if lat is None or lon is None:
        return None
    ns = "N" if lat >= 0 else "S"
    ew = "E" if lon >= 0 else "W"
    return f"{abs(lat):.4f}° {ns}, {abs(lon):.4f}° {ew}"


def split_station_name(full_name, fallback):
    """'New York/JF Kennedy Intl, NY, US' -> ('New York/JF Kennedy Intl', 'NY, US')."""
    if not full_name:
        return fallback, None
    name, _, location = full_name.partition(", ")
    return name, location or None


# ---- Runways -------------------------------------------------------------

def _runway_end_headings(runway):
    """Both ends of a runway as (end id, true heading)."""
    ends = runway.get("id", "").split("/")
    heading = runway.get("alignment")
    if len(ends) != 2 or heading in (None, "-"):
        return []
    try:
        heading = float(heading)
    except (TypeError, ValueError):
        return []
    return [(ends[0], heading % 360), (ends[1], (heading + 180) % 360)]


def runway_analysis(runways, wind_dir, wind_speed, wind_gust):
    """For each runway, the better end for the current wind and its components."""
    results = []
    for runway in runways or []:
        ends = _runway_end_headings(runway)
        if not ends:
            continue
        length = (runway.get("dimension") or "").split("x")[0]
        surface = SURFACES.get(runway.get("surface"), None)

        if wind_speed == 0:
            end, heading = ends[0]
            results.append({
                "id": runway["id"], "end": end, "heading": round(heading),
                "length": length, "surface": surface,
                "status": "CALM", "headwind": 0, "crosswind": 0, "cross_side": None,
                "gust_crosswind": None, "headwind_pct": 0,
            })
            continue
        if wind_dir is None:
            continue  # variable wind: no components to show

        best = max(ends, key=lambda e: wind_components(wind_dir, wind_speed, e[1])[0])
        end, heading = best
        head, cross = wind_components(wind_dir, wind_speed, heading)
        gust_cross = None
        if wind_gust:
            gust_cross = round(abs(wind_components(wind_dir, wind_gust, heading)[1]))

        cross_abs = round(abs(cross))
        if head < -0.5:
            status = "TAILWIND"
        elif cross_abs > 15 or (gust_cross or 0) > 20:
            status = "STRONG CROSSWIND"
        elif cross_abs > 8:
            status = "CROSSWIND"
        else:
            status = "FAVORABLE"

        results.append({
            "id": runway["id"], "end": end, "heading": round(heading),
            "length": length, "surface": surface, "status": status,
            "headwind": round(head), "crosswind": cross_abs,
            "cross_side": None if cross_abs == 0 else ("right" if cross > 0 else "left"),
            "gust_crosswind": gust_cross,
            "headwind_pct": max(0, min(100, round(100 * head / wind_speed))),
        })

    return sorted(results, key=lambda r: (r["status"] == "TAILWIND", r["crosswind"]))


# ---- Remarks ---------------------------------------------------------------

def remarks_info(raw):
    info = {}
    if " AO2" in raw:
        info["station_type"] = "Automated observation with precipitation sensor (AO2)"
    elif " AO1" in raw:
        info["station_type"] = "Automated observation without precipitation sensor (AO1)"
    exact = re.search(r"\bT([01])(\d{3})([01])(\d{3})\b", raw)
    if exact:
        t = int(exact.group(2)) / 10 * (-1 if exact.group(1) == "1" else 1)
        d = int(exact.group(4)) / 10 * (-1 if exact.group(3) == "1" else 1)
        info["exact_temp"] = f"{t:.1f}°C / {d:.1f}°C"
    return info


# ---- View model --------------------------------------------------------------

def _age_text(obs_time, now):
    minutes = int((now - obs_time).total_seconds() // 60)
    if minutes < 1:
        return "just now"
    if minutes < 60:
        return f"{minutes}m ago"
    return f"{minutes // 60}h {minutes % 60}m ago"


def build_briefing(code, metar, airport=None, now=None):
    """Everything the station page shows, from the METAR JSON and optional airport JSON."""
    now = now or datetime.now(timezone.utc)
    raw = metar.get("rawOb", "")
    decoded = METARDecoder(raw)

    name, location = split_station_name(metar.get("name"), code)
    elev_ft = round(metar["elev"] * M_TO_FT) if metar.get("elev") is not None else None

    # Wind
    wdir = metar.get("wdir")
    wind_dir = wdir if isinstance(wdir, (int, float)) else None
    wind_speed = metar.get("wspd") or 0
    wind_gust = metar.get("wgst")
    wind = {
        "speed": wind_speed,
        "gust": wind_gust,
        "dir": wind_dir,
        "variable": wdir == "VRB",
        "calm": wind_speed == 0,
        "compass": degrees_to_compass(wind_dir).title() if wind_dir is not None else None,
        "mph": round(wind_speed * KT_TO_MPH),
        "text": decoded.wind,
    }

    # Visibility
    vis_miles, vis_text, vis_plus = parse_visibility(metar.get("visib"))
    if vis_miles is None:
        vis_note = None
    elif vis_plus or vis_miles >= 10:
        vis_note = ("good", "Unrestricted")
    elif vis_miles > 5:
        vis_note = ("good", "Good visibility")
    elif vis_miles >= 3:
        vis_note = ("warn", "Reduced visibility")
    else:
        vis_note = ("bad", "Low visibility")

    # Clouds. The API calls an obscured sky "OVX"; the METAR itself says "VV".
    clouds = [{**c, "cover": "VV" if c.get("cover") == "OVX" else c.get("cover")}
              for c in (metar.get("clouds") or []) if c.get("cover")]
    ceiling = ceiling_ft(clouds)
    layers = [c for c in clouds if c.get("base") is not None]
    if layers:
        sky_headline = " • ".join(dict.fromkeys(c["cover"] for c in layers))
    else:
        cover = metar.get("cover") or (clouds[0]["cover"] if clouds else None)
        sky_headline = cover or "—"
    sky_layers = [
        f"VV {c['base']:,}' (sky obscured)" if c["cover"] == "VV" else f"{c['cover']} at {c['base']:,}' AGL"
        for c in layers
    ] or [COVER_NAMES.get(sky_headline, sky_headline)]
    sky_note = f"Ceiling at {ceiling:,} ft" if ceiling is not None else "No ceiling"

    # Category
    category = metar.get("fltCat") or flight_category(ceiling, vis_miles)
    if category not in CATEGORIES:
        category = flight_category(ceiling, vis_miles)

    # Temperature
    temp_c = metar.get("temp")
    dew_c = metar.get("dewp")
    temperature = None
    if temp_c is not None:
        temperature = {
            "c": round(temp_c),
            "f": c_to_f(temp_c),
            "dew_c": round(dew_c) if dew_c is not None else None,
            "dew_f": c_to_f(dew_c) if dew_c is not None else None,
            "humidity": relative_humidity(temp_c, dew_c) if dew_c is not None else None,
        }

    # Pressure
    altim_hpa = metar.get("altim")
    pressure = None
    if altim_hpa:
        inhg = altim_hpa * HPA_TO_INHG
        if altim_hpa > 1020:
            trend = "High pressure"
        elif altim_hpa < 1005:
            trend = "Low pressure"
        else:
            trend = "Near standard"
        pressure = {"inhg": f"{inhg:.2f}", "hpa": f"{altim_hpa:.1f}", "trend": trend}

    # Density altitude
    density = None
    if elev_ft is not None and temp_c is not None and altim_hpa:
        da = density_altitude(elev_ft, temp_c, altim_hpa * HPA_TO_INHG)
        above = da - elev_ft
        if above > 2000:
            risk = ("bad", "High risk")
        elif above > 1000:
            risk = ("warn", "Moderate risk")
        else:
            risk = ("good", "Low risk")
        density = {"ft": da, "risk": risk}

    # Time
    obs = None
    if metar.get("obsTime"):
        obs_time = datetime.fromtimestamp(metar["obsTime"], timezone.utc)
        obs = {"time": obs_time.strftime("%H:%M"), "date": obs_time.strftime("%b %d"),
               "age": _age_text(obs_time, now)}

    runways = None
    if airport and airport.get("runways"):
        runways = runway_analysis(airport["runways"], wind_dir, wind_speed, wind_gust)

    return {
        "code": code,
        "name": name,
        "location": location,
        "iata": (airport or {}).get("iataId") or None,
        "coords": format_coords(metar.get("lat"), metar.get("lon")),
        "elev_ft": elev_ft,
        "report_type": metar.get("metarType") or decoded.report_type,
        "category": category,
        "category_info": CATEGORIES[category],
        "summary": decoded.summary(),
        "wind": wind,
        "visibility": {"text": vis_text, "plus": vis_plus, "note": vis_note, "decoded": decoded.visibility},
        "sky": {"headline": sky_headline, "note": sky_note, "layers": sky_layers,
                "weather": [w.capitalize() for w in decoded.weather]},
        "temperature": temperature,
        "pressure": pressure,
        "density": density,
        "obs": obs,
        "raw": raw,
        "remarks": remarks_info(raw),
        "slp": metar.get("slp"),
        "runways": runways,
    }


def list_item(code, metar):
    """Compact data for favorites / recent lookups lists."""
    name, location = split_station_name(metar.get("name"), code)
    b = build_briefing(code, metar)
    return {
        "code": code,
        "name": name,
        "location": location,
        "category": b["category"],
        "temp_f": b["temperature"]["f"] if b["temperature"] else None,
        "summary": b["summary"],
        "obs": b["obs"]["time"] + " UTC" if b["obs"] else None,
    }
