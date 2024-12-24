from flask import Flask, jsonify
from nba_api.live.nba.endpoints import scoreboard
from datetime import datetime

app = Flask(__name__)

# Helper function to fetch today's games
def fetch_games():
    """
    使用 nba_api 的 ScoreBoard 類抓取當天比賽數據
    """
    try:
        # 使用 ScoreBoard 抓取當日比賽數據
        score_board = scoreboard.ScoreBoard()
        games = score_board.games.get_dict()  # 獲取比賽數據字典
        return games
    except Exception as e:
        print(f"Error fetching today's games: {e}")
        return []

@app.route('/api/today_games', methods=['GET'])
def get_today_games():
    games = fetch_games()  # 抓取當天比賽
    if not games:
        return jsonify({"message": "No games today"}), 200

    result = []
    for game in games:
        home_team = game['homeTeam']
        away_team = game['awayTeam']
        game_data = {
            "game_id": game['gameId'],  # 新增 gameId
            "game_date": game['gameTimeUTC'],  # 新增比賽日期（UTC 時間）
            "home_team": f"{home_team['teamCity']} {home_team['teamName']}",
            "away_team": f"{away_team['teamCity']} {away_team['teamName']}",
            "home_score": home_team['score'],
            "away_score": away_team['score'],
            "game_status": game['gameStatusText']
        }

        # Include game leaders if available
        if 'gameLeaders' in game and game['gameStatus'] != 1:  # 1 indicates pre-game
            game_data["home_leader"] = {
                "name": game['gameLeaders']['homeLeaders']['name'],
                "points": game['gameLeaders']['homeLeaders']['points'],
                "rebounds": game['gameLeaders']['homeLeaders']['rebounds'],
                "assists": game['gameLeaders']['homeLeaders']['assists']
            }
            game_data["away_leader"] = {
                "name": game['gameLeaders']['awayLeaders']['name'],
                "points": game['gameLeaders']['awayLeaders']['points'],
                "rebounds": game['gameLeaders']['awayLeaders']['rebounds'],
                "assists": game['gameLeaders']['awayLeaders']['assists']
            }

        result.append(game_data)

    return jsonify(result), 200


if __name__ == '__main__':
    app.run(debug=True)
