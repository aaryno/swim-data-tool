"""Classify command - Classify unattached swims with user decisions."""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)

console = Console()

# USA Swimming transfer rule effective date
TRANSFER_RULE_CHANGE_DATE = datetime(2023, 1, 1)
POST_2023_TRANSFER_DAYS = 60
PRE_2023_TRANSFER_DAYS = 120


class ClassifyUnattachedCommand:
    """Classify unattached swims with user-defined rules for record eligibility."""

    def __init__(self, cwd: Path, decisions: dict[str, str | None] | None = None):
        self.cwd = cwd
        self.raw_dir = Path(os.getenv("RAW_DIR", "data/raw"))
        self.processed_dir = Path(os.getenv("PROCESSED_DIR", "data/processed"))
        self.team_names = self._get_team_names()
        self.cli_decisions = decisions or {}
        self.config_file = cwd / ".swim-data-tool-classify-config.json"

    def run(self) -> None:
        """Execute the classify unattached command."""
        console.print("\n[bold cyan]🏊 Swim Data Tool - Classify Unattached Swims[/bold cyan]\n")

        # Setup directories
        swimmers_dir = self.raw_dir / "swimmers"
        classified_dir = self.processed_dir / "classified"
        official_dir = classified_dir / "official"
        excluded_dir = classified_dir / "excluded"
        progress_log = classified_dir / "classification_progress.json"

        official_dir.mkdir(parents=True, exist_ok=True)
        excluded_dir.mkdir(parents=True, exist_ok=True)

        # Get all swimmer files
        swimmer_files = sorted(swimmers_dir.glob("*.csv"))

        if not swimmer_files:
            console.print("[yellow]⚠️  No swimmer CSV files found[/yellow]\n")
            return

        # First pass: analyze all swims to show statistics
        console.print("[dim]Analyzing swims...[/dim]\n")
        stats = self._analyze_swims(swimmer_files)

        # Display statistics
        console.print(f"Found [cyan]{stats['total_swims']:,}[/cyan] total swims across [cyan]{len(swimmer_files)}[/cyan] swimmers")
        console.print(f"  • [green]{stats['club_affiliated']:,}[/green] club-affiliated swims ({stats['club_affiliated']/stats['total_swims']*100:.1f}%)")
        console.print(f"  • [yellow]{stats['unattached']:,}[/yellow] unattached swims ({stats['unattached']/stats['total_swims']*100:.1f}%)\n")

        console.print("[bold]Unattached swim breakdown:[/bold]")
        console.print(f"  • [cyan]{stats['high_school']}[/cyan] high school swims")
        console.print(f"  • [cyan]{stats['probationary']}[/cyan] probationary swims (60-day: {stats['probationary_60']}, 120-day: {stats['probationary_120']})")
        console.print(f"  • [cyan]{stats['college']}[/cyan] college swims")
        console.print(f"  • [cyan]{stats['misc_unattached']}[/cyan] misc unattached swims\n")

        # Load or get classification decisions
        decisions = self._get_decisions(stats)

        # Save decisions
        self._save_config(decisions)
        console.print("[green]✓[/green] Decisions saved to [cyan].swim-data-tool-classify-config.json[/cyan]\n")

        # Load progress
        progress = self._load_progress(progress_log)

        already_processed = len(progress["processed_swimmers"])
        to_process = len(swimmer_files)

        console.print(f"[dim]Processing classifications...[/dim]\n")

        # Process swimmers with progress bar
        processed_count = 0
        total_stats = {
            "official": 0,
            "excluded": 0,
            "by_category": {
                "official": 0,
                "high_school": 0,
                "probationary": 0,
                "college": 0,
                "misc_unattached": 0,
            }
        }

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            MofNCompleteColumn(),
            TimeElapsedColumn(),
            console=console,
        ) as progress_bar:
            task = progress_bar.add_task(
                "[cyan]Processing classifications...", total=to_process
            )

            for csv_file in swimmer_files:
                swimmer_name = csv_file.stem
                progress_bar.update(
                    task, description=f"[cyan]Classifying: {swimmer_name[:40]}"
                )

                # Classify this swimmer
                result = self._classify_swimmer(csv_file, decisions)

                # Save official swims
                if not result["official"].empty:
                    output_file = official_dir / csv_file.name
                    result["official"].to_csv(output_file, index=False)
                    total_stats["official"] += len(result["official"])

                # Save excluded swims
                if not result["excluded"].empty:
                    output_file = excluded_dir / csv_file.name
                    result["excluded"].to_csv(output_file, index=False)
                    total_stats["excluded"] += len(result["excluded"])

                # Update category stats
                for cat, count in result["stats"].items():
                    total_stats["by_category"][cat] += count

                # Record progress
                progress["processed_swimmers"][swimmer_name] = {
                    "status": "completed",
                    "official_count": len(result["official"]),
                    "excluded_count": len(result["excluded"]),
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
        console.print(f"  Total swims processed: {total_stats['official'] + total_stats['excluded']:,}")
        console.print(f"  [green]Official team swims: {total_stats['official']:,}[/green] ({total_stats['official']/(total_stats['official']+total_stats['excluded'])*100:.1f}%)")
        console.print(f"  [yellow]Excluded swims: {total_stats['excluded']:,}[/yellow] ({total_stats['excluded']/(total_stats['official']+total_stats['excluded'])*100:.1f}%)\n")

        console.print("[bold]Breakdown by decision:[/bold]")
        console.print(f"  • Club-affiliated: {total_stats['by_category']['official']:,}")
        console.print(f"  • High school: {total_stats['by_category']['high_school']:,} ({decisions['high_school']}d)")
        console.print(f"  • Probationary: {total_stats['by_category']['probationary']:,} ({decisions['probationary']}d)")
        console.print(f"  • College: {total_stats['by_category']['college']:,} ({decisions['college']}d)")
        console.print(f"  • Misc unattached: {total_stats['by_category']['misc_unattached']:,} ({decisions['misc_unattached']}d)\n")

        console.print(f"Output written to:")
        console.print(f"  • [green]{official_dir}/[/green]")
        console.print(f"  • [yellow]{excluded_dir}/[/yellow]")

        # Show next steps
        next_steps = """1. Generate team records (uses official swims only):
   [cyan]swim-data-tool generate records[/cyan]
   
   Or generate specific course:
   [cyan]swim-data-tool generate records --course=scy[/cyan]
   [cyan]swim-data-tool generate records --course=lcm[/cyan]

2. View your records:
   [cyan]cat data/records/scy/records.md[/cyan]
   
3. Check classification output:
   [cyan]ls -lh data/processed/classified/official/[/cyan]
   [cyan]ls -lh data/processed/classified/excluded/[/cyan]

4. To reclassify with different decisions:
   [cyan]swim-data-tool classify unattached --high-school=include --probationary=include[/cyan]"""

        console.print()
        console.print(Panel(
            next_steps,
            title="Next Steps",
            border_style="green",
            expand=False
        ))

    def _analyze_swims(self, swimmer_files: list[Path]) -> dict:
        """Analyze all swims to gather statistics."""
        stats = {
            "total_swims": 0,
            "club_affiliated": 0,
            "unattached": 0,
            "high_school": 0,
            "probationary": 0,
            "probationary_60": 0,
            "probationary_120": 0,
            "college": 0,
            "misc_unattached": 0,
        }

        for csv_file in swimmer_files:
            try:
                df = pd.read_csv(csv_file)
                if "Team" not in df.columns or len(df) == 0:
                    continue

                stats["total_swims"] += len(df)

                # Find first team swim to determine probationary period
                team_mask = df["Team"].apply(lambda x: self._is_team_swim(str(x)))
                team_indices = df[team_mask].index.tolist()
                first_team_idx = team_indices[0] if team_indices else None
                first_team_date = None

                if first_team_idx is not None and "SwimDate" in df.columns:
                    date_str = df.loc[first_team_idx, "SwimDate"]
                    try:
                        first_team_date = pd.to_datetime(date_str)
                    except:
                        pass

                # Classify each swim
                seen_other_club = False
                for idx, row in df.iterrows():
                    team = str(row["Team"]) if pd.notna(row["Team"]) else ""
                    is_team = self._is_team_swim(team)
                    is_unattached = self._is_unattached(team)

                    if is_team:
                        stats["club_affiliated"] += 1
                    elif is_unattached:
                        stats["unattached"] += 1

                        # Categorize unattached
                        if self._is_high_school(team):
                            stats["high_school"] += 1
                        elif first_team_idx is not None and idx < first_team_idx and first_team_date:
                            # Check if probationary
                            if seen_other_club:
                                swim_date = None
                                if "SwimDate" in row:
                                    try:
                                        swim_date = pd.to_datetime(row["SwimDate"])
                                    except:
                                        pass

                                if swim_date and self._is_probationary(swim_date, first_team_date):
                                    stats["probationary"] += 1
                                    # Determine which rule applies
                                    if swim_date >= TRANSFER_RULE_CHANGE_DATE:
                                        stats["probationary_60"] += 1
                                    else:
                                        stats["probationary_120"] += 1
                                else:
                                    stats["misc_unattached"] += 1
                            else:
                                stats["misc_unattached"] += 1
                        elif self._is_college_age(row):
                            stats["college"] += 1
                        else:
                            stats["misc_unattached"] += 1
                    elif not is_team and team.strip():
                        # Another club
                        stats["club_affiliated"] += 1
                        if first_team_idx is None or idx < first_team_idx:
                            seen_other_club = True

            except Exception:
                continue

        return stats

    def _get_decisions(self, stats: dict) -> dict[str, str]:
        """Get classification decisions from CLI, config file, or interactive prompts."""
        # Check if we have a saved config
        saved_config = self._load_config()

        decisions = {}

        # High school
        if self.cli_decisions.get("high_school"):
            decisions["high_school"] = self.cli_decisions["high_school"]
        elif saved_config.get("high_school"):
            decisions["high_school"] = saved_config["high_school"]
            console.print(f"[dim]Using saved decision for high school: {saved_config['high_school']}[/dim]")
        else:
            console.print("\n[bold]High School Swims[/bold]")
            console.print(f"Found {stats['high_school']} high school swims")
            console.print("[dim]Swimmer competed for high school team while being club member[/dim]")
            decisions["high_school"] = "include" if Confirm.ask(
                "Include high school swims in records?",
                default=False
            ) else "exclude"

        # Probationary
        if self.cli_decisions.get("probationary"):
            decisions["probationary"] = self.cli_decisions["probationary"]
        elif saved_config.get("probationary"):
            decisions["probationary"] = saved_config["probationary"]
            console.print(f"[dim]Using saved decision for probationary: {saved_config['probationary']}[/dim]")
        else:
            console.print("\n[bold]Probationary Swims[/bold]")
            console.print(f"Found {stats['probationary']} probationary swims")
            console.print(f"  • {stats['probationary_60']} swims under 60-day rule (post-2023)")
            console.print(f"  • {stats['probationary_120']} swims under 120-day rule (pre-2023)")
            console.print("[dim]Unattached swims within transfer period before joining club[/dim]")
            decisions["probationary"] = "include" if Confirm.ask(
                "Include probationary swims in records?",
                default=True
            ) else "exclude"

        # College
        if self.cli_decisions.get("college"):
            decisions["college"] = self.cli_decisions["college"]
        elif saved_config.get("college"):
            decisions["college"] = saved_config["college"]
            console.print(f"[dim]Using saved decision for college: {saved_config['college']}[/dim]")
        else:
            console.print("\n[bold]College Swims[/bold]")
            console.print(f"Found {stats['college']} college swims")
            console.print("[dim]Unattached swims during college years (ages 18-22)[/dim]")
            decisions["college"] = "include" if Confirm.ask(
                "Include unattached college swims in records?",
                default=False
            ) else "exclude"

        # Misc unattached
        if self.cli_decisions.get("misc_unattached"):
            decisions["misc_unattached"] = self.cli_decisions["misc_unattached"]
        elif saved_config.get("misc_unattached"):
            decisions["misc_unattached"] = saved_config["misc_unattached"]
            console.print(f"[dim]Using saved decision for misc unattached: {saved_config['misc_unattached']}[/dim]")
        else:
            console.print("\n[bold]Misc Unattached Swims[/bold]")
            console.print(f"Found {stats['misc_unattached']} misc unattached swims")
            console.print("[dim]Other unattached swims (time trials, pre-club, etc.)[/dim]")
            decisions["misc_unattached"] = "include" if Confirm.ask(
                "Include misc unattached swims in records?",
                default=False
            ) else "exclude"

        return decisions

    def _classify_swimmer(self, csv_file: Path, decisions: dict[str, str]) -> dict:
        """Classify all swims for a single swimmer with metadata."""
        try:
            df = pd.read_csv(csv_file)
        except Exception:
            return {
                "official": pd.DataFrame(),
                "excluded": pd.DataFrame(),
                "stats": {
                    "official": 0,
                    "high_school": 0,
                    "probationary": 0,
                    "college": 0,
                    "misc_unattached": 0,
                }
            }

        if "Team" not in df.columns or len(df) == 0:
            return {
                "official": pd.DataFrame(),
                "excluded": pd.DataFrame(),
                "stats": {
                    "official": 0,
                    "high_school": 0,
                    "probationary": 0,
                    "college": 0,
                    "misc_unattached": 0,
                }
            }

        # Add classification columns
        df["classification_category"] = ""
        df["classification_decision"] = ""
        df["classification_rationale"] = ""
        df["transfer_rule_days"] = pd.NA

        # Find first team swim
        team_mask = df["Team"].apply(lambda x: self._is_team_swim(str(x)))
        team_indices = df[team_mask].index.tolist()
        first_team_idx = team_indices[0] if team_indices else None
        first_team_date = None

        if first_team_idx is not None and "SwimDate" in df.columns:
            date_str = df.loc[first_team_idx, "SwimDate"]
            try:
                first_team_date = pd.to_datetime(date_str)
            except:
                pass

        # Classify each swim
        seen_other_club = False
        stats = {
            "official": 0,
            "high_school": 0,
            "probationary": 0,
            "college": 0,
            "misc_unattached": 0,
        }

        for idx in df.index:
            team = str(df.loc[idx, "Team"]) if pd.notna(df.loc[idx, "Team"]) else ""
            is_team = self._is_team_swim(team)
            is_unattached = self._is_unattached(team)

            if is_team:
                # Official club swim
                df.loc[idx, "classification_category"] = "Official"
                df.loc[idx, "classification_decision"] = "include"
                df.loc[idx, "classification_rationale"] = "Club-affiliated swim"
                stats["official"] += 1

            elif is_unattached:
                # Categorize and apply decisions
                if self._is_high_school(team):
                    df.loc[idx, "classification_category"] = "HighSchool"
                    df.loc[idx, "classification_decision"] = decisions["high_school"]
                    df.loc[idx, "classification_rationale"] = "High school team swim"
                    stats["high_school"] += 1

                elif first_team_idx is not None and idx < first_team_idx and first_team_date and seen_other_club:
                    # Check if probationary
                    swim_date = None
                    if "SwimDate" in df.columns:
                        try:
                            swim_date = pd.to_datetime(df.loc[idx, "SwimDate"])
                        except:
                            pass

                    if swim_date and self._is_probationary(swim_date, first_team_date):
                        df.loc[idx, "classification_category"] = "Probationary"
                        df.loc[idx, "classification_decision"] = decisions["probationary"]
                        
                        # Determine transfer rule
                        if swim_date >= TRANSFER_RULE_CHANGE_DATE:
                            df.loc[idx, "transfer_rule_days"] = POST_2023_TRANSFER_DAYS
                            df.loc[idx, "classification_rationale"] = "Probationary swim (60-day rule)"
                        else:
                            df.loc[idx, "transfer_rule_days"] = PRE_2023_TRANSFER_DAYS
                            df.loc[idx, "classification_rationale"] = "Probationary swim (120-day rule)"
                        
                        stats["probationary"] += 1
                    else:
                        df.loc[idx, "classification_category"] = "MiscUnattached"
                        df.loc[idx, "classification_decision"] = decisions["misc_unattached"]
                        df.loc[idx, "classification_rationale"] = "Misc unattached (outside transfer window)"
                        stats["misc_unattached"] += 1

                elif self._is_college_age(df.loc[idx]):
                    df.loc[idx, "classification_category"] = "College"
                    df.loc[idx, "classification_decision"] = decisions["college"]
                    df.loc[idx, "classification_rationale"] = "Unattached during college years"
                    stats["college"] += 1

                else:
                    df.loc[idx, "classification_category"] = "MiscUnattached"
                    df.loc[idx, "classification_decision"] = decisions["misc_unattached"]
                    df.loc[idx, "classification_rationale"] = "Misc unattached swim"
                    stats["misc_unattached"] += 1

            else:
                # Other club swim
                if team.strip():
                    df.loc[idx, "classification_category"] = "OtherClub"
                    df.loc[idx, "classification_decision"] = "exclude"
                    df.loc[idx, "classification_rationale"] = "Swam for different club"
                    
                    # Track if we've seen another club before team join
                    if first_team_idx is None or idx < first_team_idx:
                        seen_other_club = True
                else:
                    df.loc[idx, "classification_category"] = "Unknown"
                    df.loc[idx, "classification_decision"] = "exclude"
                    df.loc[idx, "classification_rationale"] = "No team information"

        # Split into official and excluded
        official_df = df[df["classification_decision"] == "include"].copy()
        excluded_df = df[df["classification_decision"] == "exclude"].copy()

        return {
            "official": official_df,
            "excluded": excluded_df,
            "stats": stats,
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

    def _is_high_school(self, team: str) -> bool:
        """Check if a swim is for a high school team."""
        team_lower = team.lower()
        return any(keyword in team_lower for keyword in ["high school", "hs-", " hs "])

    def _is_college_age(self, row: pd.Series) -> bool:
        """Check if swimmer was college age (18-22) during swim."""
        if "Age" in row:
            try:
                age = int(row["Age"])
                return 18 <= age <= 22
            except:
                pass
        return False

    def _is_probationary(self, swim_date: datetime, first_team_date: datetime) -> bool:
        """Check if swim falls within probationary transfer period."""
        # Determine which rule applies based on swim date
        if swim_date >= TRANSFER_RULE_CHANGE_DATE:
            transfer_days = POST_2023_TRANSFER_DAYS
        else:
            transfer_days = PRE_2023_TRANSFER_DAYS

        # Check if swim is within transfer window before first team swim
        window_start = first_team_date - timedelta(days=transfer_days)
        return window_start <= swim_date < first_team_date

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

    def _load_config(self) -> dict:
        """Load classification config from file."""
        if self.config_file.exists():
            try:
                with open(self.config_file) as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def _save_config(self, decisions: dict[str, str]) -> None:
        """Save classification decisions to config file."""
        config = {
            "high_school": decisions["high_school"],
            "probationary": decisions["probationary"],
            "college": decisions["college"],
            "misc_unattached": decisions["misc_unattached"],
            "classified_date": datetime.now().isoformat(),
            "swim_data_tool_version": os.getenv("SWIM_DATA_TOOL_VERSION", "0.4.5"),
        }
        with open(self.config_file, "w") as f:
            json.dump(config, f, indent=2)

    def _load_progress(self, progress_log: Path) -> dict:
        """Load progress from JSON log."""
        if progress_log.exists():
            with open(progress_log) as f:
                return json.load(f)
        return {
            "processed_swimmers": {},
            "last_run": None,
        }

    def _save_progress(self, progress: dict, progress_log: Path) -> None:
        """Save progress to JSON log."""
        progress["last_run"] = datetime.now().isoformat()
        with open(progress_log, "w") as f:
            json.dump(progress, f, indent=2)