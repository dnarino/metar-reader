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
- Test: `python -m pytest`

## Front end
Before changing anything in `templates/` or `static/`, follow the `metar-design` skill
(`.claude/skills/metar-design/SKILL.md`). It holds the design system, the spec (`DESIGN.md`) and a reference screenshot.
