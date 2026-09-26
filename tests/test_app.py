"""Tests for app.py, using mock METAR readings from mock_weather.py (no internet needed)."""

from datetime import datetime

import pytest

from mock_weather import SCENARIOS

SCENARIO_CODES = list(SCENARIOS)


# ---- 1. Mock METAR readings are interpreted correctly -------------------------

@pytest.mark.parametrize("code", SCENARIO_CODES, ids=[f"{c}-{SCENARIOS[c]['about']}" for c in SCENARIO_CODES])
def test_station_page_interprets_metar(page, code):
    expected = SCENARIOS[code]
    status, text = page(f"/station/{code}")

    assert status == 200
    assert f'class="cat cat-stamp cat-{expected["category"]}"' in text
    assert f'<p class="summary-line">{expected["summary"]}</p>' in text
    for snippet in expected["shows"]:
        assert snippet in text, f"{code}: expected to see {snippet!r}"
    assert expected["metar"]["rawOb"] in text  # raw report is always shown


@pytest.mark.parametrize("code", SCENARIO_CODES)
def test_api_stations_interprets_metar(client, code):
    data = client.get(f"/api/stations?ids={code}").get_json()
    (station,) = data["stations"]
    assert station["code"] == code
    assert station["category"] == SCENARIOS[code]["category"]
    assert station["summary"] == SCENARIOS[code]["summary"]


def test_missing_station_name_falls_back_to_code(page):
    _, text = page("/station/KMIN")
    assert '<p class="station-name">KMIN</p>' in text


def test_lowercase_station_url_works(page):
    status, text = page("/station/kaaa")
    assert status == 200
    assert '<span class="station-code">KAAA</span>' in text


# ---- 2. The weather service misbehaves --------------------------------------------

def test_unknown_airport_shows_not_found(page):
    status, text = page("/station/ZZZZ")
    assert status == 404
    assert "No METAR report found for ZZZZ. Check the airport code." in text


@pytest.mark.parametrize("failure, message", [
    ("timeout", "The weather service took too long to respond."),
    ("http_500", "Couldn't reach the weather service."),
    ("bad_json", "The weather service sent an unexpected response."),
])
def test_service_errors_show_friendly_message(page, fake_weather, failure, message):
    fake_weather.fail("metar", failure)
    status, text = page("/station/KAAA")
    assert status == 502
    assert message in text
    assert 'class="alert"' in text


@pytest.mark.parametrize("failure", ["timeout", "http_500", "bad_json"])
def test_airport_data_failure_still_shows_weather(page, fake_weather, failure):
    fake_weather.fail("airport", failure)
    status, text = page("/station/KAAA")
    assert status == 200
    assert SCENARIOS["KAAA"]["summary"] in text
    assert "No runway data available for this station." in text


# ---- 3. User input is validated ------------------------------------------------------

def test_lookup_cleans_code_and_redirects(client, fake_weather):
    response = client.get("/lookup?code=%20khio%20")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/station/KHIO")
    assert fake_weather.requests == []  # the redirect itself doesn't call the service


@pytest.mark.parametrize("bad_code", ["", "12", "TOOLONG", "K!@#", "KJ K"])
def test_lookup_rejects_invalid_codes(page, fake_weather, bad_code):
    status, text = page(f"/lookup?code={bad_code}")
    assert status == 400
    assert "Please enter a 3 or 4 character airport code" in text
    assert fake_weather.requests == []


def test_station_url_rejects_invalid_code(page, fake_weather):
    status, _ = page("/station/k!")
    assert status == 400
    assert fake_weather.requests == []


# ---- 4. /api/stations (used by Favorites / Recent) -------------------------------------

def test_api_stations_batches_and_cleans_ids(client, fake_weather):
    data = client.get("/api/stations?ids=kaaa,KFOG,KAAA,bad!,ZZZZ,,egxx").get_json()

    assert [s["code"] for s in data["stations"]] == ["KAAA", "KFOG", "EGXX"]  # order kept, unknown dropped
    assert fake_weather.requests == [("metar", ["KAAA", "KFOG", "ZZZZ", "EGXX"])]  # one call, cleaned ids


def test_api_stations_limits_number_of_codes(client, fake_weather):
    codes = [f"K{n:03d}" for n in range(25)]
    client.get(f"/api/stations?ids={','.join(codes)}")
    (_, requested), = fake_weather.requests
    assert requested == codes[:20]


def test_api_stations_without_valid_ids(client, fake_weather):
    assert client.get("/api/stations?ids=!!,1").get_json() == {"stations": []}
    assert client.get("/api/stations").get_json() == {"stations": []}
    assert fake_weather.requests == []


def test_api_stations_service_error(client, fake_weather):
    fake_weather.fail("metar", "timeout")
    response = client.get("/api/stations?ids=KAAA")
    assert response.status_code == 502
    assert "took too long" in response.get_json()["error"]


# ---- 5. Other pages ---------------------------------------------------------------------

@pytest.mark.parametrize("path, nav_label", [
    ("/", "Search Weather"),
    ("/favorites", "Favorites"),
    ("/recent", "Recent Reports"),
    ("/guide", "Decoder Guide"),
])
def test_pages_render_with_active_nav(page, path, nav_label):
    status, text = page(path)
    assert status == 200
    assert text.count('aria-current="page"') == 1
    assert f'aria-current="page">{nav_label}</a>' in text


def test_footer_shows_copyright_and_github(page):
    _, text = page("/")
    assert f"© {datetime.now().year} dnarino" in text
    assert 'href="https://github.com/dnarino"' in text
