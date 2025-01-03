from flask import Flask,request,render_template,redirect,session, jsonify 
import pymysql
from dotenv import load_dotenv
import os
from nba_api.live.nba.endpoints import scoreboard
from nba_api.live.nba.endpoints import boxscore
from datetime import timedelta
import requests
import hashlib
import re


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
    session.clear()  # 清除 Flask session
    session.modified = True  # 確保 session 狀態更新

    response = redirect('/login')
    response.set_cookie('session', '', expires=0)  # 手動清除 session cookie

    # 防止瀏覽器緩存
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'

    return response

# default
@app.route('/')
def default():
    return render_template('login.html')

# main page
@app.route('/main_page')
def main_page():
    if 'user' in session:
        print(session['user'])
        return render_template('main_page.html')
    else: return redirect('/login')

#------------------------login------------------------------------
##################################################################


#######################################################################
#------------------------Players_Home-----------------------------------


@app.route('/players', methods=['GET', 'POST'])
def players():
    # 建立資料庫連線
    conn = get_db_connection()
    cursor = conn.cursor()

    # 預設查詢所有球員
    sql = "SELECT * FROM player_details ORDER BY DISPLAY_FIRST_LAST"
    params = []

    if request.method == 'POST':
        query = request.form.get('query', '').strip()
        team = request.form.get('team', '').strip()
        position = request.form.get('position', '').strip()  # 取得 position 的值

        # 動態生成 SQL 和參數
        conditions = []
        if query:
            conditions.append("DISPLAY_FIRST_LAST LIKE %s")
            params.append(f"%{query}%")
        if team:
            conditions.append("TEAM_NAME = %s")
            params.append(team)
        if position:  # 添加 position 篩選條件
            conditions.append("POSITION = %s")
            params.append(position)

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
    stats = get_average_stats(player['DISPLAY_FIRST_LAST'], season=None, opponent_team=None)
    # 如果找不到球員資料，則返回 404 錯誤
    if player is None:
        return "Player not found", 404
    # 傳遞給模板並渲染

    if stats[0]['avg_points'] is None:
        return render_template('player_detail.html',player = player, stats = None)
    else:
        return render_template('player_detail.html',player = player, stats = stats)

# teams 
@app.route('/teams')
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

