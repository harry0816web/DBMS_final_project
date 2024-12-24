from flask import Flask,request,render_template,redirect,session, jsonify 
import pymysql
from dotenv import load_dotenv
import os
from nba_api.live.nba.endpoints import scoreboard
from datetime import timedelta
import requests
import signal
import hashlib

# 加載 .env 文件
load_dotenv()

# db setuop
def get_db_connection(): 
    return pymysql.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        port=int(os.getenv("DB_PORT", 3306)),
        autocommit=True,
        cursorclass=pymysql.cursors.DictCursor
    )

# init flask
app = Flask(__name__,
            static_folder='static',
            static_url_path='/',
            template_folder='templates'
            )
app.secret_key = '1234567890'
app.permanent_session_lifetime = timedelta(minutes=30)
    
# test database
# user dictionary to store user data
user_data = [
    {'username':'test','password':'test'},
    {'username':'elle','password':'1114'}
]
##################################################################
# Table set

##################################################################
#------------------------login---------------------------------

# Hash 密碼的輔助函式
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# 註冊功能
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm-password']

        # 檢查密碼是否匹配
        if password != confirm_password:
            return render_template('register.html', error="密碼不一致，請重新輸入。")

        hashed_password = hash_password(password)

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # 插入新用戶到資料庫
            query = """
                INSERT INTO users (username, email, password_hash) 
                VALUES (%s, %s, %s)
            """
            cursor.execute(query, (username, email, hashed_password))
            conn.commit()
            print(f"User {username} registered successfully.")
            return redirect('/login')
        except pymysql.IntegrityError as e:
            # 處理重複的 username 或 email
            if "Duplicate entry" in str(e):
                return render_template('register.html', error="用戶名或電子郵件已存在，請使用其他資料。")
            else:
                return render_template('register.html', error="資料庫錯誤，請稍後再試。")
        except Exception as e:
            print(f"Database error: {e}")
            return render_template('register.html', error="未知錯誤，請稍後再試。")
        finally:
            cursor.close()
            conn.close()

# 登入功能
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        username = request.form['username']
        password = request.form['password']
        hashed_password = hash_password(password)

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            query = "SELECT * FROM users WHERE username = %s AND password_hash = %s"
            cursor.execute(query, (username, hashed_password))
            user = cursor.fetchone()

            if user:
                session['user'] = username  # 設置 session
                print(f"User {username} logged in successfully.")
                return redirect('/main_page')
            else:
                return render_template('login.html', login_error=True,error = "帳號或密碼錯誤，請重新輸入")
        except Exception as e:
            print(f"Database error: {e}")
            return render_template('login.html', login_error=True)
        finally:
            cursor.close()
            conn.close()

# logout
@app.route('/logout')
def logout():
    session.pop('user', None)  # 清理 'user' 鍵
    return redirect('/login')

# main page
@app.route('/')
def main_page():
    return render_template('main_page.html')

# member main page
@app.route('/main_page')
def member_main_page():
    return render_template('member_main_page.html')

