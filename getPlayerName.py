import requests
import json
from bs4 import BeautifulSoup

# 網頁 URL
url = 'https://basketball.realgm.com/nba/players'  # 將此替換為你想要抓取的網頁網址

# 發送 GET 請求並取得網頁內容
response = requests.get(url)

# 檢查請求是否成功
if response.status_code == 200:
    # 使用 BeautifulSoup 解析 HTML
    # soup => html內容
    soup = BeautifulSoup(response.text, 'html.parser')

    # 分析HTML內容
    # 尋找所有符合條件的 <td> 標籤
    td_tags = soup.find_all('td', {'data-th': 'Player'})

    # 提取每個 <td> 中的 <a> 標籤的文字內容和 href 屬性
    player_names = []
    for td_tag in td_tags:
        a_tag = td_tag.find('a')
        if a_tag:
            player_name = a_tag.text
            player_names.append(player_name)
    # 輸出成json檔
    with open('player_names.json', 'w') as jsonfile:
        json.dump(player_names, jsonfile)
else:
    print("Failed to retrieve the page. Status code:", response.status_code)
