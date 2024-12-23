from nba_api.stats.endpoints import PlayerGameLog
from nba_api.stats.static import players
import pandas as pd
import time
import json

def get_player_id(player_name: str) -> int:
    """
    根據球員名字取得球員ID
    """
    player_dict = players.find_players_by_full_name(player_name)
    if not player_dict:
        raise ValueError(f"找不到球員: {player_name}")
    return player_dict[0]['id']

def fetch_player_data(player_id: int, seasons: list) -> pd.DataFrame:
    """
    抓取多個賽季的玩家比賽數據
    """
    all_games = pd.DataFrame()
    for season in seasons:
        print(f"Fetching data for season: {season}")
        try:
            game_log = PlayerGameLog(
                player_id=player_id,
                season=season,
                season_type_all_star='Regular Season'
            )
            game_log_df = game_log.get_data_frames()[0]
            all_games = pd.concat([all_games, game_log_df], ignore_index=True)
            # 延遲以避免API請求限制
            time.sleep(0.6)
        except Exception as e:
            print(f"Error fetching data for season {season}: {e}")
    return all_games

def main():
    with open('player_names.json', 'r') as jsonfile:
        player_names = json.load(jsonfile)
    
    # 設定賽季範圍
    seasons = ['2019-20', '2020-21', '2021-22', '2022-23', '2023-24', '2024-25']
    
    all_data = pd.DataFrame()
    for player_name in player_names:
        #若找不到球員ID，則跳過
        try:
            player_id = get_player_id(player_name)
            print(f"{player_name} 的球員ID: {player_id}")
            
            player_data = fetch_player_data(player_id, seasons)
            
            # 保存數據至總數據集中
            all_data = pd.concat([all_data, player_data], ignore_index=True)
            print(f"{player_name} 的數據已添加到總數據集中。")
        except Exception as e:
            print(f"Error fetching data for player {player_name}: {e}")
    
    # 保存所有數據至CSV
    all_data.to_csv("all_players_game_logs_2019_to_2025.csv", index=False)
    print("所有數據已保存至 all_players_game_logs_2019_to_2025.csv")

if __name__ == "__main__":
    main()
