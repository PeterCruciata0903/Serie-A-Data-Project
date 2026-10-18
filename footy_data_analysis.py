import config
import logging
import pandas as pd
import numpy as np
from pathlib import Path

class FootyDataAnalysis:
    def __init__(self):
         self.footy_data_dir = Path(config.config['filepaths']['data_dir'])
         self.logger = logging.getLogger(__name__)


    def read_footy_data(self, league: str, season: str) -> pd.DataFrame:
        """
        Reads football data from a CSV file for the specified league and season.
        """
        file_path = self.footy_data_dir / f"{league.replace(' ', '_')}_{season.replace('/', '-')}_player_stats.csv"
        if file_path.exists():
            return pd.read_csv(file_path)
        else:
            self.logger.warning(f"No data found for {league} {season}. Please fetch the data first.")
            return pd.DataFrame()

    def get_dataframe(self, league: list[str], seasons: list[str]) -> pd.DataFrame:
        """
        Returns the football data as a pandas DataFrame for the specified league and season.
        """
        df = [self.read_footy_data(league, season) for league in league for season in seasons]
        self.logger.info(f"Data fetched for leagues: {league} and seasons: {seasons}.")

        df = [data for data in df if not data.empty]
        if not df:
            self.logger.warning("No data available for the specified leagues and seasons.")
            return pd.DataFrame()

        return pd.concat(df, ignore_index=True)

    def filter_and_analyze_data(self, df: pd.DataFrame, min_minutes: int = 500) -> tuple[pd.DataFrame, pd.DataFrame]:
        try:
            columns = ['team', 'player', 'player_id', 'season_id', 'position', 'matches', 'minutes', 'goals', 'assists', 'xg', 'xa', 'yellow_cards', 'red_cards', 'shots', 'key_passes']
            filtered_df = df[columns]
            filtered_df = filtered_df[filtered_df['minutes'] >= min_minutes]
            goal_analysis_df = filtered_df[~filtered_df['position'].str.contains('GK')]
            goal_analysis_df = goal_analysis_df[goal_analysis_df['goals'] > 0]
            assist_analysis_df = filtered_df[~filtered_df['position'].str.contains('GK')]
            assist_analysis_df = assist_analysis_df[assist_analysis_df['assists'] > 0]

            return goal_analysis_df, assist_analysis_df
    
        except Exception as e:
            self.logger.error(f"Error occurred while filtering and analyzing data: {e}")
            return pd.DataFrame(), pd.DataFrame()

    def group_and_aggregate(self, df: list[pd.DataFrame], group_by_columns: list[str] = ['player', 'player_id'], agg_columns: dict = None) -> tuple[pd.DataFrame, pd.DataFrame]:
        try:
            if agg_columns is None:
                agg_columns = {
                    'matches': 'sum',
                    'minutes': 'sum',
                    'goals': 'sum',
                    'assists': 'sum',
                    'xg': 'sum',
                    'xa': 'sum',
                    'shots': 'sum',
                    'key_passes': 'sum'
                }

            goal_analysis_df = df[0].groupby(group_by_columns).agg(agg_columns).reset_index()
            assist_analysis_df = df[1].groupby(group_by_columns).agg(agg_columns).reset_index()

            goal_analysis_df['goal_conversion_rate'] = (goal_analysis_df['goals'] / goal_analysis_df['xg'].replace(0, np.nan))
            goal_analysis_df['goals_per_shot'] = (goal_analysis_df['goals'] / goal_analysis_df['shots'].replace(0, np.nan))
            assist_analysis_df['assist_conversion_rate'] = (assist_analysis_df['assists'] / assist_analysis_df['xa'].replace(0, np.nan))
            assist_analysis_df['assists_per_key_pass'] = (assist_analysis_df['assists'] / assist_analysis_df['key_passes'].replace(0, np.nan))

            return goal_analysis_df, assist_analysis_df
        except Exception as e:
            self.logger.error(f"Error occurred while grouping and aggregating data: {e}")
            return pd.DataFrame(), pd.DataFrame()
 
def main():
    leagues = ['ENG-Premier League', 'ITA-Serie A']  # Example leagues
    seasons = ['2023/2024', '2024/2025', '2025/2026']  # Example season

    footy_data = FootyDataAnalysis()
    df = footy_data.get_dataframe(leagues, seasons)
    goal_df, assist_df = footy_data.filter_and_analyze_data(df)
    goal_df, assist_df = footy_data.group_and_aggregate([goal_df, assist_df])


    if not [goal_df, assist_df]:
        print("No data to display.")
    else:
        print("Goal Analysis Data:")
        print(goal_df.head())
        print("\nAssist Analysis Data:")
        print(assist_df.head())

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()