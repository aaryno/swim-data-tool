"""Canonical data models for swim data.

These models define the standard format that all data sources
must conform to after normalization. This allows source-agnostic
record generation and processing.
"""

from dataclasses import dataclass, field
from datetime import date
from typing import Any


@dataclass
class Swimmer:
    """Unified swimmer model across all sources."""

    swimmer_id: str  # Source-specific ID (PersonKey, careerid, etc.)
    full_name: str
    gender: str  # "M" or "F"
    date_of_birth: date | None = None
    grade: str | None = None  # For high school swimmers
    source: str = ""  # Source identifier (usa_swimming, maxpreps, etc.)
    source_metadata: dict[str, Any] = field(default_factory=dict)  # Source-specific fields


@dataclass
class Swim:
    """Unified swim performance across all sources."""

    swimmer_id: str
    swimmer_name: str
    event_code: str  # Normalized: "50-free", "100-back", etc.
    event_distance: str  # "50", "100", "200", etc.
    event_stroke: str  # "free", "back", "breast", "fly", "im"
    event_course: str  # "scy", "lcm", "scm"
    time: str  # Formatted time string (e.g., "21.45" or "1:42.15")
    time_seconds: float  # Time in seconds for sorting
    age: int  # Age at swim
    age_group: str  # "10U", "11-12", "13-14", etc.
    swim_date: str  # Swim date (various formats OK, will be parsed)
    meet_name: str
    team_name: str
    team_id: str
    gender: str  # "M" or "F"
    source: str  # Source identifier
    is_relay: bool = False
    source_metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Team:
    """Unified team/school model across all sources."""

    team_id: str
    team_name: str
    organization: str  # "USA Swimming", "AIA Arizona", etc.
    level: str  # "club", "high_school", "college"
    city: str | None = None
    state: str | None = None
    region: str | None = None  # LSC for USA Swimming, Division for high school
    active_years: tuple[int, int] | None = None  # (start_year, end_year)
    source: str = ""
    source_metadata: dict[str, Any] = field(default_factory=dict)


# Column names for canonical DataFrame format
CANONICAL_COLUMNS = {
    # Swimmer info
    "swimmer_id": "Unique swimmer identifier (source-specific)",
    "swimmer_name": "Full name",
    "gender": "M or F",
    "age": "Age at swim",
    "grade": "Grade level (high school)",
    # Event info
    "event": "Original event string",
    "event_distance": "Distance (50, 100, 200, etc.)",
    "event_stroke": "Stroke (free, back, breast, fly, im)",
    "event_course": "Course (scy, lcm, scm)",
    "event_code": "Normalized code (50-free, 100-back, etc.)",
    # Time info
    "time": "Formatted time string",
    "time_seconds": "Time in seconds (for sorting)",
    "age_group": "Age group (10U, 11-12, etc.)",
    # Meet info
    "swim_date": "Date of swim",
    "meet": "Meet name",
    "team_name": "Team/school name",
    "team_id": "Team identifier",
    # Source tracking
    "source": "Data source (usa_swimming, maxpreps, etc.)",
    "source_url": "URL to source data (if applicable)",
}


def get_canonical_column_order() -> list[str]:
    """Get standard column order for canonical DataFrames.

    Returns:
        List of column names in preferred order
    """
    return [
        "swimmer_id",
        "swimmer_name",
        "gender",
        "age",
        "grade",
        "event",
        "event_distance",
        "event_stroke",
        "event_course",
        "event_code",
        "time",
        "time_seconds",
        "age_group",
        "swim_date",
        "meet",
        "team_name",
        "team_id",
        "source",
        "source_url",
    ]


def validate_canonical_dataframe(df: Any) -> tuple[bool, list[str]]:
    """Validate that a DataFrame conforms to canonical format.

    Args:
        df: DataFrame to validate

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    import pandas as pd

    if not isinstance(df, pd.DataFrame):
        return False, ["Not a pandas DataFrame"]

    errors = []

    # Required columns
    required = [
        "swimmer_id",
        "swimmer_name",
        "gender",
        "age",
        "event_code",
        "time",
        "time_seconds",
        "swim_date",
        "meet",
        "source",
    ]

    missing = [col for col in required if col not in df.columns]
    if missing:
        errors.append(f"Missing required columns: {', '.join(missing)}")

    # Check gender values
    if "gender" in df.columns:
        invalid_genders = df[~df["gender"].isin(["M", "F", None])]["gender"].unique()
        if len(invalid_genders) > 0:
            errors.append(f"Invalid gender values: {', '.join(map(str, invalid_genders))}")

    # Check time_seconds is numeric
    if "time_seconds" in df.columns:
        if not pd.api.types.is_numeric_dtype(df["time_seconds"]):
            errors.append("time_seconds must be numeric")

    # Check event_course values
    if "event_course" in df.columns:
        invalid_courses = df[~df["event_course"].isin(["scy", "lcm", "scm", None])]["event_course"].unique()
        if len(invalid_courses) > 0:
            errors.append(f"Invalid course values: {', '.join(map(str, invalid_courses))}")

    return len(errors) == 0, errors
