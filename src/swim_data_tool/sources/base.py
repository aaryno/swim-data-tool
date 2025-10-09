"""Abstract base class for swim data sources."""

from abc import ABC, abstractmethod
from typing import Any

import pandas as pd


class SwimDataSource(ABC):
    """Abstract base class for swim data sources.

    All data sources must implement this interface to provide
    consistent data collection and normalization across different
    swimming organizations (USA Swimming, MaxPreps, etc.).
    """

    @property
    @abstractmethod
    def source_name(self) -> str:
        """Human-readable source name.

        Returns:
            Source name (e.g., "USA Swimming", "MaxPreps")
        """
        pass

    @property
    @abstractmethod
    def swimmer_id_field(self) -> str:
        """Field name for unique swimmer ID.

        Returns:
            ID field name (e.g., "PersonKey", "careerid")
        """
        pass

    @abstractmethod
    def get_team_roster(self, team_id: str, seasons: list[str] | None = None) -> pd.DataFrame:
        """Fetch team roster for given seasons.

        Args:
            team_id: Team/school identifier (format varies by source)
            seasons: List of season identifiers (e.g., ["2024", "2023"] or ["24-25", "23-24"])

        Returns:
            DataFrame with columns:
                - swimmer_id: Unique identifier
                - swimmer_name: Full name
                - gender: "M" or "F"
                - grade: Optional grade level
                - [other source-specific metadata]
        """
        pass

    @abstractmethod
    def get_swimmer_history(
        self,
        swimmer_id: str,
        start_year: int | None = None,
        end_year: int | None = None,
    ) -> pd.DataFrame:
        """Fetch complete swimmer history.

        Args:
            swimmer_id: Unique swimmer identifier
            start_year: Optional start year filter
            end_year: Optional end year filter

        Returns:
            DataFrame with canonical columns:
                - swimmer_id: Unique identifier
                - swimmer_name: Full name
                - gender: "M" or "F"
                - age: Age at swim
                - event: Event string (will be parsed)
                - time: Formatted time string
                - date: Swim date (string, various formats OK)
                - meet: Meet name
                - team_name: Team/school name
                - source: Source identifier
                - [other metadata preserved for source tracking]
        """
        pass

    @abstractmethod
    def validate_team_id(self, team_id: str) -> bool:
        """Validate team identifier format.

        Args:
            team_id: Team identifier to validate

        Returns:
            True if valid, False otherwise
        """
        pass

    def get_config_template(self) -> dict[str, Any]:
        """Get configuration template for .env file.

        Returns:
            Dictionary of config keys and descriptions
        """
        return {
            "DATA_SOURCE": f"Source: {self.source_name.lower().replace(' ', '_')}",
            "CLUB_NAME": "Your team/school name",
        }

    def parse_event(self, event_str: str) -> tuple[str | None, str | None, str | None]:
        """Parse event string into distance, stroke, course.

        Default implementation for common formats. Sources can override
        if they have different event string formats.

        Args:
            event_str: Event string (e.g., "50 FR SCY", "100 Free")

        Returns:
            Tuple of (distance, stroke, course) or (None, None, None)
        """
        # This will be implemented in each source if needed
        # Default: delegate to models.events.parse_api_event
        from swim_data_tool.models.events import parse_api_event
        return parse_api_event(event_str)


