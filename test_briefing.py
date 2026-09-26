from datetime import datetime, timezone

import pytest

from briefing import (
    build_briefing, ceiling_ft, density_altitude, flight_category, format_coords,
    parse_visibility, relative_humidity, runway_analysis, split_station_name, wind_components,
)

# Real responses captured from aviationweather.gov (trimmed).
KJFK_METAR = {
    "icaoId": "KJFK", "obsTime": 1790427060, "temp": 13.9, "dewp": 11.7,
    "wdir": 20, "wspd": 20, "wgst": 33, "visib": 7, "altim": 1008.2, "slp": 1008,
    "metarType": "METAR",
    "rawOb": "METAR KJFK 261251Z 02020G33KT 7SM BKN020 OVC040 14/12 A2977 RMK AO2 PK WND 02035/1159 "
             "RAE50 SLP080 P0005 T01390117 $",
    "lat": 40.6392, "lon": -73.7639, "elev": 3, "name": "New York/JF Kennedy Intl, NY, US",
    "cover": "OVC", "clouds": [{"cover": "BKN", "base": 2000}, {"cover": "OVC", "base": 4000}],
    "fltCat": "MVFR",
}
KJFK_AIRPORT = {
    "icaoId": "KJFK", "iataId": "JFK",
    "runways": [
        {"id": "04L/22R", "dimension": "12079x200", "surface": "C", "alignment": 31},
        {"id": "13R/31L", "dimension": "14511x200", "surface": "C", "alignment": 121},
    ],
}
NOW = datetime(2026, 9, 26, 13, 3, tzinfo=timezone.utc)


def test_flight_category_boundaries():
    assert flight_category(None, 10) == "VFR"
    assert flight_category(3500, 6) == "VFR"
    assert flight_category(3000, 10) == "MVFR"
    assert flight_category(None, 4) == "MVFR"
    assert flight_category(800, 10) == "IFR"
    assert flight_category(None, 2) == "IFR"
    assert flight_category(400, 10) == "LIFR"
    assert flight_category(None, 0.25) == "LIFR"


def test_ceiling_is_lowest_broken_or_overcast():
    assert ceiling_ft([{"cover": "FEW", "base": 1000}, {"cover": "BKN", "base": 2500},
                       {"cover": "OVC", "base": 1800}]) == 1800
    assert ceiling_ft([{"cover": "SCT", "base": 1000}]) is None
    assert ceiling_ft([{"cover": "CLR"}]) is None


def test_parse_visibility():
    assert parse_visibility(7) == (7.0, "7", False)
    assert parse_visibility("10+") == (10.0, "10", True)
    assert parse_visibility(0.25) == (0.25, "0.25", False)
    assert parse_visibility(None) == (None, None, False)


def test_humidity_and_density_altitude():
    assert relative_humidity(20, 20) == 100
    assert relative_humidity(18, 6) == 45
    # Standard day at sea level: density altitude = 0.
    assert density_altitude(0, 15, 29.92) == 0
    # Hot day at a high field: ISA there is 5°C, so 5000 + 120 × 25 = 8000.
    assert density_altitude(5000, 30, 29.92) == 8000


def test_wind_components():
    head, cross = wind_components(310, 12, 310)
    assert head == pytest.approx(12) and cross == pytest.approx(0, abs=1e-9)
    head, cross = wind_components(40, 10, 310)  # 90° from the right
    assert head == pytest.approx(0, abs=1e-9) and cross == pytest.approx(10)


def test_runway_analysis_picks_best_end():
    rwys = runway_analysis(KJFK_AIRPORT["runways"], wind_dir=20, wind_speed=20, wind_gust=33)
    by_id = {r["id"]: r for r in rwys}
    rwy4 = by_id["04L/22R"]
    assert rwy4["end"] == "04L"            # into the wind
    assert rwy4["headwind"] == 20 and rwy4["crosswind"] == 4  # 20 × sin(11°) ≈ 3.8
    assert rwy4["status"] == "FAVORABLE"
    rwy13 = by_id["13R/31L"]
    assert rwy13["crosswind"] == 20
    assert rwy13["status"] == "STRONG CROSSWIND"
    assert rwys[0]["id"] == "04L/22R"      # least crosswind first


def test_runway_analysis_calm_and_variable():
    calm = runway_analysis(KJFK_AIRPORT["runways"], None, 0, None)
    assert all(r["status"] == "CALM" for r in calm)
    assert runway_analysis(KJFK_AIRPORT["runways"], None, 5, None) == []


def test_names_and_coords():
    assert split_station_name("New York/JF Kennedy Intl, NY, US", "KJFK") == ("New York/JF Kennedy Intl", "NY, US")
    assert split_station_name(None, "KJFK") == ("KJFK", None)
    assert format_coords(40.6392, -73.7639) == "40.6392° N, 73.7639° W"


def test_build_briefing_kjfk():
    b = build_briefing("KJFK", KJFK_METAR, KJFK_AIRPORT, now=NOW)
    assert b["name"] == "New York/JF Kennedy Intl"
    assert b["iata"] == "JFK"
    assert b["elev_ft"] == 10
    assert b["category"] == "MVFR"
    assert b["wind"]["compass"] == "North-Northeast"
    assert b["sky"]["headline"] == "BKN • OVC"
    assert b["sky"]["note"] == "Ceiling at 2,000 ft"
    assert b["temperature"]["f"] == 57
    assert b["pressure"]["inhg"] == "29.77"
    assert b["obs"]["time"] == "12:51" and b["obs"]["age"] == "12m ago"
    assert b["remarks"]["station_type"].endswith("(AO2)")
    assert b["remarks"]["exact_temp"] == "13.9°C / 11.7°C"
    assert b["summary"].startswith("Overcast, 57°F, wind 23 mph")


def test_build_briefing_without_airport_data():
    b = build_briefing("KJFK", KJFK_METAR, None, now=NOW)
    assert b["runways"] is None
    assert b["iata"] is None
