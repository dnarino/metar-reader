# METAR Reader

A Flask web app that turns cryptic aviation weather reports (METARs) into a friendly briefing.
Type an airport code like `KJFK` and get:

- A plain-English summary, e.g. *"Overcast, 57°F, wind 23 mph from the north-northeast, gusting to 33 mph."*
- The flight category (VFR / MVFR / IFR / LIFR)
- Wind, visibility, clouds and ceiling, temperature and dew point, humidity, altimeter, and density altitude
- Headwind and crosswind for each runway at the airport
- The raw METAR, with a copy button and a Decoder Guide page
- Favorites and recent lookups, saved in your browser

Data comes live from the [NOAA Aviation Weather Center API](https://aviationweather.gov/data/api/).
Not for operational use.

Built while following the freeCodeCamp *Claude Code for Beginners* course.

## Run it

```bash
python -m pip install -r requirements.txt
python app.py
```

Then open http://127.0.0.1:5000.

## Test it

```bash
python -m pip install pytest
python -m pytest
```

## Project layout

| File | Purpose |
|---|---|
| `app.py` | Flask routes |
| `aviation_api.py` | Calls to aviationweather.gov |
| `briefing.py` | Flight category, humidity, density altitude, runway winds |
| `metar_decoder.py` | Parses raw METAR text into plain English |
| `templates/`, `static/` | Front end (plain HTML/CSS/JS, no framework) |
| `.claude/skills/metar-design/` | Claude Code skill with the design system |
