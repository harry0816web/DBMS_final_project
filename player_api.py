from flask import Flask, jsonify, request
import mysql.connector

# Initialize the Flask app
app = Flask(__name__)

# Database connection configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'lin20040913',
    'database': 'nba_database'
}

def get_db_connection():
    """
    Create and return a database connection.
    """
    return mysql.connector.connect(**DB_CONFIG)

def get_average_stats_for_season(player_name, start_date, end_date):
    """
    Fetch average stats for a player for a specific date range.
    :param player_name: Name of the player.
    :param start_date: Start date of the range (YYYY-MM-DD).
    :param end_date: End date of the range (YYYY-MM-DD).
    :return: Average stats for the specified date range.
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT 
        AVG(pg.pts) AS avg_points,
        AVG(pg.reb) AS avg_rebounds,
        AVG(pg.stl) AS avg_steals,
        AVG(pg.blk) AS avg_blocks,
        AVG(pg.ast) AS avg_assists,
        AVG(pg.pf) AS avg_fouls,
        AVG(pg.tov) AS avg_turnovers,
        AVG(pg.min) AS avg_minutes_played,
        AVG(pg.fg_pct) AS avg_field_goal_percentage,
        AVG(pg.fg3_pct) AS avg_three_point_percentage,
        AVG(pg.ft_pct) AS avg_free_throw_percentage
    FROM player_game_logs AS pg
    JOIN name_id_map AS nm ON pg.player_id = nm.player_id
    WHERE nm.player_name = %s AND pg.game_date BETWEEN %s AND %s
    """

    cursor.execute(query, (player_name, start_date, end_date))
    result = cursor.fetchone()

    cursor.close()
    conn.close()

    return result

def get_season_date_range(season):
    """
    Calculate the start and end date for a given NBA season.
    :param season: Season in the format '2021-22'.
    :return: Start and end date as strings in 'YYYY-MM-DD'.
    """
    try:
        start_year, end_year = season.split('-')
        start_date = f"{start_year}-10-01"
        end_date = f"20{end_year}-08-31"
        return start_date, end_date
    except ValueError:
        raise ValueError("Invalid season format. Please use 'YYYY-YY', e.g., '2021-22'.")

@app.route('/')
def home():
    return jsonify({"message": "Welcome to the Player Stats API!"})

@app.route('/player/<string:player_name>/season/<string:season>', methods=['GET'])
def get_season_data(player_name, season):
    """
    API endpoint to get average stats of a player for a specific season.
    :param player_name: Name of the player.
    :param season: Season in the format 'YYYY-YY', e.g., '2021-22'.
    :return: JSON response with average stats for the season.
    """
    try:
        start_date, end_date = get_season_date_range(season)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    stats = get_average_stats_for_season(player_name, start_date, end_date)
    if not stats:
        return jsonify({"error": "No data found for the specified player and season."}), 404
    return jsonify(stats)

if __name__ == '__main__':
    app.run(debug=True)