@app.route('/teams/<team_abb>', methods=['GET', 'POST'])
def team_detail(team_abb):
    #取得隊伍資料
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT Team_ID, Team, Abbreviation FROM nba_teams ORDER BY Team")
    teams = cursor.fetchall()
    cursor.execute('SELECT Team_ID, Team FROM nba_teams WHERE Abbreviation = %s', (team_abb,))
    team = cursor.fetchone() 
    cursor.execute('SELECT * FROM player_details WHERE TEAM_ABBREVIATION = %s ORDER BY DISPLAY_FIRST_LAST', (team_abb,))
    players = cursor.fetchall()
    is_favorite=False
    if 'user' in session:
        # 查詢用戶最愛球隊
        cursor.execute("""
            SELECT * FROM user_fav_team 
            JOIN users ON user_fav_team.user_id = users.user_id 
            WHERE users.username = %s AND user_fav_team.team_id = %s
        """, (session['user'], team['Team_ID']))
        is_favorite = cursor.fetchone() is not None
    cursor.close()
    conn.close()
    if team is None :
        return "Team not found", 404
    
    # 用戶選擇隊伍、賽季、排名賽季
    input_opponent = request.args.get('opponent', '').strip() or ''
    input_season = ''
    input_standing = ''
    selected_opponent = input_opponent if input_opponent else 'allteam'
    selected_season = 'alltime'
    standing_season = '23'
    if request.method == 'POST' :
        input_standing = request.form.get('standing_seasons', '').strip()
        if input_standing :
            standing_season = input_standing
        
        input_opponent = request.form.get('opponent', '').strip()
        if input_opponent :
            selected_opponent = input_opponent
        
        input_season = request.form.get('season', '').strip()
        if input_season :
            selected_season = input_season
    
    # 隊伍數據
    team_data = {
        "games_played" : 0,
        "wins" : 0,
        "losses" : 0,
        "point" : 0,
        "rebound" : 0,
        "assist" : 0,
        "steal" : 0,
        "block" : 0,
        "avg_win" : 0
    }

    # 取得隊伍數據(Api)
    api_url = "http://127.0.0.1:5001/api/teams/" + str(team['Team_ID']) + "/summary"
    if selected_season != "alltime" : 
        api_url = api_url + "?season=20" + selected_season + "-" + str(int(selected_season) + 1)
    response = requests.get(api_url)
    if (response.status_code == 200) :
        data = response.json()
        for game in data :
            if selected_opponent != "allteam" : 
                if game['opponent'] == selected_opponent :
                    team_data['games_played'] += game['games_played']
                    team_data['wins'] += int(game['wins'])
                    team_data['losses'] += int(game['losses'])
                    if game['avg_pts'] : team_data['point'] += float(game['avg_pts']) * float(game['games_played'])
                    if game['avg_reb'] : team_data['rebound'] += float(game['avg_reb']) * float(game['games_played'])
                    if game['avg_ast'] : team_data['assist'] += float(game['avg_ast']) * float(game['games_played'])
                    if game['avg_stl'] : team_data['steal'] += float(game['avg_stl']) * float(game['games_played'])
                    if game['avg_blk'] : team_data['block'] += float(game['avg_blk']) * float(game['games_played'])
            else :
                team_data['games_played'] += game['games_played']
                team_data['wins'] += int(game['wins'])
                team_data['losses'] += int(game['losses'])
                if game['avg_pts'] : team_data['point'] += float(game['avg_pts']) * float(game['games_played'])
                if game['avg_reb'] : team_data['rebound'] += float(game['avg_reb']) * float(game['games_played'])
                if game['avg_ast'] : team_data['assist'] += float(game['avg_ast']) * float(game['games_played'])
                if game['avg_stl'] : team_data['steal'] += float(game['avg_stl']) * float(game['games_played'])
                if game['avg_blk'] : team_data['block'] += float(game['avg_blk']) * float(game['games_played'])
        # summing the data
        if team_data['games_played'] != 0 :
            team_data['point'] = round(team_data['point'] / team_data['games_played'], 2)
            team_data['rebound'] = round(team_data['rebound'] / team_data['games_played'], 2)
            team_data['assist'] = round(team_data['assist'] / team_data['games_played'], 2)
            team_data['steal'] = round(team_data['steal'] / team_data['games_played'], 2)
            team_data['block'] = round(team_data['block'] / team_data['games_played'], 2)
            team_data['avg_win'] = round(team_data['wins'] / team_data['games_played'] * 100, 2)

    # team standing data
    conference = "Not found"
    division = "Not found"
    division_rank = 0 
    playoff_rank = 0
    conference_games_back = 0 
    long_win_streak = 0 
    long_loss_streak = 0 

    # team standing API
    filiter_season = "20" + standing_season + "-" + str(int(standing_season) + 1)
    standing_api_url = "http://127.0.0.1:5001/api/team/" + str(team['Team_ID']) + "/standing"
    standing_response = requests.get(standing_api_url)
    if (standing_response.status_code == 200) :
        standing_datas = standing_response.json()
        for data in standing_datas :
            if data['season'] == filiter_season :
                conference = data['conference']
                division = data['division']
                division_rank = data['division_rank']
                playoff_rank = data['playoff_rank']
                conference_games_back = data['conference_games_back']
                long_win_streak = data['long_win_streak']
                long_loss_streak = data['long_loss_streak']

    # return page
    return render_template(
        'team_detail.html', 
        teams = teams, 
        team_abb = team_abb, 
        team_name = team['Team'], 
        team_data = team_data, 
        players = players,
        selected_opponent = selected_opponent,
        selected_season = selected_season, 
        standing_season = standing_season,
        conference = conference, 
        division = division, 
        division_rank = division_rank, 
        playoff_rank = playoff_rank, 
        conference_games_back = conference_games_back, 
        long_win_streak = long_win_streak, 
        long_loss_streak = long_loss_streak,
        team_id = team['Team_ID'],
        is_favorite=is_favorite
        )

