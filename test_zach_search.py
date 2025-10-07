#!/usr/bin/env python3
"""Test searching for Zach Duerkop."""

import json
from swim_data_tool.api import USASwimmingAPI

api = USASwimmingAPI()

print("Testing search for 'zach duerkop'...")
print("=" * 70)

teams = api.search_swimmer_for_team("zach duerkop")

print(f"Found {len(teams)} teams")

if teams:
    for team in teams:
        print(f"  - {team.team_code} | {team.team_name} | {team.lsc_code}")
else:
    print("No teams found!")
    
print("\n" + "=" * 70)
print("Testing raw API call...")

# Try the raw API call
name_parts = "zach duerkop".strip().split()
first_name = name_parts[0]
last_name = " ".join(name_parts[1:])

metadata = [
    {"jaql": {"title": "Name", "dim": "[Persons.FullName]", "datatype": "text"}},
    {"jaql": {"title": "Club", "dim": "[Persons.ClubName]", "datatype": "text"}},
    {"jaql": {"title": "ClubCode", "dim": "[Persons.ClubCode]", "datatype": "text"}},
    {"jaql": {"title": "LSC", "dim": "[Persons.LscCode]", "datatype": "text"}},
    {"jaql": {"title": "LSC_Name", "dim": "[Persons.LscName]", "datatype": "text"}},
    {"jaql": {"title": "Age", "dim": "[Persons.Age]", "datatype": "numeric"}},
    {"jaql": {"title": "PersonKey", "dim": "[Persons.PersonKey]", "datatype": "numeric"}},
    {
        "jaql": {
            "title": "FirstAndPreferredName",
            "dim": "[Persons.FirstAndPreferredName]",
            "datatype": "text",
            "filter": {"contains": first_name}
        },
        "panel": "scope"
    },
    {
        "jaql": {
            "title": "LastName",
            "dim": "[Persons.LastName]",
            "datatype": "text",
            "filter": {"contains": last_name}
        },
        "panel": "scope"
    }
]

payload = {
    "metadata": metadata,
    "datasource": "Public Person Search",
    "by": "ComposeSDK",
    "queryGuid": "test-zach",
    "count": 50,
}

print(f"First name filter: '{first_name}'")
print(f"Last name filter: '{last_name}'")
print()

response = api.session.post(api.BASE_URL, json=payload)

print(f"Status: {response.status_code}")

if response.status_code == 200:
    results = response.json()
    if "values" in results and results["values"]:
        print(f"Found {len(results['values'])} results")
        print("\nFirst result:")
        print(json.dumps(results["values"][0], indent=2))
    else:
        print("No values in response")
        print(f"Response: {json.dumps(results, indent=2)}")
else:
    print(f"Error: {response.text}")
