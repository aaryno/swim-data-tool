"""Status command - Show current status and configuration."""

import os
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from swim_data_tool.version import __version__

console = Console()


class StatusCommand:
    """Show current status and configuration."""

    def __init__(self, cwd: Path):
        self.cwd = cwd

    def run(self) -> None:
        """Execute the status command."""
        console.print()
        console.print(Panel.fit("[bold cyan]Swim Data Tool[/bold cyan]", subtitle=f"v{__version__}"))
        console.print()

        # Check for .env file
        env_file = self.cwd / ".env"
        if not env_file.exists():
            console.print("[yellow]⚠️  No .env file found in current directory[/yellow]")
            console.print("[dim]Run 'swim-data-tool init <team-name>' to initialize[/dim]\n")
            return

        # Display basic info
        table = Table(title="Current Configuration")
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="white")

        club_name = os.getenv("CLUB_NAME", "Not set")
        club_abbr = os.getenv("CLUB_ABBREVIATION", "Not set")
        data_dir = os.getenv("DATA_DIR", "data")

        table.add_row("Club Name", club_name)
        table.add_row("Abbreviation", club_abbr)
        table.add_row("Data Directory", data_dir)
        table.add_row("Working Directory", str(self.cwd))

        console.print(table)
        console.print()

        # Check data directories
        data_path = self.cwd / data_dir
        if data_path.exists():
            console.print(f"[green]✅[/green] Data directory exists: {data_path}")
        else:
            console.print(f"[yellow]⚠️[/yellow]  Data directory not found: {data_path}")

        console.print()


class ConfigCommand:
    """View current configuration from .env file."""

    def __init__(self, cwd: Path):
        self.cwd = cwd

    def run(self) -> None:
        """Execute the config command."""
        env_file = self.cwd / ".env"

        if not env_file.exists():
            console.print("[yellow]⚠️  No .env file found in current directory[/yellow]")
            console.print("[dim]Run 'swim-data-tool init <team-name>' to initialize[/dim]\n")
            return

        console.print()
        console.print(Panel.fit("[bold cyan]Current Configuration (.env)[/bold cyan]"))
        console.print()

        # Read and display .env file
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    console.print(f"  {line}")
                elif line.startswith("#"):
                    console.print(f"[dim]{line}[/dim]")

        console.print()
