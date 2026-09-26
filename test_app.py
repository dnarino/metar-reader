import pytest

import aviation_api
from app import app
from test_briefing import KJFK_AIRPORT, KJFK_METAR


@pytest.fixture
def client(monkeypatch):
    """Flask test client with the weather service replaced by canned data."""
    def fake_fetch_metars(codes):
        return {"KJFK": KJFK_METAR} if "KJFK" in codes else {}

    def fake_fetch_airport(code):
        return KJFK_AIRPORT if code == "KJFK" else None

    monkeypatch.setattr(aviation_api, "fetch_metars", fake_fetch_metars)
    monkeypatch.setattr(aviation_api, "fetch_airport", fake_fetch_airport)
    return app.test_client()


def test_pages_render(client):
    for path in ["/", "/favorites", "/recent", "/guide"]:
        assert client.get(path).status_code == 200, path


def test_lookup_redirects_to_station(client):
    res = client.get("/lookup?code=kjfk")
    assert res.status_code == 302
    assert res.headers["Location"].endswith("/station/KJFK")


def test_lookup_rejects_bad_code(client):
    res = client.get("/lookup?code=12")
    assert res.status_code == 400
    assert b"3 or 4 character" in res.data


def test_station_page(client):
    html = client.get("/station/KJFK").get_data(as_text=True)
    assert "New York/JF Kennedy Intl" in html
    assert "cat-MVFR" in html
    assert "Runway 04L" in html
    assert "METAR KJFK 261251Z" in html


def test_unknown_station(client):
    res = client.get("/station/ZZZZ")
    assert res.status_code == 404
    assert b"No METAR report found for ZZZZ" in res.data


def test_service_down(client, monkeypatch):
    def broken(codes):
        raise aviation_api.AviationAPIError("Couldn't reach the weather service. Please try again later.")
    monkeypatch.setattr(aviation_api, "fetch_metars", broken)
    res = client.get("/station/KJFK")
    assert res.status_code == 502
    assert b"Couldn&#39;t reach the weather service" in res.data


def test_api_stations(client):
    data = client.get("/api/stations?ids=kjfk,ZZZZ,bad!,KJFK").get_json()
    assert [s["code"] for s in data["stations"]] == ["KJFK"]
    assert data["stations"][0]["category"] == "MVFR"
    assert data["stations"][0]["temp_f"] == 57
