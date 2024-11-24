import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 設定瀏覽器選項
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # 若不需顯示瀏覽器畫面，可啟用此行
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

# 啟動 Chrome 瀏覽器
driver = webdriver.Chrome(options=options)
driver.get("https://www.nba.com/players")

player_names = []

# 每頁的處理
try:
    for _ in range(11):  # 假設一共有 11 頁
        # 等待玩家名稱出現
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "RosterRow_playerName__G28lg"))
        )
        
        # 抓取玩家名稱
        div_tags = driver.find_elements(By.CLASS_NAME, "RosterRow_playerName__G28lg")
        for div_tag in div_tags:
            p_tags = div_tag.find_elements(By.TAG_NAME, "p")
            player_name = ' '.join([p_tag.text for p_tag in p_tags])
            player_names.append(player_name)
        
        # 點擊下一頁按鈕
        next_page_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[title="Next Page Button"]'))
        )
        next_page_button.click()

except Exception as e:
    print("Error:", e)
finally:
    driver.quit()

# 輸出成json檔
with open('player_names.json', 'w') as jsonfile:
    json.dump(player_names, jsonfile)
print(player_names)
