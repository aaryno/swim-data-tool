"""Import swimmers command - Download data for multiple swimmers."""

import os
import time
from datetime import datetime
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
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

from swim_data_tool.sources.factory import get_source

console = Console()


class ImportSwimmersCommand:
    """Import career data for multiple swimmers from any data source."""

    def __init__(self, cwd: Path, csv_file: str | None, dry_run: bool, force: bool = False, source: str | None = None):
        self.cwd = cwd
        self.csv_file = csv_file
        self.dry_run = dry_run
        self.force = force
        self.source_name = source

    def run(self) -> None:
        """Execute the import swimmers command."""
        # Load .env
        env_file = self.cwd / ".env"
        if env_file.exists():
            load_dotenv(env_file)
        
        # Get data source
        try:
            source = get_source(self.source_name)
        except ValueError as e:
            console.print(f"[red]Error: {e}[/red]")
            return

        console.print(f"\n[bold cyan]🏊 Import Swimmers[/bold cyan]")
        console.print(f"[dim]Data source: {source.source_name}[/dim]\n")
        
        # Auto-detect roster file if not specified
        if not self.csv_file:
            source_suffix = source.source_name.lower().replace(" ", "-")
            default_files = [
                self.cwd / "data" / "lookups" / f"roster-{source_suffix}.csv",
                self.cwd / "data" / "lookups" / "roster.csv",
            ]
            
            for default_file in default_files:
                if default_file.exists():
                    self.csv_file = str(default_file)
                    console.print(f"[dim]Using roster: {self.csv_file}[/dim]\n")
                    break
            
            if not self.csv_file:
                console.print("[yellow]⚠️  No roster file found[/yellow]")
                console.print(f"Please run: [cyan]swim-data-tool roster --source={source.source_name.lower().replace(' ', '_')}[/cyan] first\n")
                console.print("Or specify a CSV file with: [cyan]swim-data-tool import swimmers --file=FILE[/cyan]")
                return

        # Load swimmer list
        try:
            swimmers_df = pd.read_csv(self.csv_file)
        except Exception as e:
            console.print(f"[red]✗ Error reading CSV file: {e}[/red]\n")
            return

        # Get swimmer ID field from source
        id_field = source.swimmer_id_field
        
        # Validate CSV has ID field
        if id_field not in swimmers_df.columns:
            console.print(f"[red]✗ CSV file must have '{id_field}' column for {source.source_name}[/red]\n")
            console.print(f"[dim]Available columns: {', '.join(swimmers_df.columns)}[/dim]")
            return

        # Get name field (handle different column names)
        name_field = None
        for possible_name in ["swimmer_name", "FullName", "Name"]:
            if possible_name in swimmers_df.columns:
                name_field = possible_name
                break
        
        if not name_field:
            console.print("[yellow]⚠️  No name column found (will use ID)[/yellow]\n")
            swimmers_df["swimmer_name"] = swimmers_df[id_field].astype(str)
            name_field = "swimmer_name"
        
        # Create gender map if gender column exists
        gender_map = {}
        gender_col = "gender" if "gender" in swimmers_df.columns else "Gender" if "Gender" in swimmers_df.columns else None
        if gender_col:
            for _, row in swimmers_df.iterrows():
                swimmer_id = str(row[id_field])
                if row.get(gender_col):
                    gender_map[swimmer_id] = row[gender_col]
        
        # Filter out relay entries (PersonKey=0 for USA Swimming)
        total_entries = len(swimmers_df)
        if id_field == "PersonKey":
            swimmers_df = swimmers_df[swimmers_df["PersonKey"] != 0].copy()
        relay_entries = total_entries - len(swimmers_df)

        # Get configuration
        raw_dir = Path(os.getenv("RAW_DIR", "data/raw"))
        swimmers_dir = raw_dir / "swimmers"
        
        # Year range only needed for USA Swimming
        if source.source_name == "USA Swimming":
            start_year_str = os.getenv("START_YEAR", "1998")
            end_year_str = os.getenv("END_YEAR", str(datetime.now().year))
            start_year = int(start_year_str) if start_year_str else 1998
            end_year = int(end_year_str) if end_year_str else datetime.now().year
        else:
            start_year = None
            end_year = None

        console.print(f"  CSV File: {self.csv_file}")
        console.print(f"  Total entries in roster: {total_entries}")
        console.print(f"  Individual swimmers: {len(swimmers_df)}")
        if relay_entries > 0:
            console.print(f"  Relay-only entries: {relay_entries} (skipped)")
        if source.source_name == "USA Swimming":
            console.print(f"  Years: {start_year}-{end_year}")
        console.print(f"  Output: {swimmers_dir}\n")

        # Check existing files (unless force mode)
        if self.force:
            existing = set()
            console.print("  [yellow]Force mode: Will re-download all swimmers[/yellow]\n")
        else:
            existing = self._get_existing_swimmer_files(swimmers_dir, id_field)

        # Determine what to download
        to_download = []
        for _, row in swimmers_df.iterrows():
            swimmer_id = str(row[id_field])
            swimmer_name = row[name_field]
            
            if swimmer_id not in existing:
                # For MaxPreps, we need the full athlete URL
                if source.source_name == "MaxPreps" and "athlete_url" in row:
                    to_download.append((row["athlete_url"], swimmer_name, swimmer_id))
                else:
                    to_download.append((swimmer_id, swimmer_name, swimmer_id))

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
            for i, (url_or_id, name, swimmer_id) in enumerate(to_download[:20], 1):
                console.print(f"  {i}. {name} (ID: {swimmer_id})")
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

            for url_or_id, name, swimmer_id in to_download:
                progress.update(task, description=f"[cyan]Fetching: {name[:30]}")

                start_time = time.time()
                try:
                    df = source.get_swimmer_history(
                        swimmer_id=url_or_id,
                        start_year=start_year,
                        end_year=end_year,
                    )
                    
                    elapsed = time.time() - start_time
                    
                    # Check if this swimmer took too long
                    if elapsed > timeout_threshold:
                        console.print(f"\n[yellow]⚠️  {name} took {elapsed:.1f}s[/yellow]")
                        timeouts += 1

                    # Track recent download times
                    recent_times.append(elapsed)
                    if len(recent_times) > max_recent:
                        recent_times.pop(0)
                    
                    # Calculate and show average rate
                    if len(recent_times) >= 3:
                        avg_time = sum(recent_times) / len(recent_times)
                        progress.update(task, description=f"[cyan]Fetching: {name[:30]} (avg: {avg_time:.1f}s/swimmer)")

                    if not df.empty:
                        # Add Gender column if we have gender data and it's not already there
                        if gender_map and swimmer_id in gender_map:
                            if "gender" not in df.columns and "Gender" not in df.columns:
                                df["Gender"] = gender_map[swimmer_id]
                        
                        safe_name = self._sanitize_filename(name)
                        filename = swimmers_dir / f"{safe_name}-{swimmer_id}.csv"
                        df.to_csv(filename, index=False)
                        downloaded += 1
                    else:
                        empty += 1

                    # Small delay to be respectful
                    time.sleep(0.5 if source.source_name == "MaxPreps" else 0.1)

                except KeyboardInterrupt:
                    console.print("\n[yellow]⚠️  Interrupted by user[/yellow]")
                    raise
                except Exception as e:
                    console.print(f"\n[red]✗ Error fetching {name}: {e}[/red]")
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

    def _get_existing_swimmer_files(self, swimmers_dir: Path, id_field: str) -> set[str]:
        """Get set of swimmer IDs that already have cached files.
        
        Args:
            swimmers_dir: Directory containing swimmer CSV files
            id_field: Name of ID field (PersonKey, careerid, etc.)
        
        Returns:
            Set of swimmer IDs (as strings) that have cached files
        """
        if not swimmers_dir.exists():
            return set()

        existing_ids = set()
        for csv_file in swimmers_dir.glob("*.csv"):
            # Extract ID from filename (last part before .csv)
            filename = csv_file.stem
            parts = filename.split("-")
            if parts:
                swimmer_id = parts[-1]
                existing_ids.add(swimmer_id)

        return existing_ids

    def _sanitize_filename(self, name: str) -> str:
        """Convert name to safe filename format."""
        safe_name = name.lower().replace(" ", "-")
        safe_name = "".join(c for c in safe_name if c.isalnum() or c == "-")
        return safe_name

