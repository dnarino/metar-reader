from metar_decoder import METARDecoder


def test_khio_real_report():
    m = METARDecoder("SPECI KHIO 261323Z 00000KT 10SM BKN003 05/05 A3018 RMK AO2 T00500050")
    assert m.report_type == "SPECI"
    assert m.station == "KHIO"
    assert m.time == "Observed on the 26th at 13:23 UTC"
    assert m.wind_calm
    assert m.visibility == "10 miles"
    assert m.clouds == ["Broken clouds at 300 ft"]
    assert m.temperature_c == 5 and m.dewpoint_c == 5
    assert m.pressure == "30.18 inHg"
    assert m.summary() == "Mostly cloudy, 41°F, calm winds."


def test_clear_with_south_wind():
    m = METARDecoder("METAR KLAX 261853Z 18004KT 10SM CLR 21/12 A2992")
    assert m.wind == "5 mph from the south"
    assert m.summary() == "Clear skies, 70°F, wind 5 mph from the south."


def test_gusts_and_variable_direction():
    m = METARDecoder("KJFK 261851Z 27015G25KT 240V300 10SM FEW050 18/08 A2990")
    assert m.wind == ("17 mph from the west, gusting to 29 mph, "
                      "varying between west-southwest and west-northwest")


def test_fractional_visibility():
    assert METARDecoder("KXYZ 261851Z 00000KT 1/2SM FG OVC002 10/10 A3000").visibility == "1/2 miles"
    assert METARDecoder("KXYZ 261851Z 00000KT 1 1/2SM BR OVC005 10/10 A3000").visibility == "1 1/2 miles"
    assert METARDecoder("KXYZ 261851Z 00000KT 1SM BR OVC005 10/10 A3000").visibility == "1 mile"
    assert METARDecoder("KXYZ 261851Z 00000KT P6SM SKC 10/10 A3000").visibility == "more than 6 miles"


def test_negative_temperatures():
    m = METARDecoder("KXYZ 261851Z 36010KT 10SM SCT030 M02/M05 A3010")
    assert m.temperature_c == -2
    assert m.dewpoint_c == -5
    assert "28°F" in m.summary()


def test_weather_phenomena():
    m = METARDecoder("KSEA 261853Z 19008KT 3SM -RA BR OVC012 12/11 A2980")
    assert m.weather == ["light rain", "mist"]
    assert m.summary().startswith("Overcast with light rain, mist, 54°F")


def test_showers_and_thunderstorms():
    assert METARDecoder("KXYZ 261851Z 00000KT 5SM -SHRA BKN020 20/18 A2990").weather == ["light rain showers"]
    assert METARDecoder("KXYZ 261851Z 00000KT 5SM +TSRA BKN020CB 20/18 A2990").weather == ["heavy thunderstorm with rain"]


def test_cloud_layers_pick_most_significant():
    m = METARDecoder("KXYZ 261851Z 00000KT 10SM FEW010 SCT030 OVC080 10/05 A3000")
    assert m.sky_cover == "OVC"
    assert m.clouds[-1] == "Overcast at 8,000 ft"


def test_metric_report():
    m = METARDecoder("METAR EGLL 261850Z 24012KT 9999 FEW035 15/09 Q1015")
    assert m.visibility == "10 km or more"
    assert m.pressure == "1015 hPa"
    assert m.summary() == "Mostly clear, 59°F, wind 14 mph from the west-southwest."


def test_unknown_tokens_do_not_crash():
    m = METARDecoder("KXYZ 261851Z AUTO 00000KT R28L/2600FT 10SM CLR 10/05 A3000 NOSIG")
    assert "automated station" in m.flags
    assert m.summary() == "Clear skies, 50°F, calm winds."
