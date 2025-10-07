#!/usr/bin/env python3
"""Simple roster test."""

import sys
from swim_data_tool.api import USASwimmingAPI

try:
    api = USASwimmingAPI()
    print("API initialized", file=sys.stderr)
    
    roster = api.get_team_roster("SWAS", season_years=["2025"])
    print(f"SUCCESS: Found {len(roster)} swimmers", file=sys.stderr)
    print(roster.head(5), file=sys.stderr)
    
except Exception as e:
    print(f"ERROR: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc(file=sys.stderr)
