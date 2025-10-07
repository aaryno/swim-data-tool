#!/usr/bin/env python3
"""Test the two-step search implementation."""

import json
from swim_data_tool.api import USASwimmingAPI

def main():
    print("=" * 80)
    print("TWO-STEP SEARCH TEST")
    print("=" * 80)
    print()
    
    api = USASwimmingAPI()
    
    # Test 1: Search for Zach Duerkop
    print("Test 1: Searching for 'zach duerkop'...")
    print("-" * 80)
    
    try:
        teams = api.search_swimmer_for_team("zach duerkop")
        
        print(f"✓ Search completed")
        print(f"✓ Found {len(teams)} team(s)")
        print()
        
        if teams:
            for i, team in enumerate(teams, 1):
                print(f"Team {i}:")
                print(f"  Team Code: {team.team_code}")
                print(f"  Team Name: {team.team_name}")
                print(f"  LSC Code:  {team.lsc_code}")
                print(f"  LSC Name:  {team.lsc_name}")
                print()
        else:
            print("✗ No teams found")
            print()
            
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    print("=" * 80)
    print("Expected Results:")
    print("  - Team Code should be 'SWAS' (not a number like '17')")
    print("  - Team Name should be 'South West Aquatic Sports'")
    print("  - LSC Code should be 'AZ'")
    print("=" * 80)

if __name__ == "__main__":
    main()
