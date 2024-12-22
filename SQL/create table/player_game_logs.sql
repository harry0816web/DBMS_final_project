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
