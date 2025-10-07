"""Import swimmer command - Download data for a single swimmer."""

import os
from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.prompt import IntPrompt

from swim_data_tool.api import USASwimmingAPI

console = Console()


class ImportSwimmerCommand:
    """Import career data for a single swimmer."""

    def __init__(self, person_key: int, cwd: Path):
        self.person_key = person_key
        self.cwd = cwd
        self.api = USASwimmingAPI()

    def run(self) -> None:
        """Execute the import swimmer command."""
        # Get configuration
        start_year = int(os.getenv("START_YEAR", "1998"))
        end_year = int(os.getenv("END_YEAR", str(datetime.now().year)))

        console.print(
            f"\n[cyan]Downloading career data for PersonKey {self.person_key}...[/cyan]"
        )
        console.print(f"  Years: {start_year}-{end_year}\n")

        try:
            # Download swimmer data
            df = self.api.download_swimmer_career(
                person_key=self.person_key,
                start_year=start_year,
                end_year=end_year,
            )

            if df.empty:
                console.print(
                    "[yellow]No swims found for this PersonKey[/yellow]"
                )
                console.print(
                    "  Swimmer may have no USA Swimming times in this date range\n"
                )
                return

            # Get swimmer name from first row
            swimmer_name = df["Name"].iloc[0] if "Name" in df.columns else "unknown"
            safe_name = self._sanitize_filename(swimmer_name)

            # Create output directory
            raw_dir = Path(os.getenv("RAW_DIR", "data/raw"))
            swimmers_dir = raw_dir / "swimmers"
            swimmers_dir.mkdir(parents=True, exist_ok=True)

            # Save to CSV
            filename = swimmers_dir / f"{safe_name}-{self.person_key}.csv"
            df.to_csv(filename, index=False)

            console.print(f"[green]✓ Downloaded {len(df)} swims[/green]")
            console.print(f"  Swimmer: {swimmer_name}")
            console.print(f"  Saved to: {filename}\n")

        except Exception as e:
            console.print(f"[red]✗ Error downloading data: {e}[/red]\n")
            raise

    def _sanitize_filename(self, name: str) -> str:
        """Convert name to safe filename format."""
        safe_name = name.lower().replace(" ", "-")
        safe_name = "".join(c for c in safe_name if c.isalnum() or c == "-")
        return safe_name
