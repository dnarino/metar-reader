import html
import re

import pytest

import aviation_api
from app import app
from mock_weather import FakeAviationWeather


@pytest.fixture
def fake_weather(monkeypatch):
    """Replace the HTTP session with canned aviationweather.gov responses."""
    fake = FakeAviationWeather()
    monkeypatch.setattr(aviation_api._session, "get", fake)
    return fake


@pytest.fixture
def client(fake_weather):
    return app.test_client()


@pytest.fixture
def page(client):
    """GET a path -> (status code, page text with HTML entities decoded and whitespace collapsed)."""
    def get(path):
        response = client.get(path)
        text = html.unescape(response.get_data(as_text=True))
        return response.status_code, re.sub(r"\s+", " ", text)
    return get
