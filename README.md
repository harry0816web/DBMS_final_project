# 資料庫期末專案：NBA 資料分析與管理平台

## 專案簡介
本專案為一個基於 Flask 的 NBA 資料管理與分析系統。使用者可以透過此系統查詢 NBA 球隊和球員的歷史數據、對戰紀錄、排名資訊，並透過帳號系統進行個人化管理。

---

## 功能
1. **使用者註冊與登入**
   - 使用者可以註冊帳號並登入系統。
   - 提供安全的密碼加密功能。
2. **球隊數據查詢**
   - 查看指定球隊的歷史比賽記錄，包含比分、籃板、助攻等數據。
   - 按賽季查詢球隊的對戰數據，支持按對手分組統計勝場、負場及勝率。
3. **球隊排名資訊**
   - 獲取指定球隊在分區和聯盟中的排名資訊，包含連勝記錄、連敗記錄和與分區第一的勝場差距。
4. **資料可視化**
   - 提供比賽數據的圖表展示（未來可擴展）。

---

## 系統架構
### 技術棧
- **後端**：Flask + Python
- **資料庫**：MySQL
- **前端**：HTML + CSS + JavaScript
- **版本控制**：Git + GitHub

### 資料庫設計
1. **`users` 表**：
   - 儲存使用者的帳號、電子郵件及加密密碼。
2. **`team_history_data` 表**：
   - 儲存球隊的歷史比賽數據，包括比分、籃板、助攻等。
3. **`team_standings` 表**：
   - 儲存球隊在分區和聯盟中的排名資訊。

---

## 安裝與使用
### 環境需求
- Python 3.10+
- MySQL 8.0+
- pip 套件管理工具

### 安裝步驟
1. 克隆專案至本地：
   ```bash
   git clone https://github.com/harry0816web/DBMS_final_project.git
   cd DBMS_final_project
   ```

2. 建立虛擬環境並安裝依賴：
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows 使用 venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. 配置 MySQL 資料庫：
   - 創建資料庫：
     ```sql
     CREATE DATABASE nba_database;
     ```
   - 匯入資料表結構：
     ```bash
     mysql -u root -p nba_database < schema.sql
     ```

4. 啟動伺服器：
   ```bash
   python app.py
   ```
   開啟瀏覽器並訪問 `http://127.0.0.1:5000`。

---

## API 文件
### 球隊數據查詢
- **路由**：`/api/team/<int:team_id>/summary`
- **方法**：GET
- **參數**：
  - `season`（可選）：指定查詢的賽季。
- **回應範例**：
  ```json
  [
      {
          "opponent": "BKN",
          "season": "2018-19",
          "games_played": 5,
          "wins": 3,
          "losses": 2,
          "avg_pts": 112.5,
          "win_percentage": 60.0
      }
  ]
  ```

### 球隊排名資訊查詢
- **路由**：`/api/team/<int:team_id>/standing`
- **方法**：GET
- **參數**：
  - `season`（可選）：指定查詢的賽季。
- **回應範例**：
  ```json
  {
      "team_name": "Atlanta Hawks",
      "season": "2018-19",
      "conference": "East",
      "playoff_rank": 7,
      "division_rank": 3
  }
  ```

---

## 未來擴展
- 添加圖表展示數據，增強使用者體驗。
- 支持更多自動化功能，如每日比賽數據自動同步。
- 增加球員詳細數據查詢功能。

---

## 貢獻者
- **開發者**：Harry, Richao, Tuna, Weikai, Sblack

歡迎對專案進行改進或提交建議！

