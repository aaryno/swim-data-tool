"""USA Swimming data source plugin.

This plugin wraps the existing USASwimmingAPI to conform to the
SwimDataSource interface.
"""

import os

import pandas as pd

from swim_data_tool.api.usa_swimming import USASwimmingAPI
from swim_data_tool.sources.base import SwimDataSource


class USASwimmingSource(SwimDataSource):
    """USA Swimming data source implementation.

    Provides access to USA Swimming times database via Sisense API.
    """

    @property
    def source_name(self) -> str:
        """Human-readable source name."""
        return "USA Swimming"

    @property
    def swimmer_id_field(self) -> str:
        """Field name for unique swimmer ID."""
        return "PersonKey"

    def __init__(self):
        """Initialize USA Swimming source."""
        self.api = USASwimmingAPI()

    def get_team_roster(self, team_id: str, seasons: list[str] | None = None) -> pd.DataFrame:
        """Fetch team roster from USA Swimming.

        Args:
            team_id: Team code (e.g., "AZ-SHS", "RAYS", "FORD")
            seasons: List of years (e.g., ["2024", "2023"])

        Returns:
            DataFrame with columns:
                - PersonKey: Unique identifier
                - FullName: Full name
                - Gender: "M" or "F"
                - FirstSwimDate, LastSwimDate, SwimCount
        """
        if seasons is None:
            # Default to current year if not specified
            from datetime import datetime
            seasons = [str(datetime.now().year)]

        # The API expects team_code and season_years parameters
        try:
            df = self.api.get_team_roster(team_code=team_id, season_years=seasons)
            return df
        except Exception as e:
            print(f"⚠️  Failed to get roster: {e}")
            return pd.DataFrame()

    def get_swimmer_history(
        self,
        swimmer_id: str,
        start_year: int | None = None,
        end_year: int | None = None,
    ) -> pd.DataFrame:
        """Fetch swimmer history from USA Swimming.

        Args:
            swimmer_id: PersonKey (as string)
            start_year: Start year (defaults to 1998)
            end_year: End year (defaults to current year)

        Returns:
            DataFrame with canonical columns:
                - swimmer_id: PersonKey (as string)
                - swimmer_name: FullName (renamed from Name)
                - gender: Gender (from API)
                - age: Age (from AgeAtMeetKey)
                - event: Event (original string)
                - time: SwimTime (original formatted)
                - date: SwimDate
                - meet: Meet name
                - team_name: Team (original)
                - source: "usa_swimming"
        """
        person_key = int(swimmer_id)

        # Use defaults if not specified
        if start_year is None:
            start_year = int(os.getenv("START_YEAR", "1998"))
        if end_year is None:
            from datetime import datetime
            end_year = int(os.getenv("END_YEAR", str(datetime.now().year)))

        # Download from API
        df = self.api.download_swimmer_career(
            person_key=person_key,
            start_year=start_year,
            end_year=end_year,
        )

        if df.empty:
            return df

        # Normalize to canonical format
        df = df.copy()

        # Rename columns to canonical names
        column_mapping = {
            "Name": "swimmer_name",
            "SwimTime": "time",
            "SwimDate": "date",
            "Meet": "meet",
            "Team": "team_name",
            "Age": "age",
            "Gender": "gender",
            "Event": "event",
        }

        df = df.rename(columns=column_mapping)

        # Add source tracking
        df["swimmer_id"] = swimmer_id
        df["source"] = "usa_swimming"

        return df

    def validate_team_id(self, team_id: str) -> bool:
        """Validate USA Swimming team ID format.

        Args:
            team_id: Team code (e.g., "AZ-SHS" or "06281")

        Returns:
            True if format looks valid
        """
        # USA Swimming team IDs are either:
        # - LSC-XXX format (e.g., "AZ-SHS")
        # - Numeric ID (e.g., "06281")
        if "-" in team_id:
            parts = team_id.split("-")
            return len(parts) == 2 and len(parts[0]) == 2
        return team_id.isdigit()

    def get_config_template(self) -> dict[str, str]:
        """Get USA Swimming configuration template."""
        return {
            "DATA_SOURCE": "usa_swimming",
            "USA_SWIMMING_TEAM_ID": "Your team code (e.g., AZ-SHS)",
            "USA_SWIMMING_TEAM_NAMES": "Team name(s) for filtering (comma-separated)",
            "START_YEAR": "1998",
            "END_YEAR": "2024",
            "CLUB_NAME": "Your team name",
        }

