import pandas as pd

# 加載抓取到的球員數據文件
file_path = "all_players_game_logs_2019_to_2025.csv"  # 替換為實際的文件路徑
data = pd.read_csv(file_path)

# 將 GAME_DATE 字段轉換為標準日期格式 YYYY-MM-DD
data['GAME_DATE'] = pd.to_datetime(data['GAME_DATE'], format='%b %d, %Y').dt.strftime('%Y-%m-%d')

# 保存處理後的數據
output_path = "player_game_logs.csv"
data.to_csv(output_path, index=False)

print(f"已處理日期格式並保存為新文件：{output_path}")
