"""Import swimmers command - Download data for multiple swimmers."""

import os
import time
from datetime import datetime
from pathlib import Path

import pandas as pd
from rich.console import Console
from rich.panel import Panel
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

    def __init__(self, cwd: Path, csv_file: str | None, dry_run: bool, force: bool = False):
        self.cwd = cwd
        self.csv_file = csv_file
        self.dry_run = dry_run
        self.force = force
        self.api = USASwimmingAPI()

    def run(self) -> None:
        """Execute the import swimmers command."""
        # Default to roster.csv if no file specified
        if not self.csv_file:
            default_file = self.cwd / "data" / "lookups" / "roster.csv"
            if default_file.exists():
                self.csv_file = str(default_file)
                console.print(f"[dim]Using default roster: {self.csv_file}[/dim]\n")
            else:
                console.print("[yellow]⚠️  No roster file found[/yellow]")
                console.print("Please run: [cyan]swim-data-tool roster[/cyan] first\n")
                console.print("Or specify a CSV file with: [cyan]swim-data-tool import swimmers --file=FILE[/cyan]")
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
        
        # Create gender map if Gender column exists in roster
        gender_map = {}
        if "Gender" in swimmers_df.columns:
            for _, row in swimmers_df.iterrows():
                if row["PersonKey"] != 0 and row.get("Gender"):
                    gender_map[int(row["PersonKey"])] = row["Gender"]
        
        # Filter out relay entries (PersonKey=0) and only-relay swimmers
        # TODO: Future enhancement - recognize individuals in relay results
        #       When generating team records, top 10 lists, or annual analysis,
        #       we should parse relay names to credit individual swimmers.
        #       This will require name matching against known swimmers.
        total_entries = len(swimmers_df)
        swimmers_df = swimmers_df[swimmers_df["PersonKey"] != 0].copy()
        relay_entries = total_entries - len(swimmers_df)

        # Get configuration
        start_year = int(os.getenv("START_YEAR", "1998"))
        end_year = int(os.getenv("END_YEAR", str(datetime.now().year)))
        raw_dir = Path(os.getenv("RAW_DIR", "data/raw"))
        swimmers_dir = raw_dir / "swimmers"

        console.print("\n[bold cyan]Import Swimmers[/bold cyan]\n")
        console.print(f"  CSV File: {self.csv_file}")
        console.print(f"  Total entries in roster: {total_entries}")
        console.print(f"  Individual swimmers: {len(swimmers_df)}")
        if relay_entries > 0:
            console.print(f"  Relay-only entries: {relay_entries} (skipped)")
        console.print(f"  Years: {start_year}-{end_year}")
        console.print(f"  Output: {swimmers_dir}\n")

        # Check existing files (unless force mode)
        if self.force:
            existing = set()
            console.print("  [yellow]Force mode: Will re-download all swimmers[/yellow]\n")
        else:
            existing = self._get_existing_swimmer_files(swimmers_dir)

        # Determine what to download
        to_download = []
        for _, row in swimmers_df.iterrows():
            person_key = int(row["PersonKey"])
            if person_key not in existing:
                to_download.append((person_key, row["FullName"]))

        # Calculate breakdown
        already_cached = len(existing)
        will_download = len(to_download)
        already_attempted = len(swimmers_df) - already_cached - will_download
        
        console.print(f"  Already cached: {already_cached} swimmers (have data files)")
        console.print(f"  Will attempt: {will_download} swimmers (not yet tried)")
        if already_attempted > 0:
            console.print(f"  Previously attempted: {already_attempted} swimmers (had no data)")
        console.print()

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
        timeouts = 0
        
        # Rate monitoring
        recent_times = []
        max_recent = 10  # Track last 10 downloads
        timeout_threshold = 30  # seconds per swimmer

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

                start_time = time.time()
                try:
                    df = self.api.download_swimmer_career(
                        person_key=person_key,
                        start_year=start_year,
                        end_year=end_year,
                    )
                    
                    elapsed = time.time() - start_time
                    
                    # Check if this swimmer took too long
                    if elapsed > timeout_threshold:
                        console.print(f"\n[yellow]⚠️  {name} took {elapsed:.1f}s (slow swimmer, might have huge career)[/yellow]")
                        timeouts += 1

                    # Track recent download times
                    recent_times.append(elapsed)
                    if len(recent_times) > max_recent:
                        recent_times.pop(0)
                    
                    # Calculate and show average rate
                    if len(recent_times) >= 3:
                        avg_time = sum(recent_times) / len(recent_times)
                        progress.update(task, description=f"[cyan]Downloading: {name[:30]} (avg: {avg_time:.1f}s/swimmer)")

                    if not df.empty:
                        # Add Gender column if we have gender data
                        if gender_map and person_key in gender_map:
                            df["Gender"] = gender_map[person_key]
                        
                        safe_name = self._sanitize_filename(name)
                        filename = swimmers_dir / f"{safe_name}-{person_key}.csv"
                        df.to_csv(filename, index=False)
                        downloaded += 1
                    else:
                        empty += 1

                    # Small delay to be respectful to API
                    time.sleep(0.1)

                except KeyboardInterrupt:
                    console.print("\n[yellow]⚠️  Download interrupted by user[/yellow]")
                    raise
                except Exception as e:
                    console.print(f"\n[red]✗ Error downloading {name}: {e}[/red]")
                    errors += 1

                progress.advance(task)

        # Summary
        console.print("\n[bold green]✓ Import Complete![/bold green]\n")
        console.print(f"  Downloaded: {downloaded} swimmers")
        console.print(f"  No data: {empty} swimmers")
        if errors > 0:
            console.print(f"  Errors: {errors} swimmers")
        if timeouts > 0:
            console.print(f"  Slow swimmers (>{timeout_threshold}s): {timeouts}")
        console.print(f"  Total cached: {len(existing) + downloaded} swimmers")
        
        # Show average rate if we have data
        if recent_times:
            avg_time = sum(recent_times) / len(recent_times)
            console.print(f"  Average rate: {avg_time:.1f}s per swimmer")
        
        # Show next steps
        next_steps = """1. Classify unattached swims:
   [cyan]swim-data-tool classify unattached[/cyan]

2. Generate team records:
   [cyan]swim-data-tool generate records[/cyan]
   
   Or generate specific course:
   [cyan]swim-data-tool generate records --course=scy[/cyan]

3. Check your records:
   [cyan]cat data/records/scy/records.md[/cyan]"""
        
        console.print()
        console.print(Panel(
            next_steps,
            title="Next Steps",
            border_style="green",
            expand=False
        ))

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

