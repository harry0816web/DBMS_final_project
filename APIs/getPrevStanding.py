import time
import pandas as pd
from nba_api.stats.endpoints import leaguestandings
from nba_api.stats.static import teams
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_current_season():
    """Determines the current NBA season based on the current date."""
    today = datetime.today()
    year = today.year
    month = today.month
    if month >= 10:  # NBA season starts in October
        season_start = year
        season_end = year + 1
    else:
        season_start = year - 1
        season_end = year
    return f"{season_start}-{str(season_end)[-2:]}"

def get_cavaliers_standings():
    # Define the seasons of interest dynamically
    current_season = get_current_season()
    seasons = [
        '2020-21',
        '2021-22',
        '2022-23',
        current_season  # Automatically include the current season
    ]
    
    cavaliers_data = []
    
    # Retrieve the TeamID for Cleveland Cavaliers dynamically
    all_teams = teams.get_teams()
    cavaliers = next((team for team in all_teams if team['full_name'] == 'Cleveland Cavaliers'), None)
    
    if not cavaliers:
        logging.error("Cleveland Cavaliers team data not found.")
        return
    
    cavaliers_id = cavaliers['id']
    
    for season in seasons:
        try:
            logging.info(f"Fetching standings for the {season} Regular Season...")
            standings = leaguestandings.LeagueStandings(
                league_id='00',                # NBA LeagueID
                season=season,                 # Season in 'YYYY-YY' format
                season_type='Regular Season'   # Regular Season standings
            )
            standings_df = standings.get_data_frames()[0]
            
            # Log available columns for verification
            logging.debug(f"Columns available: {standings_df.columns.tolist()}")
    
            # Filter for Cleveland Cavaliers using the correct 'TeamID'
            cavaliers_standing = standings_df[standings_df['TeamID'] == cavaliers_id]
            
            if not cavaliers_standing.empty:
                cavaliers_info = cavaliers_standing.iloc[0].to_dict()
                cavaliers_data.append(cavaliers_info)
                logging.info(f"Retrieved standings for {season}")
            else:
                logging.warning(f"Cleveland Cavaliers not found in standings for {season}")
            
            # Respect API rate limits
            time.sleep(1)
        
        except KeyError as ke:
            logging.error(f"KeyError for the {season} season: {ke}. Please check the column names.")
        except Exception as e:
            logging.error(f"An error occurred for the {season} season: {e}")
    
    # Convert the list of dictionaries to a DataFrame
    if cavaliers_data:
        standings_df_final = pd.DataFrame(cavaliers_data)
        logging.info("\nCleveland Cavaliers Regular Season Standings (2020-21 to Present):\n")
        # Select and rename columns for clarity
        standings_selected = standings_df_final[['SeasonID', 'WINS', 'LOSSES', 'WinPCT', 'PlayoffRank', 'DivisionRank']]
        print(standings_selected)
        
        # Optional: Save to CSV
        standings_df_final.to_csv('cavaliers_regular_season_standings_2020_to_present.csv', index=False)
        logging.info("Standings have been saved to 'cavaliers_regular_season_standings_2020_to_present.csv'")
    else:
        logging.warning("No standings data available to display.")

if __name__ == "__main__":
    get_cavaliers_standings()