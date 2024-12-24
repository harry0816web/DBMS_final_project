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
CREATE TABLE name_id_map (
    player_name VARCHAR(100) NOT NULL,
    player_id INT NOT NULL,
    PRIMARY KEY (player_id)
);
CREATE TABLE common_all_players (
    PERSON_ID INT PRIMARY KEY,
    DISPLAY_FIRST_LAST VARCHAR(100) NOT NULL,
    TEAM_NAME VARCHAR(100) NOT NULL,
    TEAM_ABBREVIATION VARCHAR(10) NOT NULL,
    GAMES_PLAYED_FLAG CHAR(1) NOT NULL
);