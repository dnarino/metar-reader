import re
from datetime import datetime

from flask import Flask, jsonify, redirect, render_template, request, url_for

import aviation_api
from aviation_api import AviationAPIError
from briefing import CATEGORIES, POPULAR_STATIONS, build_briefing, list_item

CODE_RE = re.compile(r"^[A-Z0-9]{3,4}$")
INVALID_CODE = "Please enter a 3 or 4 character airport code, like KHIO or KJFK."
MAX_LIST_CODES = 20

app = Flask(__name__)


@app.context_processor
def shared_template_data():
    return {
        "popular_stations": POPULAR_STATIONS,
        "categories": CATEGORIES,
        "current_year": datetime.now().year,
    }


def clean_code(value):
    return (value or "").strip().upper()


@app.route("/")
def index():
    return render_template("index.html", active="search")


@app.route("/lookup")
def lookup():
    code = clean_code(request.args.get("code"))
    if not CODE_RE.match(code):
        return render_template("index.html", active="search", code=code, error=INVALID_CODE), 400
    return redirect(url_for("station", code=code))


@app.route("/station/<code>")
def station(code):
    code = clean_code(code)
    if not CODE_RE.match(code):
        return render_template("index.html", active="search", code=code, error=INVALID_CODE), 400

    try:
        metar = aviation_api.fetch_metar(code)
    except AviationAPIError as exc:
        status = 404 if isinstance(exc, aviation_api.StationNotFound) else 502
        return render_template("index.html", active="search", code=code, error=str(exc)), status

    airport = aviation_api.fetch_airport(code)
    return render_template("station.html", active="search", code=code,
                           b=build_briefing(code, metar, airport))


@app.route("/favorites")
def favorites():
    return render_template("stations_list.html", active="favorites", list_kind="favorites")


@app.route("/recent")
def recent():
    return render_template("stations_list.html", active="recent", list_kind="recent")


@app.route("/guide")
def guide():
    return render_template("guide.html", active="guide")


@app.route("/api/stations")
def api_stations():
    """Current conditions for several stations: /api/stations?ids=KJFK,KHIO"""
    codes = [clean_code(c) for c in request.args.get("ids", "").split(",")]
    codes = list(dict.fromkeys(c for c in codes if CODE_RE.match(c)))[:MAX_LIST_CODES]
    if not codes:
        return jsonify({"stations": []})
    try:
        metars = aviation_api.fetch_metars(codes)
    except AviationAPIError as exc:
        return jsonify({"error": str(exc)}), 502
    return jsonify({"stations": [list_item(c, metars[c]) for c in codes if c in metars]})


if __name__ == "__main__":
    app.run(debug=True)
