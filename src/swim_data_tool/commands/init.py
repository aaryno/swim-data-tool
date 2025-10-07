"""Initialize command - Set up new team repository."""

from pathlib import Path
from rich.console import Console

console = Console()


class InitCommand:
    """Initialize a new team repository with proper structure."""
    
    def __init__(self, team_name: str, cwd: Path):
        self.team_name = team_name
        self.cwd = cwd
    
    def run(self) -> None:
        """Execute the init command."""
        console.print("[yellow]⚠️  Init command not yet implemented[/yellow]")
        console.print(f"Team: {self.team_name}")
        console.print(f"Directory: {self.cwd}")
        console.print("\n[dim]Coming soon in v0.1.0[/dim]\n")
