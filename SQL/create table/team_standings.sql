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
