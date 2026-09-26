"""Decode raw METAR weather reports into plain English."""

import re

KT_TO_MPH = 1.15078

COMPASS_POINTS = [
    "north", "north-northeast", "northeast", "east-northeast",
    "east", "east-southeast", "southeast", "south-southeast",
    "south", "south-southwest", "southwest", "west-southwest",
    "west", "west-northwest", "northwest", "north-northwest",
]

INTENSITY = {"-": "light", "+": "heavy", "VC": "in the vicinity"}

DESCRIPTORS = {
    "MI": "shallow", "PR": "partial", "BC": "patches of", "DR": "low drifting",
    "BL": "blowing", "SH": "showers", "TS": "thunderstorm", "FZ": "freezing",
}

PHENOMENA = {
    "DZ": "drizzle", "RA": "rain", "SN": "snow", "SG": "snow grains",
    "IC": "ice crystals", "PL": "ice pellets", "GR": "hail", "GS": "small hail",
    "UP": "unknown precipitation", "BR": "mist", "FG": "fog", "FU": "smoke",
    "VA": "volcanic ash", "DU": "dust", "SA": "sand", "HZ": "haze",
    "PY": "spray", "PO": "dust whirls", "SQ": "squalls", "FC": "funnel cloud",
    "SS": "sandstorm", "DS": "duststorm",
}

CLOUD_COVER = {
    "FEW": "Few clouds", "SCT": "Scattered clouds",
    "BKN": "Broken clouds", "OVC": "Overcast",
}

CLEAR_SKY = {"SKC", "CLR", "NSC", "NCD", "CAVOK"}

WIND_RE = re.compile(r"^(\d{3}|VRB)(\d{2,3})(?:G(\d{2,3}))?(KT|MPS)$")
WIND_VAR_RE = re.compile(r"^(\d{3})V(\d{3})$")
VIS_SM_RE = re.compile(r"^(P|M)?(\d+(?:/\d+)?)SM$")
VIS_M_RE = re.compile(r"^(\d{4})(NDV)?$")
WEATHER_RE = re.compile(
    r"^(-|\+|VC)?((?:MI|PR|BC|DR|BL|SH|TS|FZ)*)((?:DZ|RA|SN|SG|IC|PL|GR|GS|UP|BR|FG|FU|VA|DU|SA|HZ|PY|PO|SQ|FC|SS|DS)*)$"
)
CLOUD_RE = re.compile(r"^(FEW|SCT|BKN|OVC)(\d{3})(CB|TCU)?$")
VV_RE = re.compile(r"^VV(\d{3}|///)$")
TEMP_RE = re.compile(r"^(M?\d{2})/(M?\d{2})?$")
ALTIMETER_RE = re.compile(r"^A(\d{4})$")
QNH_RE = re.compile(r"^Q(\d{4})$")
TIME_RE = re.compile(r"^(\d{2})(\d{2})(\d{2})Z$")


def ordinal(n):
    if 10 <= n % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def c_to_f(celsius):
    return round(celsius * 9 / 5 + 32)


def parse_temp(value):
    return -int(value[1:]) if value.startswith("M") else int(value)


def degrees_to_compass(degrees):
    return COMPASS_POINTS[round(degrees / 22.5) % 16]


def eval_fraction(text):
    if "/" in text:
        num, den = text.split("/")
        return int(num) / int(den)
    return float(text)


