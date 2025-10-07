"""Classify command - Classify unattached swims."""

import json
import os
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

console = Console()


class ClassifyUnattachedCommand:
    """Classify unattached swims as probationary or team-unattached."""

    def __init__(self, cwd: Path):
        self.cwd = cwd
        self.raw_dir = Path(os.getenv("RAW_DIR", "data/raw"))
        self.processed_dir = Path(os.getenv("PROCESSED_DIR", "data/processed"))
        self.team_names = self._get_team_names()

    def run(self) -> None:
        """Execute the classify unattached command."""
        console.print("\n[bold cyan]Classify Unattached Swims[/bold cyan]\n")

        # Setup directories
        swimmers_dir = self.raw_dir / "swimmers"
        unattached_dir = self.processed_dir / "unattached"
        probationary_dir = unattached_dir / "probationary"
        team_unattached_dir = unattached_dir / f"{self._safe_team_name()}-unattached"
        progress_log = unattached_dir / "classification_progress.json"

        probationary_dir.mkdir(parents=True, exist_ok=True)
        team_unattached_dir.mkdir(parents=True, exist_ok=True)

        console.print(f"  Source: {swimmers_dir}")
        console.print(f"  Output: {unattached_dir}")
        console.print(f"  Team names: {', '.join(self.team_names)}\n")

        console.print("[dim]Classification Rules:[/dim]")
        console.print(
            "[dim]  • Probationary: Unattached BEFORE first team swim, AFTER another club[/dim]"
        )
        console.print(
            "[dim]  • Team-unattached: Unattached AFTER first team swim[/dim]\n"
        )

        # Load progress
        progress = self._load_progress(progress_log)
        if progress["last_run"]:
            console.print(f"[yellow]Resuming from: {progress['last_run']}[/yellow]")
            console.print(
                f"[yellow]Previously processed: {len(progress['processed_swimmers'])} swimmers[/yellow]\n"
            )

        # Get all swimmer files
        swimmer_files = sorted(swimmers_dir.glob("*.csv"))

        if not swimmer_files:
            console.print("[yellow]⚠️  No swimmer CSV files found[/yellow]\n")
            return

        already_processed = len(progress["processed_swimmers"])
        to_process = len(swimmer_files) - already_processed

        console.print(f"  Total swimmers: {len(swimmer_files)}")
        console.print(f"  Already processed: {already_processed}")
        console.print(f"  To process: {to_process}\n")

        if to_process == 0:
            console.print("[green]✓ All swimmers already classified![/green]\n")
            return

        # Process swimmers with progress bar
        processed_count = 0
        skipped_count = 0

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            MofNCompleteColumn(),
            TimeElapsedColumn(),
            console=console,
        ) as progress_bar:
            task = progress_bar.add_task(
                "[cyan]Classifying...", total=len(swimmer_files)
            )

            for csv_file in swimmer_files:
                swimmer_name = csv_file.stem
                progress_bar.update(
                    task, description=f"[cyan]Classifying: {swimmer_name[:30]}"
                )

                # Skip if already processed
                if swimmer_name in progress["processed_swimmers"]:
                    skipped_count += 1
                    progress_bar.advance(task)
                    continue

                # Classify this swimmer
                result = self._classify_swimmer(csv_file)

                # Save probationary swims
                if not result["probationary"].empty:
                    output_file = probationary_dir / csv_file.name
                    result["probationary"].to_csv(output_file, index=False)
                    progress["total_probationary"] += len(result["probationary"])

                # Save team-unattached swims
                if not result["team_unattached"].empty:
                    output_file = team_unattached_dir / csv_file.name
                    result["team_unattached"].to_csv(output_file, index=False)
                    progress["total_team_unattached"] += len(result["team_unattached"])

                # Record progress
                progress["processed_swimmers"][swimmer_name] = {
                    "status": "completed",
                    "probationary_count": len(result["probationary"]),
                    "team_unattached_count": len(result["team_unattached"]),
                    "first_team_date": result.get("first_team_date"),
                    "timestamp": datetime.now().isoformat(),
                }

                processed_count += 1

                # Save progress periodically
                if processed_count % 10 == 0:
                    self._save_progress(progress, progress_log)

                progress_bar.advance(task)

        # Final save
        self._save_progress(progress, progress_log)

        # Summary
        console.print("\n[bold green]✓ Classification Complete![/bold green]\n")
        console.print(f"  Processed this run: {processed_count}")
        console.print(f"  Skipped (already done): {skipped_count}")
        console.print(f"  Total swimmers: {len(progress['processed_swimmers'])}")
        console.print(f"  Probationary swims: {progress['total_probationary']}")
        console.print(f"  Team-unattached swims: {progress['total_team_unattached']}")
        
        # Show next steps
        next_steps = """1. Generate team records:
   [cyan]swim-data-tool generate records[/cyan]
   
   Or generate specific course:
   [cyan]swim-data-tool generate records --course=scy[/cyan]
   [cyan]swim-data-tool generate records --course=lcm[/cyan]

2. View your records:
   [cyan]cat data/records/scy/records.md[/cyan]
   
3. Check classification output:
   [cyan]ls -lh data/processed/unattached/[/cyan]"""
        
        console.print()
        console.print(Panel(
            next_steps,
            title="Next Steps",
            border_style="green"
        ))

    def _classify_swimmer(self, csv_file: Path) -> dict:
        """Classify unattached swims for a single swimmer.

        Classification logic:
        1. Find first team swim
        2. Before first team: Unattached after seeing another club = Probationary
        3. After first team: All unattached = Team-unattached
        """
        try:
            df = pd.read_csv(csv_file)
        except Exception:
            return {"probationary": pd.DataFrame(), "team_unattached": pd.DataFrame()}

        if "Team" not in df.columns or len(df) == 0:
            return {"probationary": pd.DataFrame(), "team_unattached": pd.DataFrame()}

        # Find first team swim
        team_mask = df["Team"].apply(lambda x: self._is_team_swim(str(x)))
        team_indices = df[team_mask].index.tolist()

        if len(team_indices) == 0:
            # No team swims - all unattached are non-team (ignore)
            return {"probationary": pd.DataFrame(), "team_unattached": pd.DataFrame()}

        first_team_idx = team_indices[0]

        # Classify unattached swims
        probationary_indices = []
        team_unattached_indices = []
        seen_other_club = False

        for idx, row in df.iterrows():
            team = str(row["Team"]) if pd.notna(row["Team"]) else ""
            is_unattached = self._is_unattached(team)
            is_team = self._is_team_swim(team)

            if idx < first_team_idx:
                # Pre-team phase
                if not is_unattached and not is_team and team.strip():
                    # Saw another club
                    seen_other_club = True
                elif is_unattached and seen_other_club:
                    # Unattached after another club, before team = PROBATIONARY
                    probationary_indices.append(idx)
            else:
                # Team-active phase
                if is_unattached:
                    # Unattached after team started = TEAM-UNATTACHED
                    team_unattached_indices.append(idx)

        probationary_df = (
            df.loc[probationary_indices].copy() if probationary_indices else pd.DataFrame()
        )
        team_unattached_df = (
            df.loc[team_unattached_indices].copy()
            if team_unattached_indices
            else pd.DataFrame()
        )

        return {
            "probationary": probationary_df,
            "team_unattached": team_unattached_df,
            "first_team_date": (
                df.loc[first_team_idx, "SwimDate"]
                if "SwimDate" in df.columns
                else None
            ),
        }

    def _is_team_swim(self, team: str) -> bool:
        """Check if a swim is for the configured team."""
        team_lower = team.lower()
        for team_name in self.team_names:
            if team_name.lower() in team_lower:
                return True
        return False

    def _is_unattached(self, team: str) -> bool:
        """Check if a swim is unattached."""
        return "unattached" in team.lower()

    def _get_team_names(self) -> list[str]:
        """Get team names from environment."""
        team_names_str = os.getenv("USA_SWIMMING_TEAM_NAMES", "")
        if team_names_str:
            names = [name.strip() for name in team_names_str.split(",")]
            return [name for name in names if name]

        # Fallback to team code
        team_code = os.getenv("USA_SWIMMING_TEAM_CODE", "")
        if team_code:
            return [team_code]

        return []

    def _safe_team_name(self) -> str:
        """Get safe team name for directory."""
        team_abbr = os.getenv("CLUB_ABBREVIATION", "team")
        return team_abbr.lower().replace(" ", "-")

    def _load_progress(self, progress_log: Path) -> dict:
        """Load progress from JSON log."""
        if progress_log.exists():
            with open(progress_log) as f:
                return json.load(f)
        return {
            "processed_swimmers": {},
            "last_run": None,
            "total_probationary": 0,
            "total_team_unattached": 0,
        }

    def _save_progress(self, progress: dict, progress_log: Path) -> None:
        """Save progress to JSON log."""
        progress["last_run"] = datetime.now().isoformat()
        with open(progress_log, "w") as f:
            json.dump(progress, f, indent=2)
