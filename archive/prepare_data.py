import pandas as pd
import numpy as np
import os

# Define paths
SOURCE_DIR = r'C:\claude\archive'
DEST_DIR = r'C:\claude\archive\cleaned_data'

# Ensure destination directory exists
os.makedirs(DEST_DIR, exist_ok=True)

def clean_players_data():
    """Clean and prepare player statistics data"""
    print("Loading players data...")
    df = pd.read_csv(os.path.join(SOURCE_DIR, 'csgo_players.csv'))

    print(f"Original players data shape: {df.shape}")

    # Clean the kill_to_death_diff column - remove placeholder text
    if 'kill_to_death_diff' in df.columns:
        df['kill_to_death_diff'] = df['kill_to_death_diff'].replace('K - D diff.', np.nan)
        # Convert to numeric, coercing errors to NaN
        df['kill_to_death_diff'] = pd.to_numeric(df['kill_to_death_diff'], errors='coerce')

    # Convert percentage columns to numeric (remove % and divide by 100)
    percentage_cols = ['headshot_percentage', 'team_win_percent_after_first_kill']
    for col in percentage_cols:
        if col in df.columns:
            df[col] = df[col].str.rstrip('%').astype('float') / 100.0

    # Convert numeric columns to proper types
    numeric_cols = [
        'age', 'total_kills', 'total_deaths', 'damage_per_round',
        'grenade_dmg_per_round', 'maps_played', 'rounds_played',
        'kills_per_death', 'kills_per_round', 'assists_per_round',
        'deaths_per_round', 'saved_by_teammate_per_round',
        'saved_teammates_per_round', 'rounds_with_kills',
        'total_opening_kills', 'total_opening_deaths', 'opening_kill_ratio',
        'opening_kill_rating', 'first_kill_in_won_rounds', '0_kill_rounds',
        '1_kill_rounds', '2_kill_rounds', '3_kill_rounds', '4_kill_rounds',
        '5_kill_rounds', 'rifle_kills', 'sniper_kills', 'smg_kills',
        'pistol_kills', 'grenade_kills', 'other_kills', 'rating'
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Remove duplicate player_ids, keeping the first occurrence
    df = df.drop_duplicates(subset=['player_id'], keep='first')

    # Fill missing values in team columns with empty string
    text_cols = ['nickname', 'real_name', 'country', 'current_team', 'teams']
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].fillna('')

    # Sort by rating descending
    if 'rating' in df.columns:
        df = df.sort_values('rating', ascending=False)

    print(f"Cleaned players data shape: {df.shape}")
    print(f"Missing values per column:\n{df.isnull().sum()[df.isnull().sum() > 0]}")

    # Save cleaned data
    output_path = os.path.join(DEST_DIR, 'players_clean.csv')
    df.to_csv(output_path, index=False)
    print(f"Saved cleaned players data to: {output_path}")

    return df

def clean_matches_data():
    """Clean and prepare match data"""
    print("\nLoading matches data...")
    df = pd.read_csv(os.path.join(SOURCE_DIR, 'CSGO_Matches.csv'))

    print(f"Original matches data shape: {df.shape}")

    # Drop the unnamed index column if it exists
    if df.columns[0].startswith('Unnamed'):
        df = df.drop(df.columns[0], axis=1)

    # Convert numeric columns to proper types
    numeric_cols = [
        'roundNum', 'tScore', 'ctScore', 'endTScore', 'endCTScore',
        'ctFreezeTimeEndEqVal', 'ctRoundStartEqVal', 'ctRoundSpendMoney',
        'tFreezeTimeEndEqVal', 'tRoundStartEqVal', 'tRoundSpendMoney'
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Clean string columns - remove extra whitespace
    text_cols = ['mapName', 'ctTeam', 'tTeam', 'roundEndReason',
                 'ctBuyType', 'tBuyType', 'winningSide', 'winningTeam', 'losingTeam']
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    # Remove rows with missing critical data
    critical_cols = ['mapName', 'ctTeam', 'tTeam', 'winningTeam']
    df = df.dropna(subset=[col for col in critical_cols if col in df.columns])

    # Remove duplicate rows
    df = df.drop_duplicates()

    # Sort by map name and round number
    if 'mapName' in df.columns and 'roundNum' in df.columns:
        df = df.sort_values(['mapName', 'roundNum'])

    print(f"Cleaned matches data shape: {df.shape}")
    print(f"Missing values per column:\n{df.isnull().sum()[df.isnull().sum() > 0]}")

    # Save cleaned data
    output_path = os.path.join(DEST_DIR, 'matches_clean.csv')
    df.to_csv(output_path, index=False)
    print(f"Saved cleaned matches data to: {output_path}")

    return df

def main():
    """Main function to clean all data"""
    print("=" * 60)
    print("CS:GO Data Cleaning Script")
    print("=" * 60)

    # Clean players data
    players_df = clean_players_data()

    # Clean matches data
    matches_df = clean_matches_data()

    print("\n" + "=" * 60)
    print("Data cleaning completed successfully!")
    print("=" * 60)
    print(f"\nCleaned files saved to: {DEST_DIR}")
    print(f"  - players_clean.csv: {len(players_df)} records")
    print(f"  - matches_clean.csv: {len(matches_df)} records")

if __name__ == "__main__":
    main()
