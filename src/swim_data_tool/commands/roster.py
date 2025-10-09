"""Roster command - Fetch team roster from any data source."""

import os
from pathlib import Path

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from swim_data_tool.sources.factory import get_source

console = Console()


class RosterCommand:
    """Fetch team roster and export to CSV."""

    def __init__(
        self,
        cwd: Path,
        seasons: list[str] | None = None,
        output: str | None = None,
        source: str | None = None,
        start_season: str | None = None,
        end_season: str | None = None,
    ):
        self.cwd = cwd
        self.seasons = seasons
        self.output = output
        self.source_name = source
        self.start_season = start_season
        self.end_season = end_season

    def _expand_season_range(self, start: str, end: str) -> list[str]:
        """Expand season range to list of seasons.

        Args:
            start: Start season (e.g., "12-13")
            end: End season (e.g., "25-26")

        Returns:
            List of seasons (e.g., ["12-13", "13-14", ..., "25-26"])
        """
        # Parse start and end years
        start_first, start_second = map(int, start.split("-"))
        end_first, end_second = map(int, end.split("-"))

        # Handle century boundary (e.g., 99-00 transitions to 00-01)
        # Assume all seasons are in 2000s for now
        if start_first > end_first:
            # Start is in 1900s or wraps century
            start_first += 1900 if start_first >= 90 else 2000
        else:
            start_first += 2000

        if end_first < 50:
            end_first += 2000
        else:
            end_first += 1900

        # Generate all seasons in range
        seasons = []
        for year in range(start_first, end_first + 1):
            year_str = f"{year % 100:02d}"
            next_year_str = f"{(year + 1) % 100:02d}"
            seasons.append(f"{year_str}-{next_year_str}")

        return seasons

    def run(self) -> None:
        """Execute the roster command."""
        # Check if initialized
        env_file = self.cwd / ".env"
        if not env_file.exists():
            console.print("[red]Error: Not initialized. Run 'swim-data-tool init' first.[/red]")
            return

        # Load environment variables from .env file
        load_dotenv(env_file)

        # Get data source
        try:
            source = get_source(self.source_name)
        except ValueError as e:
            console.print(f"[red]Error: {e}[/red]")
            return

        console.print("\n[bold cyan]🏊 Fetching Roster[/bold cyan]")
        console.print(f"[dim]Data source: {source.source_name}[/dim]\n")

        # Get source-specific configuration
        team_name = os.getenv("CLUB_NAME", "Team")

        if source.source_name == "USA Swimming":
            team_code = os.getenv("USA_SWIMMING_TEAM_CODE")
            if not team_code:
                console.print("[red]Error: USA_SWIMMING_TEAM_CODE not found in .env[/red]")
                return
            team_id = team_code
            start_year = os.getenv("START_YEAR", "2015")
            end_year = os.getenv("END_YEAR", "2025")
        elif source.source_name == "MaxPreps":
            school_slug = os.getenv("MAXPREPS_SCHOOL_SLUG")
            if not school_slug:
                console.print("[red]Error: MAXPREPS_SCHOOL_SLUG not found in .env[/red]")
                return
            team_id = school_slug
            start_year = None
            end_year = None
        else:
            console.print(f"[red]Error: Unknown source: {source.source_name}[/red]")
            return

        console.print(f"[cyan]Team:[/cyan] {team_name}")
        console.print(f"[cyan]Team ID:[/cyan] {team_id}")

        # Handle season range (--start-season and --end-season)
        seasons = self.seasons
        if self.start_season or self.end_season:
            if not (self.start_season and self.end_season):
                console.print("[red]Error: Both --start-season and --end-season must be provided together[/red]")
                return
            # Expand season range
            seasons = self._expand_season_range(self.start_season, self.end_season)
            console.print(f"[dim]Seasons: {self.start_season} to {self.end_season} ({len(seasons)} seasons)[/dim]\n")
        elif seasons and len(seasons) == 1 and seasons[0].lower() == "all":
            # Generate all years from START_YEAR to END_YEAR
            seasons = [str(year) for year in range(int(start_year), int(end_year) + 1)]
            console.print(f"[dim]Seasons: {start_year}-{end_year} (all available)[/dim]\n")
        elif seasons:
            # Expand any year ranges (e.g., "2020-2025" -> ["2020", "2021", ..., "2025"])
            expanded_seasons = []
            for season in seasons:
                if "-" in season and season.lower() != "all":
                    # Parse year range
                    try:
                        parts = season.split("-")
                        if len(parts) == 2:
                            range_start = int(parts[0])
                            range_end = int(parts[1])
                            expanded_seasons.extend([str(year) for year in range(range_start, range_end + 1)])
                        else:
                            # Not a valid range, keep as-is
                            expanded_seasons.append(season)
                    except ValueError:
                        # Not a valid range, keep as-is
                        expanded_seasons.append(season)
                else:
                    expanded_seasons.append(season)

            seasons = expanded_seasons

            # Show concise range if consecutive years
            if len(seasons) > 3 and all(seasons[i] == str(int(seasons[i - 1]) + 1) for i in range(1, len(seasons))):
                console.print(f"[dim]Seasons: {seasons[0]}-{seasons[-1]}[/dim]\n")
            else:
                console.print(f"[dim]Seasons: {', '.join(seasons)}[/dim]\n")
        else:
            console.print("[dim]Seasons: 2024-2025 (default)[/dim]\n")

        # Fetch roster
        with console.status(f"[bold cyan]Fetching roster from {source.source_name}..."):
            roster_df = source.get_team_roster(team_id, seasons)

        if roster_df.empty:
            console.print("[yellow]No swimmers found for this team.[/yellow]")
            console.print("[dim]Try different seasons with --seasons option[/dim]")
            return

        # Display results
        console.print(f"[green]✓ Found {len(roster_df)} swimmers[/green]")

        # Count genders
        if "gender" in roster_df.columns or "Gender" in roster_df.columns:
            gender_col = "gender" if "gender" in roster_df.columns else "Gender"

            # Filter out relays for USA Swimming (PersonKey=0)
            if source.swimmer_id_field == "PersonKey":
                gender_counts = roster_df[roster_df["PersonKey"] != 0][gender_col].value_counts()
            else:
                gender_counts = roster_df[gender_col].value_counts()

            males = gender_counts.get("M", 0)
            females = gender_counts.get("F", 0)
            if males > 0 or females > 0:
                console.print(f"[green]✓ Gender data: {males} males, {females} females[/green]\n")
            else:
                console.print("[yellow]⚠ No gender data found in results[/yellow]\n")
        else:
            console.print("[yellow]⚠ Gender column not available[/yellow]\n")

        # Show preview table (source-agnostic)
        table = Table(title="Team Roster Preview (first 20)")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Gender", style="magenta", justify="center")

        # Add source-specific columns
        if source.source_name == "USA Swimming":
            table.add_column("First Swim", style="dim")
            table.add_column("Last Swim", style="yellow")
            table.add_column("Swims", justify="right", style="blue")
        elif source.source_name == "MaxPreps":
            table.add_column("Grade", style="yellow", justify="center")
            table.add_column("Season", style="dim")

        for _, row in roster_df.head(20).iterrows():
            # Get swimmer ID
            swimmer_id = str(row.get(source.swimmer_id_field, ""))

            # Get name (handle different column names)
            name = row.get("swimmer_name", row.get("FullName", ""))

            # Get gender
            gender = row.get("gender", row.get("Gender", ""))
            gender_display = "M" if gender == "M" else "F" if gender == "F" else "?"

            # Build row based on source
            if source.source_name == "USA Swimming":
                table.add_row(
                    swimmer_id,
                    name,
                    gender_display,
                    str(row.get("FirstSwimDate", "")),
                    str(row.get("LastSwimDate", "")),
                    str(row.get("SwimCount", "")),
                )
            elif source.source_name == "MaxPreps":
                table.add_row(
                    swimmer_id,
                    name,
                    gender_display,
                    str(row.get("grade", "")),
                    str(row.get("season", "")),
                )

        console.print(table)
        console.print()

        # Determine output filename
        if self.output:
            output_file = Path(self.output)
        else:
            # Use source-specific filename
            source_suffix = source.source_name.lower().replace(" ", "-")
            output_file = self.cwd / "data" / "lookups" / f"roster-{source_suffix}.csv"
            output_file.parent.mkdir(parents=True, exist_ok=True)

        # Save to CSV
        roster_df.to_csv(output_file, index=False)
        console.print(f"[green]✓ Saved roster to:[/green] {output_file}")

        # Show next steps in a nice panel
        first_swimmer_id = str(roster_df.iloc[0][source.swimmer_id_field])
        first_swimmer_name = roster_df.iloc[0].get("swimmer_name", roster_df.iloc[0].get("FullName", ""))

        source_flag = f" --source={self.source_name}" if self.source_name else ""

        next_steps = f"""To import all {len(roster_df)} swimmers:
   [cyan]swim-data-tool import swimmers{source_flag}[/cyan]

Or test with a few swimmers first:
   [cyan]swim-data-tool import swimmer <ID>{source_flag}[/cyan]

Example:
   [cyan]swim-data-tool import swimmer {first_swimmer_id}{source_flag}[/cyan]  # {first_swimmer_name}"""

        console.print()
        console.print(Panel(next_steps, title="Next Steps", border_style="green", expand=False))
