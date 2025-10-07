#!/usr/bin/env python3
"""Test if we can get actual team codes from swimmer data."""

import requests
import json

# API setup
BASE_URL = "https://usaswimming.sisense.com/api/datasources/USA%20Swimming%20Times%20Elasticube/jaql"
AUTH_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoiNjRhZjE4MGY5Nzg1MmIwMDJkZTU1ZDhkIiwiYXBpU2VjcmV0IjoiMzZhZmIyOWUtYTc0ZC00YWVmLWE2YmQtMDA3MzA5ZTYwZTdkIiwiYWxsb3dlZFRlbmFudHMiOlsiNjRhYzE5ZTEwZTkxNzgwMDFiYzM5YmVhIl0sInRlbmFudElkIjoiNjRhYzE5ZTEwZTkxNzgwMDFiYzM5YmVhIn0.fFw6p06oYT6cv-NbhlxHp7-_UpEueGFQaU4N0iEGGlU"

session = requests.Session()
session.headers.update({
    "accept": "application/json, text/plain, */*",
    "authorization": f"Bearer {AUTH_TOKEN}",
    "content-type": "application/json;charset=UTF-8",
    "origin": "https://data.usaswimming.org",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
})

# Query for Wade Olsson (we know his PersonKey: 1685870)
# Get just a few swims from 2023 to see team code
payload = {
    "metadata": [
        {"jaql": {"title": "Name", "dim": "[UsasSwimTime.FullName]", "datatype": "text"}},
        {"jaql": {"title": "TeamName", "dim": "[OrgUnit.Level4Name]", "datatype": "text"}},
        {"jaql": {"title": "TeamCode", "dim": "[OrgUnit.Level4Code]", "datatype": "text"}},  # Try this
        {"jaql": {"title": "LSC", "dim": "[OrgUnit.Level3Code]", "datatype": "text"}},
        {"jaql": {"title": "Event", "dim": "[SwimEvent.EventCode]", "datatype": "text"}},
        {
            "jaql": {
                "title": "PersonKey",
                "dim": "[UsasSwimTime.PersonKey]",
                "datatype": "numeric",
                "filter": {"equals": 1685870}  # Wade Olsson
            },
            "panel": "scope"
        },
        {
            "jaql": {
                "title": "SeasonYearDesc",
                "dim": "[SeasonCalendar.SeasonYearDesc]",
                "datatype": "text",
                "filter": {"members": ["2023 (9/1/2022 - 8/31/2023)"]}
            },
            "panel": "scope"
        }
    ],
    "datasource": "USA Swimming Times Elasticube",
    "by": "ComposeSDK",
    "queryGuid": "test-team-code-field",
    "count": 10,
}

print("Testing if Level4Code (team code) field exists...")
print("Querying Wade Olsson's 2023 swims...")
print("=" * 70)

response = session.post(BASE_URL, json=payload)

print(f"Status: {response.status_code}")
if response.status_code == 200:
    results = response.json()
    if "values" in results and results["values"]:
        print(f"\nFound {len(results['values'])} swims")
        print("\nFirst swim:")
        print(json.dumps(results["values"][0], indent=2))
        
        # Check if TeamCode field has data
        headers = [col["jaql"]["title"] for col in results["metadata"] if "jaql" in col]
        print(f"\nHeaders: {headers}")
        
        if len(results["values"][0]) >= 3:
            print(f"\nTeam Name: {results['values'][0][1]}")
            print(f"Team Code: {results['values'][0][2]}")
            print(f"LSC: {results['values'][0][3]}")
    else:
        print("No values returned")
        print(json.dumps(results, indent=2))
else:
    print(f"Error: {response.text}")
