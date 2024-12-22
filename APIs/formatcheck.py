import pandas as pd

# 加載 CSV 文件
file_path = './all_players_game_logs_2019_to_now.csv'
player_game_logs_data = pd.read_csv(file_path)

# 轉換日期格式# 使用正確的日期格式轉換
player_game_logs_data['GAME_DATE'] = pd.to_datetime(
    player_game_logs_data['GAME_DATE'], 
    format='%b %d, %Y'
).dt.strftime('%Y-%m-%d')

# 保存修正後的文件
fixed_file_path = './all_players_game_logs_fixed.csv'
player_game_logs_data.to_csv(fixed_file_path, index=False)

print(f"已修正日期格式並保存為：{fixed_file_path}")
