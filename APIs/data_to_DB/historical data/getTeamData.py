import pandas as pd
from nba_api.stats.endpoints import teamgamelog, leaguestandings
from datetime import datetime

# 定義抓取球隊數據的年份範圍
START_YEAR = 2018  # 5年前的賽季開始年份
END_YEAR = datetime.now().year  # 當前年份

# 用來存放所有球隊數據的 DataFrame
team_data = []

# 抓取歷史數據 (5年內的數據 + 當前賽季數據)
for year in range(START_YEAR, END_YEAR + 1):
    season = f"{year}-{str(year + 1)[-2:]}"  # 賽季格式為 "2018-19"
    print(f"Fetching data for season {season}...")

    # 使用 teamgamelog 抓取每支球隊的數據
    try:
        for team_id in range(1610612737, 1610612767):  # NBA球隊ID範圍
            gamelogs = teamgamelog.TeamGameLog(season=season, season_type_all_star="Regular Season", team_id=team_id).get_data_frames()[0]
            gamelogs["SEASON"] = season  # 添加賽季欄位

            # 只保留已完成的比賽
            gamelogs = gamelogs[gamelogs["WL"].notnull()]

            # 如果是當前賽季，排除季後賽數據
            if season == f"{END_YEAR - 1}-{str(END_YEAR)[-2:]}":
                gamelogs = gamelogs[gamelogs["SEASON_TYPE"] != "Playoffs"]

            # 將日期轉換為標準格式
            gamelogs["GAME_DATE"] = pd.to_datetime(gamelogs["GAME_DATE"], format="%b %d, %Y", errors="coerce")

            team_data.append(gamelogs)
    except Exception as e:
        print(f"Error fetching data for season {season}, team_id {team_id}: {e}")

# 合併數據
all_team_data = pd.concat(team_data, ignore_index=True)

# 保存到 CSV
all_team_data.to_csv("team_history_data.csv", index=False)
print("歷史數據已保存到 team_history_data.csv")

# 抓取本賽季的 standings
print("Fetching current season standings...")
standings = leaguestandings.LeagueStandings().get_data_frames()[0]
standings.to_csv("current_standings.csv", index=False)
print("當前賽季 standings 已保存到 current_standings.csv")
