CREATE DATABASE nba_database;
USE nba_database;
CREATE TABLE player_game_logs (
    season_id INT NOT NULL,                -- 賽季 ID
    player_id INT NOT NULL,                -- 球員 ID
    game_id INT NOT NULL,                  -- 比賽 ID
    game_date DATE NOT NULL,               -- 比賽日期
    matchup VARCHAR(50) NOT NULL,          -- 比賽對戰
    wl CHAR(1) NOT NULL,                   -- 勝負 (W/L)
    min INT,                               -- 出場時間
    fgm INT,                               -- 投籃命中數
    fga INT,                               -- 投籃出手數
    fg_pct FLOAT,                          -- 投籃命中率
    fg3m INT,                              -- 三分命中數
    fg3a INT,                              -- 三分出手數
    fg3_pct FLOAT,                         -- 三分命中率
    ftm INT,                               -- 罰球命中數
    fta INT,                               -- 罰球出手數
    ft_pct FLOAT,                          -- 罰球命中率
    oreb INT,                              -- 進攻籃板
    dreb INT,                              -- 防守籃板
    reb INT,                               -- 總籃板
    ast INT,                               -- 助攻
    stl INT,                               -- 抄截
    blk INT,                               -- 阻攻
    tov INT,                               -- 失誤
    pf INT,                                -- 犯規
    pts INT,                               -- 得分
    plus_minus INT,                        -- 場上效率
    video_available TINYINT(1),            -- 是否有視頻
    PRIMARY KEY (player_id, game_id)       -- 主鍵
);
CREATE TABLE team_history_data (
    team_id INT NOT NULL,                  -- 球隊 ID
    game_id INT NOT NULL,                  -- 比賽 ID
    game_date DATE,                        -- 比賽日期
    matchup VARCHAR(50),                   -- 比賽對戰
    wl CHAR(1),                            -- 勝負 (W/L)
    w FLOAT,                               -- 勝場
    l FLOAT,                               -- 負場
    w_pct FLOAT,                           -- 勝率
    min INT,                               -- 比賽時間
    fgm INT,                               -- 投籃命中數
    fga INT,                               -- 投籃出手數
    fg_pct FLOAT,                          -- 投籃命中率
    fg3m INT,                              -- 三分命中數
    fg3a INT,                              -- 三分出手數
    fg3_pct FLOAT,                         -- 三分命中率
    ftm INT,                               -- 罰球命中數
    fta INT,                               -- 罰球出手數
    ft_pct FLOAT,                          -- 罰球命中率
    oreb INT,                              -- 進攻籃板
    dreb INT,                              -- 防守籃板
    reb INT,                               -- 總籃板
    ast INT,                               -- 助攻
    stl INT,                               -- 抄截
    blk INT,                               -- 阻攻
    tov INT,                               -- 失誤
    pf INT,                                -- 犯規
    pts INT,                               -- 得分
    season VARCHAR(10),                    -- 賽季
    PRIMARY KEY (team_id, game_id)         -- 主鍵
);
CREATE TABLE team_standings (
    team_id INT NOT NULL,                  -- 球隊 ID
    season VARCHAR(10) NOT NULL,           -- 賽季
    team_name VARCHAR(50),                 -- 球隊名稱
    conference VARCHAR(10),                -- 所屬會議 (East/West)
    division VARCHAR(50),                  -- 所屬分區
    long_win_streak INT,                   -- 最長連勝
    long_loss_streak INT,                  -- 最長連敗
    playoff_rank INT,                      -- 季後賽排名
    division_rank INT,                     -- 分區排名
    conference_games_back FLOAT,           -- 與會議領先球隊勝場差
    PRIMARY KEY (team_id, season)          -- 主鍵
);
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
CREATE TABLE nba_teams (
    Team VARCHAR(255),
    Abbreviation VARCHAR(255),
    Team_ID INT
);
CREATE TABLE player_details (
    PERSON_ID INT PRIMARY KEY,
    DISPLAY_FIRST_LAST VARCHAR(100) NOT NULL,
    TEAM_NAME VARCHAR(100) NOT NULL,
    TEAM_ABBREVIATION VARCHAR(10) NOT NULL,
    JERSEY VARCHAR(10),
    HEIGHT VARCHAR(10),
    WEIGHT INT,
    POSITION VARCHAR(20)
);
-- 創建 forum_posts 表
CREATE TABLE forum_posts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    game_id VARCHAR(50) NOT NULL,
    user_id INT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (game_id) REFERENCES recent_games(game_id)
);

-- 創建 recent_games 表
CREATE TABLE recent_games (
    game_id VARCHAR(50) PRIMARY KEY,
    game_date DATE NOT NULL,
    home_team VARCHAR(100) NOT NULL,
    away_team VARCHAR(100) NOT NULL,
    home_score INT NOT NULL,
    away_score INT NOT NULL,
    game_status VARCHAR(50) NOT NULL,
    home_leader_name VARCHAR(100),
    home_leader_points INT,
    home_leader_rebounds INT,
    home_leader_assists INT,
    away_leader_name VARCHAR(100),
    away_leader_points INT,
    away_leader_rebounds INT,
    away_leader_assists INT
);

-- 創建 user_fav_team 表
CREATE TABLE user_fav_team (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    team_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (team_id) REFERENCES nba_teams(team_id)
);
