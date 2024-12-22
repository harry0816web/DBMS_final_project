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
