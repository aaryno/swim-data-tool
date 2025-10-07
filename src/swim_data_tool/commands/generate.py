"""Generate records command."""

import os
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from swim_data_tool.services.record_generator import RecordGenerator

console = Console()


class GenerateRecordsCommand:
    """Generate team records from swim data."""

    def __init__(self, cwd: Path, course: str | None = None):
        """Initialize command.

        Args:
            cwd: Current working directory
            course: Course to generate ("scy", "lcm", "scm", or None for all)
        """
        self.cwd = Path(cwd)
        self.course = course

        # Load config from .env
        self.team_name = os.getenv("CLUB_NAME", "Swim Team")
        team_names_str = os.getenv("USA_SWIMMING_TEAM_NAMES", "")
        self.team_names = [name.strip() for name in team_names_str.split(",")]

        self.data_dir = self.cwd / "data"
        self.records_dir = self.data_dir / "records"

    def run(self) -> None:
        """Execute the command."""
        console.print("\n[bold cyan]🏊 Generating Team Records[/bold cyan]\n")

        # Verify data directory exists
        if not self.data_dir.exists():
            console.print("[red]❌ Data directory not found.[/red]")
            console.print(
                "[yellow]Run 'swim-data-tool init' first to set up your team.[/yellow]"
            )
            return

        # Create records directory
        self.records_dir.mkdir(exist_ok=True)

        # Initialize generator
        generator = RecordGenerator(self.data_dir)

        # Load data
        console.print("[cyan]📂 Loading swimmer data...[/cyan]")
        df_all = generator.load_all_swimmer_data()

        if df_all.empty:
            console.print("[yellow]⚠️  No swimmer data found.[/yellow]")
            console.print(
                "[yellow]Run 'swim-data-tool import swimmers' to download data.[/yellow]"
            )
            return

        console.print(f"[green]✓[/green] Loaded {len(df_all):,} swims\n")

        # Filter for team swims
        console.print("[cyan]🔍 Filtering team swims...[/cyan]")
        df_team = generator.filter_team_swims(df_all, self.team_names)
        console.print(f"[green]✓[/green] Found {len(df_team):,} team swims\n")

        # Parse and normalize events
        console.print("[cyan]⚙️  Parsing events...[/cyan]")
        df_normalized = generator.parse_and_normalize_events(df_team)
        console.print(f"[green]✓[/green] Parsed events\n")

        # Determine which courses to process
        if self.course:
            courses = [self.course]
        else:
            courses = ["scy", "lcm", "scm"]

        # Generate records for each course
        for course in courses:
            console.print(f"[cyan]📊 Generating {course.upper()} records...[/cyan]")

            # Get best times
            records = generator.get_best_times_by_event(df_normalized, course)

            if not records:
                console.print(f"[yellow]⚠️  No {course.upper()} data found.[/yellow]\n")
                continue

            # Count total records
            total_records = sum(len(age_records) for age_records in records.values())
            console.print(f"[green]✓[/green] Found {total_records} records\n")

            # Create course directory
            course_dir = self.records_dir / course
            course_dir.mkdir(exist_ok=True)

            # Generate markdown
            output_path = course_dir / "records.md"
            generator.generate_records_markdown(
                records, course, self.team_name, output_path
            )

            console.print(
                f"[green]✅ Generated:[/green] {output_path.relative_to(self.cwd)}\n"
            )

        # Summary
        console.print("[bold green]✓ Record Generation Complete![/bold green]\n")

        # Display summary table
        table = Table(title="Generated Files")
        table.add_column("Course", style="cyan")
        table.add_column("File", style="green")

        for course in courses:
            file_path = self.records_dir / course / "records.md"
            if file_path.exists():
                table.add_row(course.upper(), str(file_path.relative_to(self.cwd)))

        console.print(table)
        
        # Show next steps
        view_commands = []
        for course in courses:
            file_path = self.records_dir / course / "records.md"
            if file_path.exists():
                view_commands.append(f"   [cyan]cat {file_path.relative_to(self.cwd)}[/cyan]")
        
        next_steps = f"""1. View your team records:
{chr(10).join(view_commands)}

2. Share records:
   Copy the markdown files to your team website or GitHub
   Files are in: [cyan]data/records/[/cyan]

3. Update records after new meets:
   [cyan]swim-data-tool import swimmers[/cyan]
   [cyan]swim-data-tool classify unattached[/cyan]
   [cyan]swim-data-tool generate records[/cyan]"""
        
        console.print()
        console.print(Panel(
            next_steps,
            title="Next Steps",
            border_style="green"
        ))


