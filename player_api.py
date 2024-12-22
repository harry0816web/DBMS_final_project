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

def get_average_stats_against_teams(player_name):
    """
    Fetch average stats for a player against all other teams.
    :param player_name: Name of the player.
    :return: Average stats grouped by opponent team.
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT 
        nt.Team AS opponent_team,
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
    JOIN nba_teams AS nt ON pg.matchup LIKE CONCAT('%', nt.Abbreviation, '%')
    WHERE nm.player_name = %s
    GROUP BY nt.Team
    """

    cursor.execute(query, (player_name,))
    results = cursor.fetchall()

    cursor.close()
    conn.close()

    return results

@app.route('/')
def home():
    return jsonify({"message": "Welcome to the Player vs Teams Stats API!"})

@app.route('/player/<string:player_name>/against_all_teams', methods=['GET'])
def get_avg_stats_against_all_teams(player_name):
    """
    API endpoint to get average stats of a player against all teams.
    :param player_name: Name of the player.
    :return: JSON response with average stats grouped by team.
    """
    stats = get_average_stats_against_teams(player_name)
    if not stats:
        return jsonify({"error": "No data found for the specified player"}), 404
    return jsonify(stats)

if __name__ == '__main__':
    app.run(debug=True)