# teams 
@app.route('/teams', methods=['GET'])
def teams_page():
    conn = get_db_connection()
    cursor = conn.cursor()

    # 獲取所有隊伍的列表
    try:
        cursor.execute("SELECT Team_ID, Team, Abbreviation FROM nba_teams ORDER BY Team")
        teams = cursor.fetchall()

        # 渲染HTML頁面
        return render_template('teams.html', teams=teams)
    except Exception as e:
        print(f"Database error: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

#------------------------login------------------------------------
##################################################################


#######################################################################
#------------------------Players_Home-----------------------------------


@app.route('/players', methods=['GET', 'POST'])
def players():
    # 建立資料庫連線
    conn = get_db_connection()
    cursor = conn.cursor()  # dictionary=True 返回字典形式

    # 預設查詢所有球員
    sql = "SELECT * FROM player_details ORDER BY DISPLAY_FIRST_LAST"
    params = []

    if request.method == 'POST':
        query = request.form.get('query', '').strip()
        team = request.form.get('team', '').strip()

        # 動態生成 SQL 和參數
        conditions = []
        if query:
            conditions.append("DISPLAY_FIRST_LAST LIKE %s")
            params.append(f"%{query}%")
        if team:
            conditions.append("team_name = %s")
            params.append(team)

        if conditions:
            sql = f"SELECT * FROM player_details WHERE {' AND '.join(conditions)} ORDER BY DISPLAY_FIRST_LAST"

    # 執行查詢
    cursor.execute(sql, params)
    players = cursor.fetchall()

    # 關閉連線
    cursor.close()
    conn.close()

    # 渲染模板
    
    return render_template('players.html', players=players)

@app.route('/player/<int:player_id>')
def player_detail(player_id):
    # 取得資料庫連接與 cursor
    conn = get_db_connection()
    cursor = conn.cursor()

    # 查詢資料
    cursor.execute('SELECT * FROM player_details WHERE PERSON_ID = %s', (player_id,))
    player = cursor.fetchone()  # 取得單一結果

    # 關閉資料庫連接
    cursor.close()
    conn.close()

    # 如果找不到球員資料，則返回 404 錯誤
    if player is None:
        return "Player not found", 404

    # 傳遞給模板並渲染
    return render_template('player_detail.html', player=player)





#######################################################################
#-----------------------team_data-------------------------------------

@app.route('/team/<team_name>')
def team_detail(team_name):
    players = Player.query.filter_by(team=team_name).order_by(Player.name).all()
    return render_template('team_detail.html', team=team_name, players=players)

@app.route('/api/team/<int:team_id>/summary', methods=['GET'])
def get_team_summary(team_id):
    season = request.args.get('season')  # 可選參數：賽季
    opponent = request.args.get('opponent')  # 可選參數：對手隊伍名稱
    conn = get_db_connection()
    cursor = conn.cursor()

    # 查詢 team_history_data 表，合併主客場數據並統計
    query = """
        SELECT 
            SUBSTRING_INDEX(matchup, ' ', -1) AS opponent,  -- 提取對手球隊名稱
            season,
            COUNT(*) AS games_played,
            SUM(CASE WHEN wl = 'W' THEN 1 ELSE 0 END) AS wins,
            SUM(CASE WHEN wl = 'L' THEN 1 ELSE 0 END) AS losses,
            AVG(pts) AS avg_pts,
            AVG(reb) AS avg_reb,
            AVG(ast) AS avg_ast,
            AVG(stl) AS avg_stl,
            AVG(blk) AS avg_blk,
            ROUND(SUM(CASE WHEN wl = 'W' THEN 1 ELSE 0 END) / COUNT(*) * 100, 2) AS win_percentage
        FROM team_history_data
        WHERE team_id = %s
    """
    params = [team_id]
    
    # 如果指定了賽季，添加篩選條件
    if season:
        query += " AND season LIKE %s"
        params.append(f"%{season}%")
    
    # 如果指定了對手隊伍，使用 LIKE 篩選
    if opponent:
        query += " AND SUBSTRING_INDEX(matchup, ' ', -1) LIKE CONCAT('%', %s, '%')"
        params.append(opponent)

    query += """
        GROUP BY opponent, season
        ORDER BY season, opponent
    """
    
    try:
        # 執行查詢
        cursor.execute(query, params)
        results = cursor.fetchall()

        # 如果無數據返回 404
        if not results:
            return jsonify({"message": "No data found for the given team, season, or opponent"}), 404

        return jsonify(results)
    except Exception as e:
        print(f"Database error: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

    
#--------------------team_data-----------------------------------------------------------
#  #######################################################################################

#####################################################################################
#--------------------------team_standing-------------------------------------------------

@app.route('/api/team/<int:team_id>/standing', methods=['GET'])
def get_team_standing(team_id):
    season = request.args.get('season')  # 可選參數：賽季
    conn = get_db_connection()
    cursor = conn.cursor()

    # 查詢 team_standings 表
    query = """
        SELECT 
            team_name,
            season,
            conference,
            division,
            long_win_streak,
            long_loss_streak,
            playoff_rank,
            division_rank,
            conference_games_back
        FROM team_standings
        WHERE team_id = %s
    """
    params = [team_id]

    # 如果指定了賽季，添加篩選條件
    if season:
        query += " AND season LIKE %s"
        params.append(f"%{season}%")
    
    try:
        # 執行查詢
        cursor.execute(query, params)
        results = cursor.fetchall()

        # 如果無數據返回 404
        if not results:
            return jsonify({"message": "No standings found for the given team and season"}), 404

        return jsonify(results)
    except Exception as e:
        print(f"Database error: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()
    
#----------------------------------------------------------------------------------------------
######################################################################################################

#######################################################################
#-----------------------player_data-------------------------------------

def get_average_stats(player_name, season=None, opponent_team=None):
    """
    Fetch average stats for a player against all other teams or a specific opponent.
    :param player_name: Name of the player.
    :param season: Optional parameter for the season in the format 'YYYY-YY', e.g., '2021-22'.
    :param opponent_team: Optional parameter for filtering by opponent team name.
    :return: Average stats grouped by opponent team.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

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
        JOIN player_details AS pd ON pg.player_id = pd.PERSON_ID
        JOIN nba_teams AS nt ON pg.matchup LIKE CONCAT('%%', nt.Abbreviation, '%%')
        WHERE pd.DISPLAY_FIRST_LAST = %s
    """
    params = [player_name]

    # 如果指定了賽季，添加篩選條件
    if season:
        try:
            start_year, end_year = season.split('-')
            start_date = f"{start_year}-10-01"
            end_date = f"20{end_year}-08-31"
            query += " AND pg.game_date BETWEEN %s AND %s"
            params.extend([start_date, end_date])
        except ValueError:
            raise ValueError("Invalid season format. Please use 'YYYY-YY', e.g., '2021-22'.")

    # 如果指定了對手隊伍，使用 LIKE 篩選
    if opponent_team:
        query += " AND nt.Team LIKE CONCAT('%', %s, '%')"
        params.append(opponent_team)

    query += " GROUP BY nt.Team"

    try:
        cursor.execute(query, params)
        results = cursor.fetchall()
    except Exception as e:
        print(f"Database error: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

    return results



@app.route('/api/player/<string:player_name>/against_all_teams', methods=['GET'])
def get_avg_stats_against_all_teams(player_name):
    # 檢查並清理 player_name
    player_name = player_name.replace("'", "''")  # 防止單引號導致 SQL 問題
    season = request.args.get('season')  # Optional parameter: season (e.g., '2021-22')
    opponent_team = request.args.get('opponent_team')  # Optional parameter: opponent team name

    try:
        stats = get_average_stats(player_name, season=season, opponent_team=opponent_team)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400  # Invalid season format

    if not stats:
        message = "No data found for the specified player"
        if season:
            message += f" in season {season}"
        if opponent_team:
            message += f" against {opponent_team}"
        return jsonify({"error": message}), 404

    return jsonify(stats)
    
#---------------------------------player_data--------------------------------------------
#######################################################################################

##############################################################################################
#--------------------------------------real_time_scoreboard--------------------------------------

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

#---------------------------------------------------------------------------------------------------------------
#####################################################################################################################

#####################################################################################################################
#--------------------------------real_time_player_data-------------------------------------------------------------------

@app.route("/get_players", methods=["GET"])
def get_players():
    NBA_BOX_SCORE_URL = "https://cdn.nba.com/static/json/liveData/boxscore/boxscore_{game_id}.json"

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
    
#-------------------------------------------------------------------------------------------------------------------------
####################################################################################################################################


# run server
if __name__ == '__main__':
    app.run(debug=True,port=5001)

