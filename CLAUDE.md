# METAR Reader

Flask app: the user enters an airport code, the app fetches the METAR from aviationweather.gov and shows a
decoded flight-weather briefing in plain English.

- `aviation_api.py`: calls to aviationweather.gov (`metar` and `airport` JSON endpoints)
- `briefing.py`: turns API data into the page's numbers (flight category, humidity, density altitude, runway crosswind)
- `metar_decoder.py`: `METARDecoder` parses the raw METAR text into plain English (`summary()`)
- `app.py`: routes: `/`, `/lookup`, `/station/<code>`, `/favorites`, `/recent`, `/guide`, `/api/stations`
- `templates/`, `static/style.css`, `static/app.js`: front end (no CSS framework)

## Commands
- Run: `python app.py` (http://127.0.0.1:5000)
- Test: `python -m pytest` (tests live in `tests/`, config in `pytest.ini`)

## Testing
- Tests never call the real API. `tests/conftest.py` swaps `aviation_api._session.get` for `FakeAviationWeather`.
- New weather situation? Add a scenario (mock METAR + expected category/summary/text) to `SCENARIOS` in
  `tests/mock_weather.py`, and the parametrized tests in `tests/test_app.py` cover it automatically.
- Pure calculations (category, crosswind, density altitude…) get direct tests in `tests/test_briefing.py`.

## Front end
Before changing anything in `templates/` or `static/`, follow the `metar-design` skill
(`.claude/skills/metar-design/SKILL.md`). It holds the design system, the spec (`DESIGN.md`) and a reference screenshot.
