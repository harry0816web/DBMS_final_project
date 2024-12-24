import requests
from datetime import datetime

def get_todays_games():
    # API endpoint
    url = "https://cdn.nba.com/static/json/liveData/scoreboard/todaysScoreboard_00.json"
    
    try:
        # Make API request
        response = requests.get(url)
        data = response.json()
        
        # Get all games for today
        games = data['scoreboard']['games']
        
        # If no games today
        if not games:
            print("No games today")
            return
        
        # Print all games
        print(f"NBA Games for {datetime.now().strftime('%Y-%m-%d')}:\n")
        
        for game in games:
            home_team = game['homeTeam']
            away_team = game['awayTeam']
            
            print(f"{away_team['teamCity']} {away_team['teamName']} ({away_team['wins']}-{away_team['losses']}) "
                  f"{away_team['score']} - "
                  f"{home_team['score']} "
                  f"{home_team['teamCity']} {home_team['teamName']} ({home_team['wins']}-{home_team['losses']})")
            print(f"Status: {game['gameStatusText']}")
            
            # Print game leaders if game has started/finished
            if 'gameLeaders' in game and game['gameStatus'] != 1:  # 1 is pre-game status
                home_leader = game['gameLeaders']['homeLeaders']
                away_leader = game['gameLeaders']['awayLeaders']
                
                print("\nGame Leaders:")
                print(f"{away_team['teamTricode']}: {away_leader['name']} - "
                      f"{away_leader['points']}pts, {away_leader['rebounds']}reb, {away_leader['assists']}ast")
                print(f"{home_team['teamTricode']}: {home_leader['name']} - "
                      f"{home_leader['points']}pts, {home_leader['rebounds']}reb, {home_leader['assists']}ast")
            print("\n" + "-"*50 + "\n")
            
    except Exception as e:
        print(f"Error fetching data: {str(e)}")

# Execute the function
get_todays_games()