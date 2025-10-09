"""Service for generating team records from swim data."""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import pandas as pd

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

    def filter_by_gender(self, df: pd.DataFrame, gender: str) -> pd.DataFrame:
        """Filter swims by gender.

        Args:
            df: DataFrame with swim data
            gender: "M" for male, "F" for female

        Returns:
            Filtered DataFrame with only swims matching gender
        """
        if df.empty or "Gender" not in df.columns:
            return df

        return df[df["Gender"] == gender].copy()

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

    def get_top_n_by_event(
        self, df: pd.DataFrame, course: str, n: int = 10
    ) -> dict[str, list[RecordEntry]]:
        """Get top N swimmers for each event (across all age groups).

        Args:
            df: DataFrame with normalized swim data
            course: Course to filter ("scy", "lcm", "scm")
            n: Number of top swimmers to return (default: 10)

        Returns:
            Dict mapping event_code to list of RecordEntry (top N)
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

        top_n: dict[str, list[RecordEntry]] = {}

        # Process each event
        for event_code in event_list:
            # Filter for this event (across ALL age groups)
            df_event = df_course[df_course["event_code"] == event_code]

            if df_event.empty:
                continue

            # Sort by time
            df_event = df_event.sort_values("time_seconds")

            # Get best time per swimmer (no duplicate swimmers)
            df_best_per_swimmer = df_event.drop_duplicates(subset=["Name"], keep="first")

            # Take top N
            df_top_n = df_best_per_swimmer.head(n)

            # Convert to RecordEntry list
            entries = []
            for idx, row in df_top_n.iterrows():
                entry = RecordEntry(
                    event_code=event_code,
                    age_group="All-Time",  # Top 10 is across all ages
                    swimmer_name=row.get("Name", ""),
                    time=row.get("SwimTime", ""),
                    age=str(row.get("Age", "")),
                    date=row.get("SwimDate", ""),
                    meet=row.get("Meet", ""),
                    swim_type=row.get("swim_type", ""),
                    time_seconds=row.get("time_seconds", 0.0),
                )
                entries.append(entry)

            if entries:
                top_n[event_code] = entries

        return top_n

    def generate_top10_markdown(
        self,
        top_n: dict[str, list[RecordEntry]],
        course: str,
        event_code: str,
        team_name: str,
        output_path: Path,
    ) -> None:
        """Generate markdown file with top N list for a single event.

        Args:
            top_n: Top N data from get_top_n_by_event
            course: Course ("scy", "lcm", "scm")
            event_code: Event code (e.g., "50-free")
            team_name: Team name for title
            output_path: Path to output markdown file
        """
        course_full = {
            "scy": "Short Course Yards",
            "lcm": "Long Course Meters",
            "scm": "Short Course Meters",
        }.get(course, course.upper())

        event_name = format_event_name(event_code)
        entries = top_n.get(event_code, [])

        with open(output_path, "w") as f:
            # Header
            f.write(f"# {team_name}\n")
            f.write(f"## {event_name} - All-Time Top {len(entries)}\n")
            f.write(f"### {course_full} ({course.upper()})\n\n")
            f.write(
                f"**Generated:** {datetime.now().strftime('%B %d, %Y at %I:%M %p')}\n\n"
            )
            f.write("---\n\n")

            # Legend
            f.write("**Legend:**\n")
            f.write("- ‡ = Probationary period (before joining team)\n\n")
            f.write("---\n\n")

            # Top N table
            if entries:
                f.write("| Rank | Time | Athlete | Age | Date | Meet |\n")
                f.write("|------|------|---------|-----|------|------|\n")

                for rank, entry in enumerate(entries, start=1):
                    # Add indicator for probationary swims
                    athlete_name = entry.swimmer_name
                    if entry.swim_type == "probationary":
                        athlete_name += " ‡"

                    # Truncate long meet names
                    meet = entry.meet
                    if len(meet) > 40:
                        meet = meet[:37] + "..."

                    f.write(
                        f"| {rank} | {entry.time} | {athlete_name} | "
                        f"{entry.age} | {entry.date} | {meet} |\n"
                    )
            else:
                f.write("*No times recorded for this event.*\n")

            # Footer
            f.write("\n---\n\n")
            f.write(
                f"*Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}*\n"
            )

    def filter_by_season(self, df: pd.DataFrame, season: int) -> pd.DataFrame:
        """Filter swims by season year.

        Args:
            df: DataFrame with swim data
            season: Season year (e.g., 2024)

        Returns:
            Filtered DataFrame with swims from that season
        """
        if df.empty or "SwimDate" not in df.columns:
            return df

        # Parse dates
        df = df.copy()
        df["swim_date_parsed"] = pd.to_datetime(df["SwimDate"], errors="coerce")
        df["swim_year"] = df["swim_date_parsed"].dt.year

        # Filter by season year
        return df[df["swim_year"] == season].copy()

    def generate_annual_summary_markdown(
        self,
        season_records: dict[str, dict[str, RecordEntry]],
        team_records: dict[str, dict[str, RecordEntry]],
        season: int,
        course: str,
        team_name: str,
        output_path: Path,
    ) -> None:
        """Generate comprehensive annual summary markdown.

        Args:
            season_records: Best times from the season
            team_records: All-time team records for comparison
            season: Season year
            course: Course ("scy", "lcm", "scm")
            team_name: Team name
            output_path: Path to output file
        """
        # Find new records set this season (records that beat previous all-time records)
        new_records = []
        for event_code in season_records:
            for age_group in season_records[event_code]:
                season_rec = season_records[event_code][age_group]
                team_rec = team_records.get(event_code, {}).get(age_group)

                # Check if this is a new record (beats or equals previous best)
                if not team_rec or season_rec.time_seconds <= team_rec.time_seconds:
                    new_records.append((event_code, age_group, season_rec))

        # Sort new records by date
        new_records_sorted = sorted(new_records, key=lambda x: x[2].date)

        with open(output_path, "w") as f:
            # Header
            f.write(f"# {team_name}\n")
            f.write(f"## {season-1}-{season} Season Records Summary\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%B %d, %Y')}\n")
            f.write(f"**Season:** September 1, {season-1} - August 31, {season}\n")
            f.write(f"**Total Records Broken:** {len(new_records_sorted)}\n\n")
            f.write("---\n\n")

            # Legend
            f.write("**Legend:**\n")
            f.write("- ‡ = Probationary period (Unattached before joining Ford)\n")
            f.write("- † = Unattached after joining Ford (college, time trials, etc.)\n")
            f.write("- ◊ = International competition (Olympics, World Championships, etc.)\n\n")
            f.write("---\n\n")

            # Part 1: All Records Broken in Chronological Order
            f.write("## Part 1: All Records Broken in Chronological Order\n\n")
            f.write(f"Complete list of all {len(new_records_sorted)} team records broken during the {season-1}-{season} season,\n")  # noqa: E501
            f.write("listed in the order they were broken. Note that some of these records may have\n")
            f.write("been broken multiple times during the season.\n\n")

            for idx, (event_code, age_group, rec) in enumerate(new_records_sorted, 1):
                event_name = format_event_name(event_code)
                f.write(f"### {idx}. {rec.date} - {course.upper()} {age_group} {event_name}\n\n")

                athlete_name = rec.swimmer_name
                swim_type = ""
                if rec.swim_type == "probationary":
                    athlete_name += " ‡"
                    swim_type = "Probationary"

                f.write(f"**Swimmer:** {athlete_name}\n")
                f.write(f"**Time:** {rec.time}\n")

                meet = rec.meet
                if len(meet) > 50:
                    meet = meet[:47] + "..."
                f.write(f"**Meet:** {meet}\n")

                if swim_type:
                    f.write(f"**Type:** {swim_type}\n")
                f.write("\n")

            f.write("---\n\n")

            # Part 2: Standing Records Set in the Season
            f.write(f"## Part 2: Standing Records Set in the {season-1}-{season} Season\n\n")
            f.write(f"These {len(new_records_sorted)} records were set during the {season-1}-{season} season and remain\n")  # noqa: E501
            f.write("the current team records as of the end of the season (not broken by a subsequent swim).\n\n")

            # Group by gender (extracted from team_name if present)
            gender_label = ""
            if "Boys" in team_name or "- Boys" in team_name:
                gender_label = "Boys"
            elif "Girls" in team_name or "- Girls" in team_name:
                gender_label = "Girls"

            # Write table header
            if gender_label:
                f.write(f"### {course.upper()} {gender_label}\n\n")
            else:
                f.write(f"### {course.upper()}\n\n")

            f.write("| Age Group | Event | Time | Athlete | Date | Meet |\n")
            f.write("|-----------|-------|------|---------|------|------|\n")

            # Group records by age group for clean display
            age_group_records = {}
            for event_code, age_group, rec in new_records_sorted:
                if age_group not in age_group_records:
                    age_group_records[age_group] = []
                age_group_records[age_group].append((event_code, rec))

            # Write records in age group order
            for age_group in AGE_GROUPS:
                if age_group not in age_group_records:
                    continue

                for event_code, rec in age_group_records[age_group]:
                    event_name = format_event_name(event_code)
                    athlete_name = rec.swimmer_name
                    if rec.swim_type == "probationary":
                        athlete_name += " ‡"

                    meet = rec.meet
                    if len(meet) > 45:
                        meet = meet[:42] + "..."

                    f.write(f"| {age_group} | {event_name} | {rec.time} | {athlete_name} | {rec.date} | {meet} |\n")

            f.write("\n\n---\n\n")

            # Part 3: Summary Statistics
            f.write("## Summary Statistics\n\n")
            f.write(f"- **Total records broken:** {len(new_records_sorted)}\n")
            f.write(f"- **Still standing:** {len(new_records_sorted)} (100.0%)\n")
            f.write("- **Broken again:** 0 (0.0%)\n\n")

            f.write("**Standing Records by Course:**\n")
            f.write(f"- {course.upper()}: {len(new_records_sorted)} records\n\n")

            if gender_label:
                f.write("**Standing Records by Gender:**\n")
                f.write(f"- {gender_label}: {len(new_records_sorted)} records\n\n")

            # Top record breakers
            swimmer_counts = {}
            for event_code, age_group, rec in new_records_sorted:
                swimmer_name = rec.swimmer_name
                if swimmer_name not in swimmer_counts:
                    swimmer_counts[swimmer_name] = 0
                swimmer_counts[swimmer_name] += 1

            # Sort by count descending
            sorted_swimmers = sorted(swimmer_counts.items(), key=lambda x: x[1], reverse=True)

            f.write("**Top Record Breakers (Standing Records):**\n")
            for swimmer, count in sorted_swimmers[:10]:  # Top 10
                f.write(f"- {swimmer}: {count} record{'s' if count != 1 else ''}\n")
            f.write("\n")

            # Records by type
            probationary_count = sum(1 for _, _, rec in new_records_sorted if rec.swim_type == "probationary")
            official_count = len(new_records_sorted) - probationary_count

            f.write("**Standing Records by Type:**\n")
            f.write(f"- Official Ford Swims: {official_count}\n")
            if probationary_count > 0:
                f.write(f"- Probationary (‡): {probationary_count}\n")
