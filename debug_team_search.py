#!/usr/bin/env python3
"""Debug script to test team search API calls."""

import json
from swim_data_tool.api import USASwimmingAPI

# Create API client
api = USASwimmingAPI()

# Test the raw API call
print("Testing team search for 'Aquatic' in Arizona...")
print("=" * 70)

# Build the query manually to see raw response
search_years = ["2021", "2022", "2023", "2024", "2025"]
year_members = []
for year_str in search_years:
    year_int = int(year_str)
    separator = " - "  # All years before 2026 have spaces
    year_members.append(f"{year_str} (9/1/{year_int-1}{separator}8/31/{year_str})")

print(f"Year members: {year_members}")
print()

metadata = [
    {
        "jaql": {
            "title": "Team",
            "dim": "[OrgUnit.Level4Name]",
            "datatype": "text",
            "filter": {
                "contains": "Aquatic"
            }
        }
    },
    {
        "jaql": {
            "title": "LSC",
            "dim": "[OrgUnit.Level3Code]",
            "datatype": "text",
            "filter": {"equals": "AZ"}
        }
    },
    {
        "jaql": {
            "title": "LSC_Name",
            "dim": "[OrgUnit.Level3Name]",
            "datatype": "text",
        }
    },
    {
        "jaql": {
            "title": "SeasonYearDesc",
            "dim": "[SeasonCalendar.SeasonYearDesc]",
            "datatype": "text",
            "filter": {
                "members": year_members
            }
        },
        "panel": "scope"
    }
]

payload = {
    "metadata": metadata,
    "datasource": "USA Swimming Times Elasticube",
    "by": "ComposeSDK",
    "queryGuid": "team-search-debug",
    "count": 100,
}

print("Sending API request...")
response = api.session.post(api.BASE_URL, json=payload)

print(f"Status code: {response.status_code}")
print()

if response.status_code == 200:
    results = response.json()
    print(f"Response keys: {results.keys()}")
    print()
    
    if "values" in results and results["values"]:
        print(f"Number of results: {len(results['values'])}")
        print()
        print("First 10 results:")
        for idx, row in enumerate(results["values"][:10], 1):
            print(f"{idx}. {row}")
        print()
        
        # Now test the actual search_team method
        print("=" * 70)
        print("Testing search_team() method...")
        teams = api.search_team("Aquatic", lsc_code="AZ")
        print(f"Found {len(teams)} teams:")
        for team in teams:
            print(f"  - {team.team_name} ({team.lsc_code})")
    else:
        print("No values in response!")
        print(f"Full response: {json.dumps(results, indent=2)}")
else:
    print(f"Error response: {response.text}")
