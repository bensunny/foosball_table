from flask import Flask, request, jsonify, render_template
from http import HTTPStatus
import foosball


app = Flask(__name__)


def json_error(error, status_code):
    response = jsonify(error=str(error))
    response.status_code = status_code
    return response


def score_validator(goals):
    if not isinstance(goals, (int, float)):
        raise TypeError(f"{goals} must be an integer or float")
    if 0 < goals > 10:
        raise ValueError("{goals} cannot be more than 10 or less than 0")


@app.route("/v1/")
def welcome():
    return "Welcome to the league table app"


@app.route("/v1/health")
def health():
    return "OK"


@app.route("/v1/player", methods=["POST"])
def add_player():
    try:
        data = request.get_json()
        first_name = data["first_name"]
        last_name = data["last_name"]
        foosball.add_player(first_name=first_name, last_name=last_name)
        return jsonify(player_added=True, first_name=first_name, last_name=last_name)
    except Exception as err:
        json_error(err, HTTPStatus.BAD_REQUEST)


@app.route("/v1/delete")
def delete():
    try:
        data = request.get_json()
        first_name = data["first_name"]
        last_name = data["last_name"]
        foosball.delete_player(first_name=first_name, last_name=last_name)
        return jsonify(player_deleted=True, first_name=first_name, last_name=last_name)
    except Exception as err:
        json_error(err, HTTPStatus.BAD_REQUEST)


@app.route("/v1/fixture")
def schedule():
    foosball._fixtures()
    return foosball.show_fixtures()


@app.route("/v1/fixture/")
def fixtures():
    fixture_table = foosball.show_fixtures()
    return render_template("temp.html", table=fixture_table)


@app.route("/v1/result", methods=["POST"])
def result():
    try:
        data = request.get_json()
        match_id = data["match_id"]
        home_goals = data["home_goals"]
        away_goals = data["away_goals"]
        score_validator(home_goals)
        score_validator(away_goals)
        foosball.add_result(match_id=match_id, home_goals=home_goals, away_goals=away_goals)
        return jsonify(result_added=True)
    except Exception as err:
        json_error(err, HTTPStatus.BAD_REQUEST)


@app.route("/v1/league")
def league():
    league_table = foosball.league_table()
    return render_template("temp.html", table=league_table)


if __name__ == "__main__":
    # foosball.create_database(force=True)
    app.run(host="0.0.0.0", port=5000)
