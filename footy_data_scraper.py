import config
import pandas as pd 
import soccerdata as sd
import time
from pathlib import Path

# Use the below code to fetch football data for a specific league and season using the soccerdata library. 
# The data will be saved as a CSV file in the specified output directory.

class FootyData:
    def __init__(self, leagues: str, seasons: str):
        self.leagues = leagues
        self.seasons = seasons
        self.footy_data_dir = Path(config.config['filepaths']['data_dir'])
        self.understat = sd.Understat(leagues=self.leagues, seasons=self.seasons)

    def fetch_data(self, understat: sd.Understat):
        """
        Fetches football data for the specified league and season.
        """
        try:
            player_stats = understat.read_player_season_stats()
            print(f"Player data fetched successfully for {self.leagues} {self.seasons}.")
            player_stats.to_csv(f"{self.footy_data_dir}/{self.leagues.replace(' ', '_')}_{self.seasons.replace('/', '-')}_player_stats.csv", index=True)
            return player_stats
        except Exception as e:
            print(f"An error occurred while fetching data: {e}")
            return None
        
    def get_dataframe(self, player_stats) -> pd.DataFrame:
        """
        Returns the fetched data as a pandas DataFrame.
        """
        if player_stats is not None:
            return pd.DataFrame(player_stats)
        else:
            print("No data available. Please fetch data first.")
            return pd.DataFrame()

def main():
    leagues = 'ENG-Premier League'  # Possible values: 'ENG-Premier League', 'ESP-La Liga', 'ITA-Serie A', 'GER-Bundesliga', 'FRA-Ligue 1' Change for other leagues as needed.
    seasons = '2023/2024'  # Example season

    print(f"Fetching data for {leagues} {seasons}...")
    print(f"This may take a few moments, please wait..., querying Understat for data...query started at: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}")
    footy_data = FootyData(leagues, seasons)
    player_stats = footy_data.fetch_data(footy_data.understat)
    df = footy_data.get_dataframe(player_stats)


    if not df.empty:
        print(df.head())
        print(f"query completed at: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}")
    else:
        print("No data to display.")

if __name__ == "__main__":
    main()