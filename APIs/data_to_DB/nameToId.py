import json
import pandas as pd

def convert_json_to_csv(input_json_file: str, output_csv_file: str):
    """
    將 JSON 文件轉換為 CSV 文件
    """
    # 讀取 JSON 文件
    with open(input_json_file, 'r') as file:
        data = json.load(file)
    
    # 將 JSON 格式轉換為 DataFrame
    df = pd.DataFrame(list(data.items()), columns=['PlayerName', 'PlayerID'])
    
    # 保存為 CSV 文件
    df.to_csv(output_csv_file, index=False)
    print(f"JSON 文件已成功轉換為 CSV 文件，保存為: {output_csv_file}")

# Example usage
input_json_file = "player_name_id_map.json"  # 輸入 JSON 文件
output_csv_file = "player_name_id_map.csv"   # 輸出 CSV 文件

convert_json_to_csv(input_json_file, output_csv_file)
