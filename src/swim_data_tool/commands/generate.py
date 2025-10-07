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