class GenerateTop10Command:
    """Generate top 10 all-time lists from swim data."""

    def __init__(self, cwd: Path, course: str | None = None, n: int = 10):
        """Initialize command.

        Args:
            cwd: Current working directory
            course: Course to generate ("scy", "lcm", "scm", or None for all)
            n: Number of swimmers to include (default: 10)
        """
        self.cwd = Path(cwd)
        self.course = course
        self.n = n

        # Load config from .env
        self.team_name = os.getenv("CLUB_NAME", "Swim Team")
        team_names_str = os.getenv("USA_SWIMMING_TEAM_NAMES", "")
        self.team_names = [name.strip() for name in team_names_str.split(",")]

        self.data_dir = self.cwd / "data"
        self.records_dir = self.data_dir / "records"

    def run(self) -> None:
        """Execute the command."""
        console.print(f"\n[bold cyan]🏆 Generating Top {self.n} Lists[/bold cyan]\n")

        # Verify data directory exists
        if not self.data_dir.exists():
            console.print("[red]❌ Data directory not found.[/red]")
            console.print(
                "[yellow]Run 'swim-data-tool init' first to set up your team.[/yellow]"
            )
            return

        # Create records directory
        self.records_dir.mkdir(exist_ok=True)

        # Initialize generator
        generator = RecordGenerator(self.data_dir)

        # Load data
        console.print("[cyan]📂 Loading swimmer data...[/cyan]")
        df_all = generator.load_all_swimmer_data()

        if df_all.empty:
            console.print("[yellow]⚠️  No swimmer data found.[/yellow]")
            console.print(
                "[yellow]Run 'swim-data-tool import swimmers' to download data.[/yellow]"
            )
            return

        console.print(f"[green]✓[/green] Loaded {len(df_all):,} swims\n")

        # Filter for team swims
        console.print("[cyan]🔍 Filtering team swims...[/cyan]")
        df_team = generator.filter_team_swims(df_all, self.team_names)
        console.print(f"[green]✓[/green] Found {len(df_team):,} team swims\n")

        # Parse and normalize events
        console.print("[cyan]⚙️  Parsing events...[/cyan]")
        df_normalized = generator.parse_and_normalize_events(df_team)
        console.print(f"[green]✓[/green] Parsed events\n")

        # Determine which courses to process
        if self.course:
            courses = [self.course]
        else:
            courses = ["scy", "lcm", "scm"]

        # Track generated files
        generated_files = []

        # Generate top N for each course
        for course in courses:
            console.print(f"[cyan]📊 Generating {course.upper()} top {self.n} lists...[/cyan]")

            # Get top N for all events
            top_n = generator.get_top_n_by_event(df_normalized, course, self.n)

            if not top_n:
                console.print(f"[yellow]⚠️  No {course.upper()} data found.[/yellow]\n")
                continue

            console.print(f"[green]✓[/green] Found data for {len(top_n)} events\n")

            # Create course directory
            course_dir = self.records_dir / "top10" / course
            course_dir.mkdir(parents=True, exist_ok=True)

            # Generate markdown for each event
            for event_code, entries in top_n.items():
                output_path = course_dir / f"{event_code}.md"
                generator.generate_top10_markdown(
                    top_n, course, event_code, self.team_name, output_path
                )
                generated_files.append((course.upper(), output_path.relative_to(self.cwd)))

            console.print(
                f"[green]✅ Generated {len(top_n)} event files for {course.upper()}[/green]\n"
            )

        # Summary
        console.print(f"[bold green]✓ Top {self.n} Generation Complete![/bold green]\n")

        # Display summary table
        if generated_files:
            table = Table(title=f"Generated Top {self.n} Files")
            table.add_column("Course", style="cyan")
            table.add_column("Files", style="green")

            # Group by course
            course_counts = {}
            for course, _ in generated_files:
                course_counts[course] = course_counts.get(course, 0) + 1

            for course, count in course_counts.items():
                table.add_row(course, f"{count} event files")

            console.print(table)

            # Show next steps
            example_file = generated_files[0][1] if generated_files else None
            
            next_steps = f"""1. View top {self.n} lists:
   [cyan]cat {example_file}[/cyan]
   [cyan]ls data/records/top10/[/cyan]

2. Generate team records (if not done):
   [cyan]swim-data-tool generate records[/cyan]

3. Create annual summaries:
   [cyan]swim-data-tool generate annual --season=2024[/cyan]

4. Publish records to GitHub:
   [cyan]swim-data-tool publish[/cyan]"""

            console.print()
            console.print(Panel(
                next_steps,
                title="Next Steps",
                border_style="green"
            ))
        else:
            console.print("[yellow]No files generated. Check your data.[/yellow]")


