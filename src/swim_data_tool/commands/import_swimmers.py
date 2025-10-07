"""Import swimmers command - Download data for multiple swimmers."""

import os
import time
from datetime import datetime
from pathlib import Path

import pandas as pd
from rich.console import Console
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)

from swim_data_tool.api import USASwimmingAPI

console = Console()


class ImportSwimmersCommand:
    """Import career data for multiple swimmers from a CSV file."""

    def __init__(self, cwd: Path, csv_file: str | None, dry_run: bool):
        self.cwd = cwd
        self.csv_file = csv_file
        self.dry_run = dry_run
        self.api = USASwimmingAPI()

    def run(self) -> None:
        """Execute the import swimmers command."""
        if not self.csv_file:
            console.print("[yellow]⚠️  No CSV file specified[/yellow]")
            console.print("Usage: swim-data-tool import swimmers --file=swimmers.csv\n")
            console.print("CSV file should have columns: PersonKey, FullName")
            return

        # Load swimmer list
        try:
            swimmers_df = pd.read_csv(self.csv_file)
        except Exception as e:
            console.print(f"[red]✗ Error reading CSV file: {e}[/red]\n")
            return

        # Validate CSV format
        if "PersonKey" not in swimmers_df.columns:
            console.print(
                "[red]✗ CSV file must have 'PersonKey' column[/red]\n"
            )
            return

        if "FullName" not in swimmers_df.columns:
            console.print(
                "[yellow]⚠️  CSV file missing 'FullName' column (will use PersonKey)[/yellow]\n"
            )
            swimmers_df["FullName"] = swimmers_df["PersonKey"].astype(str)

        # Get configuration
        start_year = int(os.getenv("START_YEAR", "1998"))
        end_year = int(os.getenv("END_YEAR", str(datetime.now().year)))
        raw_dir = Path(os.getenv("RAW_DIR", "data/raw"))
        swimmers_dir = raw_dir / "swimmers"

        console.print("\n[bold cyan]Import Swimmers[/bold cyan]\n")
        console.print(f"  CSV File: {self.csv_file}")
        console.print(f"  Swimmers: {len(swimmers_df)}")
        console.print(f"  Years: {start_year}-{end_year}")
        console.print(f"  Output: {swimmers_dir}\n")

        # Check existing files
        existing = self._get_existing_swimmer_files(swimmers_dir)
        console.print(f"  Existing cached: {len(existing)} swimmers")

        # Determine what to download
        to_download = []
        for _, row in swimmers_df.iterrows():
            person_key = int(row["PersonKey"])
            if person_key not in existing:
                to_download.append((person_key, row["FullName"]))

        console.print(f"  Need to download: {len(to_download)} swimmers")
        console.print(f"  Skipping: {len(existing)} swimmers\n")

        if not to_download:
            console.print("[green]✓ All swimmers already cached![/green]\n")
            return

        # Dry run mode
        if self.dry_run:
            console.print("[yellow]DRY RUN MODE - showing first 20 swimmers:[/yellow]\n")
            for i, (pk, name) in enumerate(to_download[:20], 1):
                console.print(f"  {i}. {name} (PersonKey: {pk})")
            if len(to_download) > 20:
                console.print(f"  ... and {len(to_download) - 20} more")
            console.print("\n💡 Remove --dry-run to actually download\n")
            return

        # Create output directory
        swimmers_dir.mkdir(parents=True, exist_ok=True)

        # Download with progress bar
        downloaded = 0
        errors = 0
        empty = 0

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            MofNCompleteColumn(),
            TimeElapsedColumn(),
            console=console,
        ) as progress:
            task = progress.add_task(
                "[cyan]Downloading swimmers...", total=len(to_download)
            )

            for person_key, name in to_download:
                progress.update(task, description=f"[cyan]Downloading: {name[:30]}")

                try:
                    df = self.api.download_swimmer_career(
                        person_key=person_key,
                        start_year=start_year,
                        end_year=end_year,
                    )

                    if not df.empty:
                        safe_name = self._sanitize_filename(name)
                        filename = swimmers_dir / f"{safe_name}-{person_key}.csv"
                        df.to_csv(filename, index=False)
                        downloaded += 1
                    else:
                        empty += 1

                    # Small delay to be respectful to API
                    time.sleep(0.1)

                except Exception as e:
                    console.print(f"\n[red]✗ Error downloading {name}: {e}[/red]")
                    errors += 1

                progress.advance(task)

        # Summary
        console.print("\n[bold green]Import Complete![/bold green]\n")
        console.print(f"  ✓ Downloaded: {downloaded} swimmers")
        console.print(f"  ⚠️  No data: {empty} swimmers")
        console.print(f"  ✗ Errors: {errors} swimmers")
        console.print(f"  📁 Total cached: {len(existing) + downloaded} swimmers\n")

    def _get_existing_swimmer_files(self, swimmers_dir: Path) -> set[int]:
        """Get set of PersonKeys that already have cached files."""
        if not swimmers_dir.exists():
            return set()

        existing_person_keys = set()
        for csv_file in swimmers_dir.glob("*.csv"):
            # Extract PersonKey from filename (last part before .csv)
            filename = csv_file.stem
            parts = filename.split("-")
            if parts:
                try:
                    person_key = int(parts[-1])
                    existing_person_keys.add(person_key)
                except ValueError:
                    continue

        return existing_person_keys

    def _sanitize_filename(self, name: str) -> str:
        """Convert name to safe filename format."""
        safe_name = name.lower().replace(" ", "-")
        safe_name = "".join(c for c in safe_name if c.isalnum() or c == "-")
        return safe_name

