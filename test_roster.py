#!/usr/bin/env python3
"""Test the roster functionality."""

from swim_data_tool.api import USASwimmingAPI

api = USASwimmingAPI()

print("Testing roster fetch for SWAS...")
print("=" * 70)

roster = api.get_team_roster("SWAS", season_years=["2024", "2025"])

print(f"Found {len(roster)} swimmers\n")

if not roster.empty:
    print("First 10 swimmers:")
    print(roster.head(10).to_string())
    print("\n✓ Roster fetch working!")
else:
    print("✗ No swimmers found")
