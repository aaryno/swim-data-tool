"""USA Swimming API client for team search and data collection.

This client interfaces with the USA Swimming Times Elasticube API via Sisense.
"""

from dataclasses import dataclass
from typing import Any

import pandas as pd
import requests


@dataclass
class TeamInfo:
    """Information about a swim team from USA Swimming."""

    team_code: str
    team_name: str
    lsc_code: str
    lsc_name: str
    swimcloud_id: str | None = None


class USASwimmingAPI:
    """Client for USA Swimming Times Elasticube API via Sisense.

    This API provides access to USA Swimming's swimmer times database.
    No authentication beyond the public token is required.
    """

    # Sisense API endpoint
    BASE_URL = "https://usaswimming.sisense.com/api/datasources/USA%20Swimming%20Times%20Elasticube/jaql"  # noqa: E501

    # Public API token (captured from network traffic)
    AUTH_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoiNjRhZjE4MGY5Nzg1MmIwMDJkZTU1ZDhkIiwiYXBpU2VjcmV0IjoiMzZhZmIyOWUtYTc0ZC00YWVmLWE2YmQtMDA3MzA5ZTYwZTdkIiwiYWxsb3dlZFRlbmFudHMiOlsiNjRhYzE5ZTEwZTkxNzgwMDFiYzM5YmVhIl0sInRlbmFudElkIjoiNjRhYzE5ZTEwZTkxNzgwMDFiYzM5YmVhIn0.fFw6p06oYT6cv-NbhlxHp7-_UpEueGFQaU4N0iEGGlU"  # noqa: E501

    def __init__(self):
        """Initialize the API client."""
        self.session = requests.Session()
        self.session.headers.update({
            "accept": "application/json, text/plain, */*",
            "authorization": f"Bearer {self.AUTH_TOKEN}",
            "content-type": "application/json;charset=UTF-8",
            "origin": "https://data.usaswimming.org",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        })

    def query_times_multi_year(
        self,
        competition_years: list[str],
        person_key: int,
        count: int = 500,
    ) -> dict[str, Any]:
        """Query USA Swimming times for a person across multiple years.

        This is much more efficient than calling query_times multiple times.

        Args:
            competition_years: List of years, e.g., ["2020", "2021", "2022"]
            person_key: PersonKey to filter by
            count: Number of results to return (max 500)

        Returns:
            Dictionary with query results containing metadata and values
        """
        # Build year filter members
        year_members = []
        for year in competition_years:
            year_int = int(year)
            # Handle date format differences
            separator = "-" if year_int >= 2026 else " - "
            year_str = f"{year} (9/1/{year_int-1}{separator}8/31/{year})"
            year_members.append(year_str)

        # Build the query payload
        metadata = [
            {
                "jaql": {
                    "title": "SwimTime",
                    "dim": "[UsasSwimTime.SwimTimeFormatted]",
                    "datatype": "text",
                }
            },
            {
                "jaql": {
                    "title": "Name",
                    "dim": "[UsasSwimTime.FullName]",
                    "datatype": "text",
                }
            },
            {
                "jaql": {
                    "title": "Foreign",
                    "dim": "[Person.IsForeign]",
                    "datatype": "numeric",
                }
            },
            {
                "jaql": {
                    "title": "Age",
                    "dim": "[UsasSwimTime.AgeAtMeetKey]",
                    "datatype": "numeric",
                }
            },
            {
                "jaql": {
                    "title": "Event",
                    "dim": "[SwimEvent.EventCode]",
                    "datatype": "text",
                }
            },
            {
                "jaql": {
                    "title": "LSC",
                    "dim": "[OrgUnit.Level3Code]",
                    "datatype": "text",
                }
            },
            {
                "jaql": {
                    "title": "Team",
                    "dim": "[OrgUnit.Level4Name]",
                    "datatype": "text",
                }
            },
            {
                "jaql": {
                    "title": "Meet",
                    "dim": "[Meet.MeetName]",
                    "datatype": "text",
                }
            },
            {
                "jaql": {
                    "title": "SwimDate",
                    "dim": "[SeasonCalendar.CalendarDate (Calendar)]",
                    "datatype": "datetime",
                    "level": "days",
                },
                "format": {"mask": {"days": "MM/dd/yyyy"}},
            },
            {
                "jaql": {
                    "title": "MeetKey",
                    "dim": "[UsasSwimTime.MeetKey]",
                    "datatype": "numeric",
                }
            },
            {
                "jaql": {
                    "title": "TimeStandard",
                    "dim": "[TimeStandard.TimeStandardName]",
                    "datatype": "text",
                }
            },
            {
                "jaql": {
                    "title": "SwimEventKey",
                    "dim": "[UsasSwimTime.SwimEventKey]",
                    "datatype": "numeric",
                }
            },
            {
                "jaql": {
                    "title": "EventCompetitionCategoryKey",
                    "dim": "[EventCompetitionCategory.EventCompetitionCategoryKey]",
                    "datatype": "numeric",
                }
            },
            {
                "jaql": {
                    "title": "PersonKey",
                    "dim": "[UsasSwimTime.PersonKey]",
                    "datatype": "numeric",
                }
            },
            {
                "jaql": {
                    "title": "SortKey",
                    "dim": "[UsasSwimTime.SortKey]",
                    "datatype": "text",
                    "sort": "asc",
                }
            },
            {
                "jaql": {
                    "title": "UsasSwimTimeKey",
                    "dim": "[UsasSwimTime.UsasSwimTimeKey]",
                    "datatype": "numeric",
                }
            },
            {
                "jaql": {
                    "title": "Rank",
                    "formula": 'RANK(min([4EB09-79E]),"ASC","1224", [42D59-ECD],[4664C-71C])',
                    "context": {
                        "[4664C-71C]": {
                            "title": "EventCompetitionCategoryKey",
                            "dim": "[EventCompetitionCategory.EventCompetitionCategoryKey]",
                            "datatype": "numeric",
                        },
                        "[4EB09-79E]": {
                            "title": "SwimTimeSeconds",
                            "dim": "[UsasSwimTime.SwimTimeSeconds]",
                            "datatype": "numeric",
                        },
                        "[42D59-ECD]": {
                            "title": "SwimEventKey",
                            "dim": "[UsasSwimTime.SwimEventKey]",
                            "datatype": "numeric",
                        },
                    },
                }
            },
            # Multi-year filter
            {
                "jaql": {
                    "title": "SeasonYearDesc",
                    "dim": "[SeasonCalendar.SeasonYearDesc]",
                    "datatype": "text",
                    "filter": {"members": year_members},
                },
                "panel": "scope",
            },
            # PersonKey filter
            {
                "jaql": {
                    "title": "PersonKey",
                    "dim": "[UsasSwimTime.PersonKey]",
                    "datatype": "numeric",
                    "filter": {"equals": int(person_key)},
                },
                "panel": "scope",
            },
        ]

        payload = {
            "metadata": metadata,
            "datasource": "USA Swimming Times Elasticube",
            "by": "ComposeSDK",
            "queryGuid": "optimized-multi-year-query",
            "count": count,
        }

        response = self.session.post(self.BASE_URL, json=payload)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Query failed with status {response.status_code}")

    def to_dataframe(self, results: dict[str, Any]) -> pd.DataFrame | None:
        """Convert API results to pandas DataFrame.

        Args:
            results: API response dictionary

        Returns:
            DataFrame with swim times, or None if no results
        """
        if not results or "values" not in results:
            return None

        # Extract column headers
        headers = [col["jaql"]["title"] for col in results["metadata"] if "jaql" in col]

        # Create DataFrame
        df = pd.DataFrame(results["values"], columns=headers)

        # Extract 'text' field from dictionary columns
        for col in df.columns:
            if col in df and len(df) > 0:
                first_val = df[col].iloc[0]
                if isinstance(first_val, dict) and "text" in first_val:
                    df[col] = df[col].apply(lambda x: x["text"] if isinstance(x, dict) else x)

        return df

    def download_swimmer_career(
        self,
        person_key: int,
        start_year: int = 1998,
        end_year: int = 2025,
    ) -> pd.DataFrame:
        """Download complete career data for a swimmer.

        Args:
            person_key: USA Swimming PersonKey
            start_year: Start year for data collection
            end_year: End year for data collection

        Returns:
            DataFrame with all swims, de-duplicated
        """
        all_swims = []

        # Try ALL years in a single call first
        all_years = [str(y) for y in range(start_year, end_year + 1)]
        try:
            result = self.query_times_multi_year(
                competition_years=all_years,
                person_key=person_key,
                count=500,
            )
            if result and "values" in result and result["values"]:
                df = self.to_dataframe(result)
                if df is not None and not df.empty:
                    all_swims.append(df)
                    # If we didn't hit the 500 limit, we're done
                    if len(df) < 500:
                        combined = (
                            df.drop_duplicates(subset=["UsasSwimTimeKey"])
                            if "UsasSwimTimeKey" in df.columns
                            else df
                        )
                        return combined
        except Exception:
            pass  # Fall back to chunked approach

        # If single query hit limit or failed, use chunks
        if not all_swims or len(all_swims[0]) >= 500:
            all_swims = []

            # Chunk 1: Recent years (2019-2024)
            years_2019_2024 = [str(y) for y in range(2019, end_year + 1)]
            result = self.query_times_multi_year(
                competition_years=years_2019_2024,
                person_key=person_key,
                count=500,
            )
            if result and "values" in result and result["values"]:
                df = self.to_dataframe(result)
                if df is not None and not df.empty:
                    all_swims.append(df)

            # Chunk 2: Middle years (2010-2018)
            years_2010_2018 = [str(y) for y in range(2010, 2019)]
            result = self.query_times_multi_year(
                competition_years=years_2010_2018,
                person_key=person_key,
                count=500,
            )
            if result and "values" in result and result["values"]:
                df = self.to_dataframe(result)
                if df is not None and not df.empty:
                    all_swims.append(df)

            # Chunk 3: Older years (1998-2009)
            years_1998_2009 = [str(y) for y in range(start_year, 2010)]
            result = self.query_times_multi_year(
                competition_years=years_1998_2009,
                person_key=person_key,
                count=500,
            )
            if result and "values" in result and result["values"]:
                df = self.to_dataframe(result)
                if df is not None and not df.empty:
                    all_swims.append(df)

        if all_swims:
            combined = pd.concat(all_swims, ignore_index=True)
            if "UsasSwimTimeKey" in combined.columns:
                combined = combined.drop_duplicates(subset=["UsasSwimTimeKey"])
            return combined

        return pd.DataFrame()

    def search_swimmer_for_team(self, swimmer_name: str) -> list[TeamInfo]:
        """Search for a swimmer and extract their team information.
        
        Two-step process:
        1. Find swimmer(s) by name using Public Person Search
        2. Query their recent swims to get actual team code
        
        Args:
            swimmer_name: Full or partial swimmer name (e.g., "John Smith" or just "Smith")
            
        Returns:
            List of TeamInfo objects from matched swimmers' recent swims
        """
        # STEP 1: Find swimmer PersonKey(s) by name
        # Split name into parts for better matching
        name_parts = swimmer_name.strip().split()
        
        # Build metadata for person search
        metadata = [
            {"jaql": {"title": "Name", "dim": "[Persons.FullName]", "datatype": "text"}},
            {"jaql": {"title": "PersonKey", "dim": "[Persons.PersonKey]", "datatype": "numeric"}},
        ]
        
        # Add name filter
        if len(name_parts) >= 2:
            # Split into first and last name
            first_name = name_parts[0]
            last_name = " ".join(name_parts[1:])
            metadata.append({
                "jaql": {
                    "title": "FirstAndPreferredName",
                    "dim": "[Persons.FirstAndPreferredName]",
                    "datatype": "text",
                    "filter": {"contains": first_name}
                },
                "panel": "scope"
            })
            metadata.append({
                "jaql": {
                    "title": "LastName",
                    "dim": "[Persons.LastName]",
                    "datatype": "text",
                    "filter": {"contains": last_name}
                },
                "panel": "scope"
            })
        else:
            # Just search by full name or last name
            metadata.append({
                "jaql": {
                    "title": "LastName",
                    "dim": "[Persons.LastName]",
                    "datatype": "text",
                    "filter": {"contains": swimmer_name}
                },
                "panel": "scope"
            })
        
        payload = {
            "metadata": metadata,
            "datasource": "Public Person Search",
            "by": "ComposeSDK",
            "queryGuid": "person-search-for-team",
            "count": 50,  # Get multiple matches in case of common names
        }
        
        try:
            response = self.session.post(
                "https://usaswimming.sisense.com/api/datasources/Public%20Person%20Search/jaql",
                json=payload
            )
            
            if response.status_code != 200:
                return []
            
            results = response.json()
            
            if not results or "values" not in results or not results["values"]:
                return []
            
            # Extract PersonKeys from Step 1
            # Results format: [0]=Name, [1]=PersonKey
            person_keys = []
            for row in results["values"]:
                person_key = row[1]
                if isinstance(person_key, dict):
                    person_key = person_key.get("data", person_key.get("text"))
                person_keys.append(int(person_key))
            
            if not person_keys:
                return []
            
            # STEP 2: Query recent swims for each PersonKey to get team info
            teams_dict = {}
            
            for person_key in person_keys[:10]:  # Limit to first 10 matches to avoid overload
                # Build metadata for team lookup from swims
                team_metadata = [
                    {"jaql": {"title": "TeamCode", "dim": "[OrgUnit.Level4Code]", "datatype": "text"}},
                    {"jaql": {"title": "TeamName", "dim": "[OrgUnit.Level4Name]", "datatype": "text"}},
                    {"jaql": {"title": "LSC_Code", "dim": "[OrgUnit.Level3Code]", "datatype": "text"}},
                    {"jaql": {"title": "LSC_Name", "dim": "[OrgUnit.Level3Name]", "datatype": "text"}},
                    {
                        "jaql": {
                            "title": "PersonKey",
                            "dim": "[UsasSwimTime.PersonKey]",
                            "datatype": "numeric",
                            "filter": {"equals": person_key}
                        },
                        "panel": "scope"
                    },
                    {
                        "jaql": {
                            "title": "SeasonYearDesc",
                            "dim": "[SeasonCalendar.SeasonYearDesc]",
                            "datatype": "text",
                            "filter": {"members": ["2025 (9/1/2024 - 8/31/2025)"]}  # Current season only
                        },
                        "panel": "scope"
                    }
                ]
                
                team_payload = {
                    "metadata": team_metadata,
                    "datasource": "USA Swimming Times Elasticube",
                    "by": "ComposeSDK",
                    "queryGuid": "team-lookup-from-swims",
                    "count": 10,
                }
                
                team_response = self.session.post(self.BASE_URL, json=team_payload)
                
                if team_response.status_code != 200:
                    continue
                
                team_results = team_response.json()
                
                if not team_results or "values" not in team_results or not team_results["values"]:
                    continue
                
                # Extract teams from swim results
                # Format: [0]=TeamCode, [1]=TeamName, [2]=LSC_Code, [3]=LSC_Name
                for row in team_results["values"]:
                    team_code = row[0]["text"] if isinstance(row[0], dict) else row[0]
                    team_name = row[1]["text"] if isinstance(row[1], dict) else row[1]
                    lsc_code = row[2]["text"] if isinstance(row[2], dict) else row[2]
                    lsc_name = row[3]["text"] if isinstance(row[3], dict) else row[3]
                    
                    # Use team code + LSC as unique key
                    key = f"{team_code}|{lsc_code}"
                    
                    if key not in teams_dict:
                        teams_dict[key] = TeamInfo(
                            team_code=team_code,
                            team_name=team_name,
                            lsc_code=lsc_code,
                            lsc_name=lsc_name,
                        )
            
            return list(teams_dict.values())
            
        except Exception:
            return []
    
    def get_team_roster(
        self,
        team_code: str,
        season_years: list[str] | None = None,
    ) -> pd.DataFrame:
        """Get roster of swimmers for a team based on recent swims.
        
        Queries USA Swimming Times for all swimmers who swam for the team
        in recent seasons and returns their PersonKeys and names.
        
        Args:
            team_code: USA Swimming team code (e.g., "SWAS", "FORD")
            season_years: List of season years to search (default: last 2 seasons)
            
        Returns:
            DataFrame with columns: PersonKey, FullName, FirstSwimDate, LastSwimDate, SwimCount
        """
        if season_years is None:
            # Default to current and previous season
            season_years = ["2025", "2024"]
        
        # Build year members
        year_members = []
        for year_str in season_years:
            year_int = int(year_str)
            separator = "-" if year_int >= 2026 else " - "
            year_members.append(f"{year_str} (9/1/{year_int-1}{separator}8/31/{year_str})")
        
        # Query for all swims by team code
        metadata = [
            {"jaql": {"title": "PersonKey", "dim": "[UsasSwimTime.PersonKey]", "datatype": "numeric"}},
            {"jaql": {"title": "FullName", "dim": "[UsasSwimTime.FullName]", "datatype": "text"}},
            {"jaql": {"title": "SwimDate", "dim": "[SeasonCalendar.CalendarDate (Calendar)]", "datatype": "datetime", "level": "days"}},
            {
                "jaql": {
                    "title": "TeamCode",
                    "dim": "[OrgUnit.Level4Code]",
                    "datatype": "text",
                    "filter": {"equals": team_code.upper()}
                },
                "panel": "scope"
            },
            {
                "jaql": {
                    "title": "SeasonYearDesc",
                    "dim": "[SeasonCalendar.SeasonYearDesc]",
                    "datatype": "text",
                    "filter": {"members": year_members}
                },
                "panel": "scope"
            }
        ]
        
        payload = {
            "metadata": metadata,
            "datasource": "USA Swimming Times Elasticube",
            "by": "ComposeSDK",
            "queryGuid": "team-roster-query",
            "count": 10000,  # Get lots of swims to capture all swimmers
        }
        
        try:
            response = self.session.post(self.BASE_URL, json=payload)
            
            if response.status_code != 200:
                return pd.DataFrame()
            
            results = response.json()
            
            if not results or "values" not in results or not results["values"]:
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = self.to_dataframe(results)
            
            if df is None or df.empty:
                return pd.DataFrame()
            
            # Aggregate by PersonKey to get roster
            roster = df.groupby(["PersonKey", "FullName"]).agg(
                FirstSwimDate=("SwimDate", "min"),
                LastSwimDate=("SwimDate", "max"),
                SwimCount=("SwimDate", "count")
            ).reset_index()
            
            # Sort by most recent activity
            roster = roster.sort_values("LastSwimDate", ascending=False)
            
            return roster
            
        except Exception as e:
            print(f"Error fetching roster: {e}")
            return pd.DataFrame()
    
    def search_team(self, team_name: str, lsc_code: str | None = None) -> list[TeamInfo]:
        """Search for teams by name in USA Swimming database.

        Args:
            team_name: Full or partial team name to search for
            lsc_code: Optional LSC code to narrow search (e.g., "AZ")

        Returns:
            List of matching teams with their information
        """
        # Query recent years to find active teams (expanded to 5 years for better coverage)
        current_year = 2025
        search_years = [str(y) for y in range(current_year - 4, current_year + 1)]  # 2021-2025
        
        # Build year members with correct format (spaces for years < 2026)
        year_members = []
        for year_str in search_years:
            year_int = int(year_str)
            # 2026+ has no spaces, earlier years have spaces
            separator = "-" if year_int >= 2026 else " - "
            year_members.append(f"{year_str} (9/1/{year_int-1}{separator}8/31/{year_str})")
        
        # Build metadata for team search
        metadata = [
            {
                "jaql": {
                    "title": "Team",
                    "dim": "[OrgUnit.Level4Name]",
                    "datatype": "text",
                    "filter": {
                        "contains": team_name
                    }
                }
            },
            {
                "jaql": {
                    "title": "LSC",
                    "dim": "[OrgUnit.Level3Code]",
                    "datatype": "text",
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
        
        # Add LSC filter if provided
        if lsc_code:
            metadata[1]["jaql"]["filter"] = {"equals": lsc_code.upper()}
        
        payload = {
            "metadata": metadata,
            "datasource": "USA Swimming Times Elasticube",
            "by": "ComposeSDK",
            "queryGuid": "team-search-query",
            "count": 100,
        }
        
        try:
            response = self.session.post(self.BASE_URL, json=payload)
            
            if response.status_code != 200:
                return []
            
            results = response.json()
            
            if not results or "values" not in results:
                return []
            
            # Process results into unique teams
            teams_dict = {}
            for row in results["values"]:
                team_name_val = row[0]["text"] if isinstance(row[0], dict) else row[0]
                lsc_code_val = row[1]["text"] if isinstance(row[1], dict) else row[1]
                lsc_name_val = row[2]["text"] if isinstance(row[2], dict) else row[2]
                
                # Use team name + LSC as unique key
                key = f"{team_name_val}|{lsc_code_val}"
                
                if key not in teams_dict:
                    teams_dict[key] = TeamInfo(
                        team_code=f"{lsc_code_val} {team_name_val.split()[0].upper()}",  # Estimate
                        team_name=team_name_val,
                        lsc_code=lsc_code_val,
                        lsc_name=lsc_name_val,
                    )
            
            return list(teams_dict.values())
            
        except Exception:
            return []