class GenerateAnnualCommand:
    """Generate annual season summary."""

    def __init__(self, cwd: Path, season: int, course: str | None = None):
        """Initialize command.

        Args:
            cwd: Current working directory
            season: Season year (e.g., 2024)
            course: Course to generate ("scy", "lcm", "scm", or None for all)
        """
        self.cwd = Path(cwd)
        self.season = season
        self.course = course

        # Load config from .env
        self.team_name = os.getenv("CLUB_NAME", "Swim Team")
        team_names_str = os.getenv("USA_SWIMMING_TEAM_NAMES", "")
        self.team_names = [name.strip() for name in team_names_str.split(",")]

        self.data_dir = self.cwd / "data"
        self.records_dir = self.data_dir / "records"

    def run(self) -> None:
        """Execute the command."""
        console.print(f"\n[bold cyan]📅 Generating {self.season} Season Summary[/bold cyan]\n")

        # Verify data directory exists
        if not self.data_dir.exists():
            console.print("[red]❌ Data directory not found.[/red]")
            console.print(
                "[yellow]Run 'swim-data-tool init' first to set up your team.[/yellow]"
            )
            return

        # Create records directory
        self.records_dir.mkdir(exist_ok=True)

        # Initialize generator
        generator = RecordGenerator(self.data_dir)

        # Load all data
        console.print("[cyan]📂 Loading swimmer data...[/cyan]")
        df_all = generator.load_all_swimmer_data()

        if df_all.empty:
            console.print("[yellow]⚠️  No swimmer data found.[/yellow]")
            console.print(
                "[yellow]Run 'swim-data-tool import swimmers' to download data.[/yellow]"
            )
            return

        console.print(f"[green]✓[/green] Loaded {len(df_all):,} swims\n")

        # Filter for team swims
        console.print("[cyan]🔍 Filtering team swims...[/cyan]")
        df_team = generator.filter_team_swims(df_all, self.team_names)
        console.print(f"[green]✓[/green] Found {len(df_team):,} team swims\n")

        # Parse and normalize events
        console.print("[cyan]⚙️  Parsing events...[/cyan]")
        df_normalized = generator.parse_and_normalize_events(df_team)
        console.print(f"[green]✓[/green] Parsed events\n")

        # Filter by season
        console.print(f"[cyan]📆 Filtering {self.season} season data...[/cyan]")
        df_season = generator.filter_by_season(df_normalized, self.season)
        
        if df_season.empty:
            console.print(f"[yellow]⚠️  No data found for {self.season} season.[/yellow]")
            console.print(f"[yellow]Check that swimmers have data with SwimDate in {self.season}.[/yellow]")
            return

        console.print(f"[green]✓[/green] Found {len(df_season):,} swims from {self.season}\n")

        # Determine which courses to process
        if self.course:
            courses = [self.course]
        else:
            courses = ["scy", "lcm", "scm"]

        # Track generated files
        generated_files = []

        # Generate summary for each course
        for course in courses:
            console.print(f"[cyan]📊 Generating {course.upper()} summary for {self.season}...[/cyan]")

            # Get best times for the season
            season_records = generator.get_best_times_by_event(df_season, course)

            if not season_records:
                console.print(f"[yellow]⚠️  No {course.upper()} data found for {self.season}.[/yellow]\n")
                continue

            # Get all-time team records for comparison
            team_records = generator.get_best_times_by_event(df_normalized, course)

            # Count season records
            total_season_records = sum(len(age_records) for age_records in season_records.values())
            console.print(f"[green]✓[/green] Found {total_season_records} season bests\n")

            # Create annual directory
            annual_dir = self.records_dir / "annual"
            annual_dir.mkdir(exist_ok=True)

            # Generate markdown
            output_path = annual_dir / f"{self.season}-{course}.md"
            generator.generate_annual_summary_markdown(
                season_records, team_records, self.season, course, self.team_name, output_path
            )

            console.print(
                f"[green]✅ Generated:[/green] {output_path.relative_to(self.cwd)}\n"
            )
            generated_files.append((course.upper(), output_path.relative_to(self.cwd)))

        # Summary
        if generated_files:
            console.print(f"[bold green]✓ {self.season} Season Summary Complete![/bold green]\n")

            # Display summary table
            table = Table(title=f"{self.season} Season Summaries")
            table.add_column("Course", style="cyan")
            table.add_column("File", style="green")

            for course, file_path in generated_files:
                table.add_row(course, str(file_path))

            console.print(table)

            # Show next steps
            example_file = generated_files[0][1] if generated_files else None
            
            next_steps = f"""1. View {self.season} season summary:
   [cyan]cat {example_file}[/cyan]

2. Generate summaries for other seasons:
   [cyan]swim-data-tool generate annual --season=2023[/cyan]
   [cyan]swim-data-tool generate annual --season=2025[/cyan]

3. Generate top 10 lists (if not done):
   [cyan]swim-data-tool generate top10[/cyan]

4. Publish records to GitHub:
   [cyan]swim-data-tool publish[/cyan]"""

            console.print()
            console.print(Panel(
                next_steps,
                title="Next Steps",
                border_style="green"
            ))
        else:
            console.print(f"[yellow]No summaries generated for {self.season}. Check your data.[/yellow]")
