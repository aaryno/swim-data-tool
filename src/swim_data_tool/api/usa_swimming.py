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
    AUTH_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoiNjRhZjE4MGY5Nzg1MmIwMDJkZTU1ZDhkIiwiYXBpU2VjcmV0IjoiZGQxZjU3ZTgtNTgxYy04OWU5LTgxZTUtMTE5MDZjMTRlZmRlIiwiYWxsb3dlZFRlbmFudHMiOlsiNjRhYzE5ZTEwZTkxNzgwMDFiYzM5YmVhIl0sInRlbmFudElkIjoiNjRhYzE5ZTEwZTkxNzgwMDFiYzM5YmVhIn0.z3etpHoiXSqsrXYzNCDG1oLn-irbnfJvPeI4HDMZiCU"  # noqa: E501

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

    def search_team(self, team_name: str) -> list[TeamInfo]:
        """Search for teams by name.

        Args:
            team_name: Full or partial team name to search for

        Returns:
            List of matching teams with their information

        Note:
            Not yet implemented - requires scraping team listings.
            For now, return empty list to trigger manual entry.
        """
        # TODO: Implement team search
        return []
