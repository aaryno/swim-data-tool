#!/usr/bin/env python3
"""Check what teams appear for Wade Olsson in the API."""

from swim_data_tool.api import USASwimmingAPI

# Wade Olsson's PersonKey from the CSV file
WADE_PERSON_KEY = 1685870

# Create API client
api = USASwimmingAPI()

print(f"Querying swims for PersonKey {WADE_PERSON_KEY} (Wade Olsson)...")
print("=" * 70)

# Download career data (2021-2025 should include the 2023 swim)
df = api.download_swimmer_career(WADE_PERSON_KEY, start_year=2021, end_year=2025)

if df.empty:
    print("No swims found!")
else:
    print(f"Found {len(df)} swims")
    print()
    
    # Get unique team names
    if 'Team' in df.columns:
        unique_teams = df['Team'].unique()
        print(f"Unique teams ({len(unique_teams)}):")
        for team in sorted(unique_teams):
            print(f"  - '{team}'")
        print()
        
        # Show some sample swims with team names
        print("Sample swims:")
        for idx, row in df.head(10).iterrows():
            print(f"  {row.get('SwimTime', 'N/A')} | {row.get('Event', 'N/A')} | Team: '{row.get('Team', 'N/A')}' | LSC: '{row.get('LSC', 'N/A')}'")
    else:
        print("No 'Team' column found in results!")
        print(f"Columns: {df.columns.tolist()}")
