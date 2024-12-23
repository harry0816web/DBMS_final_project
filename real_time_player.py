from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

NBA_BOX_SCORE_URL = "https://cdn.nba.com/static/json/liveData/boxscore/boxscore_{game_id}.json"

@app.route("/get_players", methods=["GET"])
def get_players():
    game_id = request.args.get("game_id")
    if not game_id:
        return jsonify({"error": "Game ID is required"}), 400

    url = NBA_BOX_SCORE_URL.format(game_id=game_id)

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to fetch data from NBA API: {str(e)}"}), 500

    try:
        game_data = data.get("game", {})
        players = []

        for team_key in ["homeTeam", "awayTeam"]:
            team_data = game_data.get(team_key, {})
            team_name = team_data.get("teamName", "Unknown Team")
            for player in team_data.get("players", []):
                if player.get("played") == "1":
                    players.append({
                        "name": player.get("name"),
                        "first_name": player.get("firstName"),
                        "last_name": player.get("familyName"),
                        "team": team_name,
                        "position": player.get("position"),
                        "minutes": player.get("statistics", {}).get("minutes", "0:00"),
                        "points": player.get("statistics", {}).get("points", 0),
                        "rebounds": player.get("statistics", {}).get("reboundsTotal", 0),
                        "assists": player.get("statistics", {}).get("assists", 0),
                        "steals": player.get("statistics", {}).get("steals", 0),
                        "blocks": player.get("statistics", {}).get("blocks", 0)
                    })

        return jsonify({"game_id": game_id, "players": players})

    except KeyError as e:
        return jsonify({"error": f"Data parsing error: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True)