class METARDecoder:
    """Parses a raw METAR string. Decoded parts are available as attributes."""

    def __init__(self, raw):
        self.raw = raw.strip()
        self.report_type = "METAR"
        self.station = None
        self.time = None
        self.flags = []
        self.wind = None
        self.wind_calm = False
        self.visibility = None
        self.weather = []
        self.clouds = []
        self.sky_cover = None  # most significant cover code, e.g. "BKN"
        self.temperature_c = None
        self.dewpoint_c = None
        self.pressure = None
        self.remarks = None
        self._parse()

    def _parse(self):
        body, _, remarks = self.raw.partition(" RMK ")
        self.remarks = remarks or None
        tokens = body.split()

        if tokens and tokens[0] in ("METAR", "SPECI"):
            self.report_type = tokens.pop(0)
        if tokens:
            self.station = tokens.pop(0)

        i = 0
        while i < len(tokens):
            token = tokens[i]
            # Visibility like "1 1/2SM" is split into two tokens.
            if (token.isdigit() and i + 1 < len(tokens)
                    and re.match(r"^\d/\dSM$", tokens[i + 1])):
                self._decode_visibility(f"{token} {tokens[i + 1]}")
                i += 2
                continue
            self._decode_token(token)
            i += 1

    def _decode_token(self, token):
        if TIME_RE.match(token):
            self._decode_time(token)
        elif token in ("AUTO", "COR"):
            self.flags.append("automated station" if token == "AUTO" else "corrected report")
        elif WIND_RE.match(token):
            self._decode_wind(token)
        elif WIND_VAR_RE.match(token):
            low, high = WIND_VAR_RE.match(token).groups()
            if self.wind:
                self.wind += (f", varying between {degrees_to_compass(int(low))}"
                              f" and {degrees_to_compass(int(high))}")
        elif VIS_SM_RE.match(token) or (VIS_M_RE.match(token) and self.visibility is None):
            self._decode_visibility(token)
        elif token in CLEAR_SKY:
            self.sky_cover = "CLR"
            self.clouds.append("Clear skies")
            if token == "CAVOK":
                self.visibility = "10 km or more"
        elif CLOUD_RE.match(token) or VV_RE.match(token):
            self._decode_cloud(token)
        elif TEMP_RE.match(token):
            self._decode_temperature(token)
        elif ALTIMETER_RE.match(token) or QNH_RE.match(token):
            self._decode_pressure(token)
        elif WEATHER_RE.match(token):
            self._decode_weather(token)
        # Anything else (runway visual range, trends, etc.) is ignored.

    def _decode_time(self, token):
        day, hour, minute = TIME_RE.match(token).groups()
        self.time = f"Observed on the {ordinal(int(day))} at {hour}:{minute} UTC"

    def _decode_wind(self, token):
        direction, speed, gust, unit = WIND_RE.match(token).groups()
        speed = int(speed)
        to_mph = KT_TO_MPH if unit == "KT" else 2.23694

        if speed == 0:
            self.wind_calm = True
            self.wind = "Calm"
            return

        mph = round(speed * to_mph)
        if direction == "VRB":
            text = f"{mph} mph from variable directions"
        else:
            text = f"{mph} mph from the {degrees_to_compass(int(direction))}"
        if gust:
            text += f", gusting to {round(int(gust) * to_mph)} mph"
        self.wind = text

    def _decode_visibility(self, token):
        if token.endswith("SM"):
            value = token[:-2]
            prefix = ""
            if value.startswith("P"):
                prefix, value = "more than ", value[1:]
            elif value.startswith("M"):
                prefix, value = "less than ", value[1:]
            number = sum(eval_fraction(part) for part in value.split())
            unit = "mile" if number == 1 else "miles"
            self.visibility = f"{prefix}{value} {unit}"
        else:
            meters = int(token[:4])
            if meters == 9999:
                self.visibility = "10 km or more"
            elif meters >= 1000:
                self.visibility = f"{meters / 1000:g} km"
            else:
                self.visibility = f"{meters} meters"

    def _decode_weather(self, token):
        intensity, descriptors, phenomena = WEATHER_RE.match(token).groups()
        if not descriptors and not phenomena:
            return
        desc_list = [DESCRIPTORS[descriptors[j:j + 2]] for j in range(0, len(descriptors), 2)]
        phen_list = [PHENOMENA[phenomena[j:j + 2]] for j in range(0, len(phenomena), 2)]

        words = []
        if intensity in ("-", "+"):
            words.append(INTENSITY[intensity])
        # "Thunderstorm with rain" and "rain showers" read more naturally.
        if "thunderstorm" in desc_list and phen_list:
            words.append("thunderstorm with")
            desc_list.remove("thunderstorm")
        trailing = [d for d in desc_list if d in ("showers", "thunderstorm")]
        words.extend(d for d in desc_list if d not in trailing)
        if phen_list:
            words.append(" and ".join(phen_list))
        words.extend(trailing)
        if intensity == "VC":
            words.append(INTENSITY["VC"])
        self.weather.append(" ".join(words))

    def _decode_cloud(self, token):
        vv = VV_RE.match(token)
        if vv:
            height = vv.group(1)
            if height == "///":
                self.clouds.append("Sky obscured")
            else:
                self.clouds.append(f"Sky obscured, vertical visibility {int(height) * 100:,} ft")
            self.sky_cover = "OVC"
            return

        cover, height, cloud_type = CLOUD_RE.match(token).groups()
        text = f"{CLOUD_COVER[cover]} at {int(height) * 100:,} ft"
        if cloud_type == "CB":
            text += " (cumulonimbus)"
        elif cloud_type == "TCU":
            text += " (towering cumulus)"
        self.clouds.append(text)

        order = ["CLR", "FEW", "SCT", "BKN", "OVC"]
        if self.sky_cover is None or order.index(cover) > order.index(self.sky_cover):
            self.sky_cover = cover

    def _decode_temperature(self, token):
        temp, dew = TEMP_RE.match(token).groups()
        self.temperature_c = parse_temp(temp)
        if dew:
            self.dewpoint_c = parse_temp(dew)

    def _decode_pressure(self, token):
        if token.startswith("A"):
            self.pressure = f"{int(token[1:]) / 100:.2f} inHg"
        else:
            self.pressure = f"{int(token[1:])} hPa"

    # ---- Friendly output -------------------------------------------------

    def sky_description(self):
        return {
            "CLR": "Clear skies",
            "FEW": "Mostly clear",
            "SCT": "Partly cloudy",
            "BKN": "Mostly cloudy",
            "OVC": "Overcast",
            None: None,
        }[self.sky_cover]

    def summary(self):
        """One friendly sentence, e.g. 'Partly cloudy, 70°F, wind 5 mph from the south.'"""
        parts = []
        sky = self.sky_description()
        if self.weather:
            weather = ", ".join(self.weather)
            parts.append(f"{sky} with {weather}" if sky else weather.capitalize())
        elif sky:
            parts.append(sky)

        if self.temperature_c is not None:
            parts.append(f"{c_to_f(self.temperature_c)}°F")

        if self.wind_calm:
            parts.append("calm winds")
        elif self.wind:
            parts.append(f"wind {self.wind}")

        if not parts:
            return "Weather details unavailable."
        sentence = ", ".join(parts)
        return sentence[0].upper() + sentence[1:] + "."

    def details(self):
        """List of (label, value) pairs for display."""
        rows = []
        if self.time:
            rows.append(("Time", self.time))
        if self.wind:
            rows.append(("Wind", self.wind))
        if self.visibility:
            rows.append(("Visibility", self.visibility))
        if self.weather:
            rows.append(("Weather", ", ".join(w.capitalize() for w in self.weather)))
        if self.clouds:
            rows.append(("Clouds", "; ".join(self.clouds)))
        if self.temperature_c is not None:
            rows.append(("Temperature",
                         f"{c_to_f(self.temperature_c)}°F ({self.temperature_c}°C)"))
        if self.dewpoint_c is not None:
            rows.append(("Dew point",
                         f"{c_to_f(self.dewpoint_c)}°F ({self.dewpoint_c}°C)"))
        if self.pressure:
            rows.append(("Pressure", self.pressure))
        if self.flags:
            rows.append(("Notes", ", ".join(self.flags).capitalize()))
        return rows