# Game Detail

#將 PT35M39.03S 格式轉換為只保留分鐘部分
def convert_playtime(playtime):
    match = re.match(r"PT(\d+)M", playtime)
    if match:
        return f"{match.group(1)} 分鐘"
    return "0 分鐘"

@app.route('/game_detail_page/<game_id>', methods=['GET', 'POST'])
def game_detail_page(game_id):
    try:
        # 使用 nba_api 獲取比賽詳細數據
        boxscore_data = boxscore.BoxScore(game_id).get_dict()
        game_data = boxscore_data.get("game", {})
        home_team = game_data.get("homeTeam", {}).get("teamName", "Unknown Home Team")
        away_team = game_data.get("awayTeam", {}).get("teamName", "Unknown Away Team")
        home_score = 0
        away_score = 0
        players = []

        for team_key in ["homeTeam", "awayTeam"]:
            team_data = game_data.get(team_key, {})
            team_name = team_data.get("teamName", "Unknown Team")
            for player in team_data.get("players", []):
                if player.get("played") == "1":
                    if team_name == home_team:
                        home_score += player.get("statistics", {}).get("points", 0)
                    else:
                        away_score += player.get("statistics", {}).get("points", 0)
                    players.append({
                        "name": player.get("name"),
                        "team": team_name,
                        "position": player.get("position"),
                        "minutes": convert_playtime(player.get("statistics", {}).get("minutes", "PT0M0S")),
                        "points": player.get("statistics", {}).get("points", 0),
                        "rebounds": player.get("statistics", {}).get("reboundsTotal", 0),
                        "assists": player.get("statistics", {}).get("assists", 0),
                        "steals": player.get("statistics", {}).get("steals", 0),
                        "blocks": player.get("statistics", {}).get("blocks", 0)
                    })

        # 查詢隊伍縮寫
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT Abbreviation 
            FROM nba_teams 
            WHERE Team LIKE %s
        """, (f"%{home_team}%",))
        home_team_abbreviation_row = cursor.fetchone()

        cursor.execute("""
            SELECT Abbreviation 
            FROM nba_teams 
            WHERE Team LIKE %s
        """, (f"%{away_team}%",))
        away_team_abbreviation_row = cursor.fetchone()

        home_team_abbreviation = home_team_abbreviation_row['Abbreviation'] if home_team_abbreviation_row else None
        away_team_abbreviation = away_team_abbreviation_row['Abbreviation'] if away_team_abbreviation_row else None

        if request.method == 'POST':
            user_name = session.get('user')
            cursor.execute("SELECT user_id FROM users WHERE users.username = %s", (user_name,))
            user_id = cursor.fetchone()
            content = request.form.get("comment")

            cursor.execute("""
                INSERT INTO forum_posts (game_id, user_id, content)
                VALUES (%s, %s, %s)
            """, (game_id, user_id['user_id'], content))
            conn.commit()

        # 從 forum_posts 表中獲取留言
        cursor.execute("""
            SELECT username, content 
            FROM forum_posts as fp
            JOIN users ON users.user_id = fp.user_id
            WHERE game_id = %s
            ORDER BY id DESC
        """, (game_id,))
        comments = cursor.fetchall()

        cursor.close()
        conn.close()

        # 渲染比賽詳細頁
        return render_template(
            'game_detail.html',
            game_id=game_id,
            home_team=home_team,
            away_team=away_team,
            home_team_score=home_score,
            away_team_score=away_score,
            players=players,
            comments=comments,
            home_team_abbreviation=home_team_abbreviation,
            away_team_abbreviation=away_team_abbreviation
        )
    except Exception as e:
        return render_template(
            'game_detail.html',
            game_id=game_id,
            home_team=home_team,
            away_team=away_team,
            players=players,
            home_team_abbreviation=None,
            away_team_abbreviation=None
        )



#######################################################################
#-----------------------team_data-------------------------------------

@app.route('/api/teams/<int:team_id>/summary', methods=['GET'])
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


    try:
        cursor.execute(query, params)
        results = cursor.fetchall()
    except Exception as e:
        print(f"Database error: {e}")
        raise
    finally:
        cursor.close()
        conn.close()
    print(results)
    
    return results

def get_average_stats_by_team(player_name, season=None, opponent_team=None):
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
        stats = get_average_stats_by_team(player_name, season=season, opponent_team=opponent_team)
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
#--------------------------------------論壇--------------------------------------
@app.route('/api/add_comment', methods=['POST'])
def add_comment():
    """
    API 用於新增比賽留言到 forum_posts 表
    """
    data = request.json
    game_id = data.get('game_id')  # 比賽 ID
    user_id = data.get('user_id')  # 使用者 ID
    content = data.get('content')  # 留言內容

    # 驗證請求參數
    if not game_id or not user_id or not content:
        return jsonify({"error": "Missing required fields (game_id, user_id, content)."}), 400

    try:
        # 建立資料庫連線
        conn = get_db_connection()
        cursor = conn.cursor()

        # 新增留言到 forum_posts 表
        cursor.execute("""
            INSERT INTO forum_posts (game_id, user_id, content)
            VALUES (%s, %s, %s)
        """, (game_id, user_id, content))
        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({"message": "Comment added successfully!"}), 201

    except Exception as e:
        print(f"Error adding comment: {e}")
        return jsonify({"error": "Failed to add comment."}), 500
#---------------------------------論壇--------------------------------------------
#######################################################################################
##############################################################################################
#--------------------------------------real_time_scoreboard--------------------------------------

def fetch_games():
    """
    使用 nba_api 的 ScoreBoard 類抓取當天比賽數據
    """
    try:
        score_board = scoreboard.ScoreBoard()
        games = score_board.games.get_dict()  # 獲取比賽數據字典
        return games
    except Exception as e:
        print(f"Error fetching today's games: {e}")
        return []

@app.route('/api/today_games', methods=['GET'])
def get_today_games():
    games = fetch_games()  # Fetch today's games
    conn = get_db_connection()
    cursor = conn.cursor()

    # 檢查 session 中的用戶名
    user_name = session.get('user')
    user_fav_team_ids = []

    if user_name:
        # 取得 user_id
        cursor.execute("""
            SELECT user_id
            FROM users
            WHERE username = %s
        """, (user_name,))
        user = cursor.fetchone()

        if user:
            user_id = user['user_id']

            # 查詢最愛球隊的 team_id
            cursor.execute("""
                SELECT team_id
                FROM user_fav_team
                WHERE user_id = %s
            """, (user_id,))
            user_fav_team_ids = [row['team_id'] for row in cursor.fetchall()]

    if not games:
        # If no games today, fetch the most recent game data for a specific date
        cursor.execute("""
            SELECT DISTINCT game_date 
            FROM recent_games 
            ORDER BY game_date DESC 
            LIMIT 1
        """)
        last_game_date = cursor.fetchone()

        if last_game_date:
            last_date = last_game_date['game_date']
            cursor.execute("""
                SELECT game_id, game_date, home_team, away_team, home_score, away_score, game_status,
                    home_leader_name, home_leader_points, home_leader_rebounds, home_leader_assists,
                    away_leader_name, away_leader_points, away_leader_rebounds, away_leader_assists
                FROM recent_games 
                WHERE game_date = %s
            """, (last_date,))
            last_games = cursor.fetchall()


            cursor.close()
            conn.close()

            if last_games:
                formatted_games = []
                for game in last_games:
                    formatted_games.append({
                        "game_id": game['game_id'],
                        "game_date": game['game_date'],
                        "home_team": game['home_team'],
                        "away_team": game['away_team'],
                        "home_score": game['home_score'],
                        "away_score": game['away_score'],
                        "game_status": game['game_status'],
                        "home_leader": {
                            "name": game['home_leader_name'],
                            "points": game['home_leader_points'],
                            "rebounds": game['home_leader_rebounds'],
                            "assists": game['home_leader_assists']
                        },
                        "away_leader": {
                            "name": game['away_leader_name'],
                            "points": game['away_leader_points'],
                            "rebounds": game['away_leader_rebounds'],
                            "assists": game['away_leader_assists']
                        },
                        "detail_url": f"/game_detail_page/{game['game_id']}"
                    })

                return jsonify({
                    "message": "今日無比賽，以下為最近一次有比賽的結果",
                    "games": formatted_games,
                }), 200
            else:
                return jsonify({"message": "今日無比賽，且無最近比賽數據", "games": []}), 200
        else:
            cursor.close()
            conn.close()
            return jsonify({"message": "今日無比賽，且無最近比賽數據", "games": []}), 200



    result = []
    for game in games:
        home_team = game['homeTeam']
        away_team = game['awayTeam']
        game_status = game['gameStatus']

        game_data = {
            "game_id": game['gameId'],
            "game_date": game['gameTimeUTC'],
            "home_team": f"{home_team['teamCity']} {home_team['teamName']}",
            "away_team": f"{away_team['teamCity']} {away_team['teamName']}",
            "home_score": home_team['score'],
            "away_score": away_team['score'],
            "game_status": game_status,
            "detail_url": f"/game_detail_page/{game['gameId']}"  # 加入跳轉詳細頁的連結
        }

        # Add game leaders if available
        if 'gameLeaders' in game and game_status != 1:
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

        # 根據 game_status 設置 message
        if game_status == 1:
            game_data["message"] = "Upcoming"
        elif game_status == 2:
            game_data["message"] = "Ongoing"
        elif game_status == 3:
            game_data["message"] = "Finished"

        result.append({
            **game_data,
            "is_favorite": home_team['teamId'] in user_fav_team_ids or away_team['teamId'] in user_fav_team_ids
        })

    # 將比賽按最愛球隊排序
    sorted_result = sorted(result, key=lambda x: x["is_favorite"], reverse=True)

    cursor.close()
    conn.close()
    return jsonify({
        "message": "今日比賽如下",
        "games": sorted_result  # 使用統一的鍵 "games"
    }), 200



def store_team_data(game, cursor):
    """
    將比賽數據存入 team_history_data 和 recent_games 表
    """
    try:
        home_team = game['homeTeam']
        away_team = game['awayTeam']

        # 儲存到 team_history_data
        cursor.execute("""
            INSERT INTO team_history_data (
                team_id, game_id, game_date, matchup, wl, pts
            ) VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE pts = VALUES(pts)
        """, (
            home_team['teamId'], game['gameId'], game['gameTimeUTC'],
            f"{home_team['teamName']} vs {away_team['teamName']}",
            "W" if home_team['score'] > away_team['score'] else "L",
            home_team['score']
        ))

        # 儲存到 recent_games
        cursor.execute("""
            INSERT INTO recent_games (
                game_id, game_date, home_team, away_team, home_score, away_score, game_status,
                home_leader_name, home_leader_points, home_leader_rebounds, home_leader_assists,
                away_leader_name, away_leader_points, away_leader_rebounds, away_leader_assists
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
                home_score = VALUES(home_score),
                away_score = VALUES(away_score),
                game_status = VALUES(game_status),
                home_leader_name = VALUES(home_leader_name),
                home_leader_points = VALUES(home_leader_points),
                home_leader_rebounds = VALUES(home_leader_rebounds),
                home_leader_assists = VALUES(home_leader_assists),
                away_leader_name = VALUES(away_leader_name),
                away_leader_points = VALUES(away_leader_points),
                away_leader_rebounds = VALUES(away_leader_rebounds),
                away_leader_assists = VALUES(away_leader_assists)
        """, (
            game['gameId'], game['gameTimeUTC'],
            f"{home_team['teamCity']} {home_team['teamName']}",
            f"{away_team['teamCity']} {away_team['teamName']}",
            home_team['score'], away_team['score'],
            game['gameStatusText'],
            # 添加主隊和客隊領袖數據，確保有數據或用預設值填充
            game['gameLeaders']['homeLeaders']['name'] if 'gameLeaders' in game else "N/A",
            game['gameLeaders']['homeLeaders']['points'] if 'gameLeaders' in game else 0,
            game['gameLeaders']['homeLeaders']['rebounds'] if 'gameLeaders' in game else 0,
            game['gameLeaders']['homeLeaders']['assists'] if 'gameLeaders' in game else 0,
            game['gameLeaders']['awayLeaders']['name'] if 'gameLeaders' in game else "N/A",
            game['gameLeaders']['awayLeaders']['points'] if 'gameLeaders' in game else 0,
            game['gameLeaders']['awayLeaders']['rebounds'] if 'gameLeaders' in game else 0,
            game['gameLeaders']['awayLeaders']['assists'] if 'gameLeaders' in game else 0
        ))

    except Exception as e:
        print(f"Error inserting team data: {e}")



##################-real_time_player_data#####################################################


@app.route("/get_players", methods=["GET"])
def get_players():
    game_id = request.args.get("game_id")
    if not game_id:
        return jsonify({"error": "Game ID is required"}), 400

    try:
        # 使用 nba_api 的 BoxScore 類別直接抓取資料
        boxscore_data = boxscore.BoxScore(game_id).get_dict()
    except Exception as e:
        return jsonify({"error": f"Failed to fetch data from nba_api: {str(e)}"}), 500

    try:
        game_data = boxscore_data.get("game", {})
        players = []

        # 初始化 home_team 和 away_team 的分數

        for team_key in ["homeTeam", "awayTeam"]:
            team_data = game_data.get(team_key, {})
            team_name = team_data.get("teamName", "Unknown Team")
            for player in team_data.get("players", []):
                # 只取「有上場」的球員
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

        return jsonify({
            "game_id": game_id,
            "players": players
        })

    except KeyError as e:
        return jsonify({"error": f"Data parsing error: {str(e)}"}), 500

    
#-------------------------------------------------------------------------------------------------------------------------
####################################################################################################################################



####################################################################################################################################
#---------------------------------------------------------------------------------------------------------------------------------

@app.route('/api/search_players', methods=['GET'])
def search_players():
    search_query = request.args.get('query', '').strip()
    team_filter = request.args.get('team', '').strip()

    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        query = "SELECT DISPLAY_FIRST_LAST FROM player_details WHERE DISPLAY_FIRST_LAST LIKE %s"
        params = [f"%{search_query}%"]
        
        if team_filter:
            query += " AND TEAM_NAME = %s"
            params.append(team_filter)
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        return jsonify([row['DISPLAY_FIRST_LAST'] for row in results])
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

#-------------------------------------------------------------------------------------------------------------------------------------------------
#######################################################################################################################################

@app.route('/api/favorite_team', methods=['POST', 'DELETE'])
def handle_favorite_team():
    if 'user' not in session:
        return jsonify({"message": "用戶未登入"}), 401

    # 取得 user_id
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT user_id FROM users WHERE username = %s
    """, (session['user'],))
    user = cursor.fetchone()

    if not user:
        cursor.close()
        conn.close()
        return jsonify({"message": "找不到使用者"}), 404

    user_id = user['user_id']
    data = request.get_json()
    team_id = data.get('team_id')

    if not team_id:
        return jsonify({"message": "缺少 team_id"}), 400

    if request.method == 'POST':
        # 確保只有一支最愛球隊
        cursor.execute("""
            SELECT * FROM user_fav_team WHERE user_id = %s
        """, (user_id,))
        existing_record = cursor.fetchone()

        if existing_record:
            # 更新最愛球隊
            cursor.execute("""
                UPDATE user_fav_team SET team_id = %s WHERE user_id = %s
            """, (team_id, user_id))
        else:
            # 新增最愛球隊
            cursor.execute("""
                INSERT INTO user_fav_team (user_id, team_id) VALUES (%s, %s)
            """, (user_id, team_id))

    elif request.method == 'DELETE':
        # 刪除最愛球隊
        cursor.execute("""
            DELETE FROM user_fav_team WHERE user_id = %s AND team_id = %s
        """, (user_id, team_id))

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "操作成功"}), 200


# run server
if __name__ == '__main__':
    app.run(debug=True,port=5001)
