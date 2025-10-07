"""Service for generating team records from swim data."""

import pandas as pd
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from swim_data_tool.models.events import (
    AGE_GROUPS,
    LCM_EVENTS,
    SCM_EVENTS,
    SCY_EVENTS,
    convert_time_to_seconds,
    create_event_code,
    determine_age_group,
    format_event_name,
    parse_api_event,
)


@dataclass
class RecordEntry:
    """A single record entry."""

    event_code: str
    age_group: str
    swimmer_name: str
    time: str
    age: str
    date: str
    meet: str
    swim_type: str = ""  # probationary, team-unattached, etc.
    time_seconds: float = 0.0


class RecordGenerator:
    """Generate team records from swimmer data."""

    def __init__(self, data_dir: Path):
        """Initialize record generator.

        Args:
            data_dir: Path to data directory (should contain raw/ and processed/)
        """
        self.data_dir = Path(data_dir)
        self.raw_dir = self.data_dir / "raw" / "swimmers"
        self.processed_dir = self.data_dir / "processed" / "unattached"

    def load_all_swimmer_data(self) -> pd.DataFrame:
        """Load all swimmer CSVs from raw directory.

        Returns:
            Combined DataFrame with all swimmer data
        """
        if not self.raw_dir.exists():
            return pd.DataFrame()

        all_data = []
        csv_files = list(self.raw_dir.glob("*.csv"))

        for csv_file in csv_files:
            try:
                df = pd.read_csv(csv_file)
                df["swimmer_file"] = csv_file.stem
                all_data.append(df)
            except Exception as e:
                print(f"⚠️  Error reading {csv_file}: {e}")
                continue

        if not all_data:
            return pd.DataFrame()

        return pd.concat(all_data, ignore_index=True)

    def load_probationary_data(self) -> pd.DataFrame:
        """Load probationary swims from processed directory.

        Returns:
            Combined DataFrame with probationary swims
        """
        prob_dir = self.processed_dir / "probationary"
        if not prob_dir.exists():
            return pd.DataFrame()

        all_data = []
        csv_files = list(prob_dir.glob("*.csv"))

        for csv_file in csv_files:
            try:
                df = pd.read_csv(csv_file)
                df["swim_type"] = "probationary"
                all_data.append(df)
            except Exception:
                continue

        if not all_data:
            return pd.DataFrame()

        return pd.concat(all_data, ignore_index=True)

    def filter_team_swims(
        self, df: pd.DataFrame, team_names: list[str]
    ) -> pd.DataFrame:
        """Filter for team-affiliated swims.

        Args:
            df: DataFrame with swim data
            team_names: List of team names to match

        Returns:
            Filtered DataFrame with only team swims
        """
        if df.empty:
            return df

        if "Team" not in df.columns:
            return pd.DataFrame()

        # Match any team name
        mask = df["Team"].str.contains("|".join(team_names), case=False, na=False)
        return df[mask].copy()

    def parse_and_normalize_events(self, df: pd.DataFrame) -> pd.DataFrame:
        """Parse event strings and add normalized columns.

        Adds columns:
            - event_distance: Distance (e.g., "50", "100")
            - event_stroke: Stroke (e.g., "free", "back")
            - event_course: Course (e.g., "scy", "lcm")
            - event_code: Normalized event code (e.g., "50-free")
            - time_seconds: Time in seconds for sorting
            - age_group: Age group (e.g., "10U", "11-12")

        Args:
            df: DataFrame with Event and SwimTime columns

        Returns:
            DataFrame with added columns
        """
        if df.empty or "Event" not in df.columns:
            return df

        # Parse events
        parsed = df["Event"].apply(parse_api_event)
        df["event_distance"] = parsed.apply(lambda x: x[0])
        df["event_stroke"] = parsed.apply(lambda x: x[1])
        df["event_course"] = parsed.apply(lambda x: x[2])

        # Create event codes
        df["event_code"] = df.apply(
            lambda row: (
                create_event_code(row["event_distance"], row["event_stroke"])
                if row["event_distance"] and row["event_stroke"]
                else None
            ),
            axis=1,
        )

        # Convert times to seconds
        if "SwimTime" in df.columns:
            df["time_seconds"] = df["SwimTime"].apply(convert_time_to_seconds)

        # Determine age groups
        if "Age" in df.columns:
            df["age_group"] = df["Age"].apply(determine_age_group)

        return df

    def get_best_times_by_event(
        self, df: pd.DataFrame, course: str
    ) -> dict[str, dict[str, RecordEntry]]:
        """Get best times for each event/age group combination.

        Args:
            df: DataFrame with normalized swim data
            course: Course to filter ("scy", "lcm", "scm")

        Returns:
            Nested dict: {event_code: {age_group: RecordEntry}}
        """
        # Filter by course
        df_course = df[df["event_course"] == course].copy()

        if df_course.empty:
            return {}

        # Remove invalid times
        df_course = df_course[df_course["time_seconds"] < float("inf")]

        # Get event list for course
        if course == "scy":
            event_list = SCY_EVENTS
        elif course == "lcm":
            event_list = LCM_EVENTS
        elif course == "scm":
            event_list = SCM_EVENTS
        else:
            return {}

        records: dict[str, dict[str, RecordEntry]] = {}

        # Process each event
        for event_code in event_list:
            records[event_code] = {}

            # Filter for this event
            df_event = df_course[df_course["event_code"] == event_code]

            if df_event.empty:
                continue

            # Process each age group
            for age_group in AGE_GROUPS:
                if age_group == "Open":
                    # Open includes everyone
                    df_age = df_event.copy()
                else:
                    # Specific age group
                    df_age = df_event[df_event["age_group"] == age_group]

                if df_age.empty:
                    continue

                # Sort by time and get best
                df_age = df_age.sort_values("time_seconds")

                # Get best time per swimmer, then overall best
                df_best_per_swimmer = df_age.drop_duplicates(
                    subset=["Name"], keep="first"
                )

                if df_best_per_swimmer.empty:
                    continue

                # Get overall best
                best = df_best_per_swimmer.iloc[0]

                # Create record entry
                record = RecordEntry(
                    event_code=event_code,
                    age_group=age_group,
                    swimmer_name=best.get("Name", ""),
                    time=best.get("SwimTime", ""),
                    age=str(best.get("Age", "")),
                    date=best.get("SwimDate", ""),
                    meet=best.get("Meet", ""),
                    swim_type=best.get("swim_type", ""),
                    time_seconds=best.get("time_seconds", 0.0),
                )

                records[event_code][age_group] = record

        return records

    def generate_records_markdown(
        self,
        records: dict[str, dict[str, RecordEntry]],
        course: str,
        team_name: str,
        output_path: Path,
    ) -> None:
        """Generate markdown file with records.

        Args:
            records: Records data from get_best_times_by_event
            course: Course ("scy", "lcm", "scm")
            team_name: Team name for title
            output_path: Path to output markdown file
        """
        course_full = {
            "scy": "Short Course Yards",
            "lcm": "Long Course Meters",
            "scm": "Short Course Meters",
        }.get(course, course.upper())

        with open(output_path, "w") as f:
            # Header
            f.write(f"# {team_name}\n")
            f.write(f"## Team Records - {course_full} ({course.upper()})\n\n")
            f.write(
                f"**Generated:** {datetime.now().strftime('%B %d, %Y at %I:%M %p')}\n\n"
            )
            f.write("---\n\n")

            # Legend
            f.write("**Legend:**\n")
            f.write("- ‡ = Probationary period (before joining team)\n\n")
            f.write("---\n\n")

            # Get event list
            if course == "scy":
                event_list = SCY_EVENTS
            elif course == "lcm":
                event_list = LCM_EVENTS
            elif course == "scm":
                event_list = SCM_EVENTS
            else:
                return

            # Write records by event
            for event_code in event_list:
                event_name = format_event_name(event_code)
                f.write(f"### {event_name}\n\n")
                f.write("| Age Group | Time | Athlete | Age | Date | Meet |\n")
                f.write("|-----------|------|---------|-----|------|------|\n")

                event_records = records.get(event_code, {})

                for age_group in AGE_GROUPS:
                    record = event_records.get(age_group)

                    if record:
                        # Add indicator for probationary swims
                        athlete_name = record.swimmer_name
                        if record.swim_type == "probationary":
                            athlete_name += " ‡"

                        # Truncate long meet names
                        meet = record.meet
                        if len(meet) > 45:
                            meet = meet[:42] + "..."

                        f.write(
                            f"| {age_group} | {record.time} | {athlete_name} | "
                            f"{record.age} | {record.date} | {meet} |\n"
                        )
                    else:
                        f.write(f"| {age_group} | — | — | — | — | — |\n")

                f.write("\n")

            # Footer
            f.write("---\n\n")
            f.write(
                f"*Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}*\n"
            )
