"""Roster command - Fetch team roster from USA Swimming."""

import os
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from swim_data_tool.api import USASwimmingAPI

console = Console()


class RosterCommand:
    """Fetch team roster and export to CSV."""

    def __init__(self, cwd: Path, seasons: list[str] | None = None, output: str | None = None):
        self.cwd = cwd
        self.seasons = seasons
        self.output = output
        self.api = USASwimmingAPI()

    def run(self) -> None:
        """Execute the roster command."""
        # Check if initialized
        env_file = self.cwd / ".env"
        if not env_file.exists():
            console.print("[red]Error: Not initialized. Run 'swim-data-tool init' first.[/red]")
            return

        # Get team code from environment
        team_code = os.getenv("USA_SWIMMING_TEAM_CODE")
        team_name = os.getenv("CLUB_NAME")
        start_year = os.getenv("START_YEAR", "2015")
        end_year = os.getenv("END_YEAR", "2025")
        
        if not team_code:
            console.print("[red]Error: USA_SWIMMING_TEAM_CODE not found in .env[/red]")
            return

        console.print(f"\n[cyan]Fetching roster for:[/cyan] {team_name} ({team_code})")
        
        # Handle --seasons=all
        seasons = self.seasons
        if seasons and len(seasons) == 1 and seasons[0].lower() == "all":
            # Generate all years from START_YEAR to END_YEAR
            seasons = [str(year) for year in range(int(start_year), int(end_year) + 1)]
            console.print(f"[dim]Seasons: {start_year}-{end_year} (all available)[/dim]\n")
        elif seasons:
            console.print(f"[dim]Seasons: {', '.join(seasons)}[/dim]\n")
        else:
            console.print("[dim]Seasons: 2024-2025 (default)[/dim]\n")

        # Fetch roster
        with console.status("[bold cyan]Querying USA Swimming API..."):
            roster_df = self.api.get_team_roster(team_code, seasons)

        if roster_df.empty:
            console.print("[yellow]No swimmers found for this team.[/yellow]")
            console.print("[dim]Try different seasons with --seasons option[/dim]")
            return

        # Display results
        console.print(f"[green]✓ Found {len(roster_df)} swimmers[/green]\n")

        # Show preview table
        table = Table(title="Team Roster Preview (first 20)")
        table.add_column("PersonKey", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("First Swim", style="dim")
        table.add_column("Last Swim", style="yellow")
        table.add_column("Swims", justify="right", style="blue")

        for _, row in roster_df.head(20).iterrows():
            table.add_row(
                str(row["PersonKey"]),
                row["FullName"],
                str(row["FirstSwimDate"]),
                str(row["LastSwimDate"]),
                str(row["SwimCount"]),
            )

        console.print(table)
        console.print()

        # Determine output filename
        if self.output:
            output_file = Path(self.output)
        else:
            output_file = self.cwd / "data" / "lookups" / "roster.csv"
            output_file.parent.mkdir(parents=True, exist_ok=True)

        # Save to CSV
        roster_df.to_csv(output_file, index=False)
        console.print(f"[green]✓ Saved roster to:[/green] {output_file}")
        
        # Show next steps in a nice panel
        next_steps = f"""To import all {len(roster_df)} swimmers:
   [cyan]swim-data-tool import swimmers[/cyan]

Or test with a few swimmers first:
   [cyan]swim-data-tool import swimmer <PERSON_KEY>[/cyan]

Example:
   [cyan]swim-data-tool import swimmer {roster_df.iloc[0]['PersonKey']}[/cyan]  # {roster_df.iloc[0]['FullName']}"""
        
        console.print()
        console.print(Panel(
            next_steps,
            title="Next Steps",
            border_style="green"
        ))
