from flask import Flask,request,render_template,redirect,session, jsonify
import pymysql

# db setup
db = pymysql.connect(
    host="localhost",
    user="root",
    password="1234",
    database="nba_database"
)

# init flask
app = Flask(__name__,
            static_folder='static',
            static_url_path='/',
            template_folder='templates'
            )
app.secret_key = '1234567890'

# router
@app.route('/')
def index():return redirect('/login')
    
# test database
# user dictionary to store user data
user_data = [
    {'username':'test','password':'test'},
    {'username':'elle','password':'1114'}
]

##################################################################
#------------------------login---------------------------------
#
from flask import Flask, render_template, request, redirect, session
import pymysql
import hashlib

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# 資料庫配置
db = pymysql.connect(
    host="localhost",
    user="root",
    password="1234",
    database="nba_database"
)

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

        cursor = db.cursor()
        try:
            # 插入新用戶到資料庫
            query = """
                INSERT INTO users (username, email, password_hash) 
                VALUES (%s, %s, %s)
            """
            cursor.execute(query, (username, email, hashed_password))
            db.commit()
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

# 登入功能
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        username = request.form['username']
        password = request.form['password']
        hashed_password = hash_password(password)

        cursor = db.cursor(pymysql.cursors.DictCursor)
        try:
            query = "SELECT * FROM users WHERE username = %s AND password_hash = %s"
            cursor.execute(query, (username, hashed_password))
            user = cursor.fetchone()

            if user:
                session['user'] = username  # 設置 session
                print(f"User {username} logged in successfully.")
                return redirect('/')
            else:
                return render_template('login.html', login_error=True)
        except Exception as e:
            print(f"Database error: {e}")
            return render_template('login.html', login_error=True)
        finally:
            cursor.close()

# logout
@app.route('/logout')
def logout():
    session.pop('user', None)  # 清理 'user' 鍵
    return redirect('/login')



# main page
@app.route('/')
def main_page():
    return render_template('main_page.html')


#------------------------login------------------------------------
##################################################################


#######################################################################
#------------------------Players_Home-----------------------------------
@app.route('/players', methods=['GET', 'POST'])
def index():
    players = Player.query.order_by(Player.name).all()

    if request.method == 'POST':
        query = request.form.get('query', '').strip()
        team = request.form.get('team', '').strip()

        players = Player.query
        if query:
            players = players.filter(Player.name.ilike(f"%{query}%"))
        if team:
            players = players.filter(Player.team == team)

        players = players.order_by(Player.name).all()

    return render_template('index.html', players=players)


@app.route('/player/<int:player_id>')
def player_detail(player_id):
    player = Player.query.get_or_404(player_id)
    return render_template('player_detail.html', player=player)


@app.route('/team/<team_name>')
def team_detail(team_name):
    players = Player.query.filter_by(team=team_name).order_by(Player.name).all()
    return render_template('team_detail.html', team=team_name, players=players)



#######################################################################
#-----------------------team_data-------------------------------------

@app.route('/api/team/<int:team_id>/summary', methods=['GET'])
def get_team_summary(team_id):
    season = request.args.get('season')  # 可選參數：賽季
    cursor = db.cursor(pymysql.cursors.DictCursor)

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
            return jsonify({"message": "No data found for the given team and season"}), 404

        return jsonify(results)
    except Exception as e:
        print(f"Database error: {e}")
        return jsonify({"error": str(e)}), 500
    
#--------------------team_data-----------------------------------------------------------
#  #######################################################################################

#######################################################################
#-----------------------plaeyer_data-------------------------------------

@app.route('/api/team/<int:team_id>/standing', methods=['GET'])
def get_team_standing(team_id):
    season = request.args.get('season')  # 可選參數：賽季
    cursor = db.cursor(pymysql.cursors.DictCursor)

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
    
    #---------------------------------player_data--------------------------------------------
    #######################################################################################


# run server
if __name__ == '__main__':
    app.run(debug=True,port=5001)

