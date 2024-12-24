import csv
from nba_api.stats.endpoints import CommonAllPlayers

def fetch_common_all_players():
    # Fetch players for the current season using nba_api
    common_players = CommonAllPlayers(is_only_current_season=1, league_id="00", season="2023-24")
    data = common_players.get_normalized_dict()
    return data

def save_players_to_csv():
    data = fetch_common_all_players()

    # Extract relevant data
    players = data["CommonAllPlayers"]

    filtered_players = []

    for player in players:
        # Ignore players without a team
        if player["GAMES_PLAYED_FLAG"] == "Y" and player["TEAM_NAME"]:
            player_data = {
                "PERSON_ID": player["PERSON_ID"],
                "DISPLAY_FIRST_LAST": player["DISPLAY_FIRST_LAST"],
                "TEAM_NAME": player["TEAM_NAME"],
                "TEAM_ABBREVIATION": player["TEAM_ABBREVIATION"],
                "GAMES_PLAYED_FLAG": player["GAMES_PLAYED_FLAG"]
            }
            filtered_players.append(player_data)
            print(f"Fetched Player: {player_data['DISPLAY_FIRST_LAST']}, Team: {player_data['TEAM_NAME']}")

    # Save to CSV
    with open("common_all_players.csv", "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["PERSON_ID", "DISPLAY_FIRST_LAST", "TEAM_NAME", "TEAM_ABBREVIATION", "GAMES_PLAYED_FLAG"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(filtered_players)

    print("CSV file 'common_all_players.csv' created successfully!")

# # SQL Table Definition
# sql_table_definition = """
# CREATE TABLE common_all_players (
#     PERSON_ID INT PRIMARY KEY,
#     DISPLAY_FIRST_LAST VARCHAR(100) NOT NULL,
#     TEAM_NAME VARCHAR(100) NOT NULL,
#     TEAM_ABBREVIATION VARCHAR(10) NOT NULL,
#     GAMES_PLAYED_FLAG CHAR(1) NOT NULL
# );
# """
# print("SQL Table Definition:")
# print(sql_table_definition)

# Run the script
if __name__ == "__main__":
    save_players_to_csv()
