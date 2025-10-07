"""Publish records command."""

import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm

console = Console()


class PublishCommand:
    """Publish records to public GitHub repository."""

    def __init__(self, cwd: Path, dry_run: bool = False):
        """Initialize command.

        Args:
            cwd: Current working directory
            dry_run: If True, show what would be published without making changes
        """
        self.cwd = Path(cwd)
        self.dry_run = dry_run

        # Load config from .env
        self.team_name = os.getenv("CLUB_NAME", "Swim Team")
        self.public_repo_url = os.getenv("PUBLIC_REPO_URL", "")
        self.public_repo_local = os.getenv("PUBLIC_REPO_LOCAL", "")

        self.data_dir = self.cwd / "data"
        self.records_dir = self.data_dir / "records"

    def run(self) -> None:
        """Execute the command."""
        console.print("\n[bold cyan]📤 Publishing Records to GitHub[/bold cyan]\n")

        # Check configuration
        if not self.public_repo_url:
            console.print("[red]❌ PUBLIC_REPO_URL not configured in .env[/red]")
            console.print("[yellow]Add PUBLIC_REPO_URL to your .env file:[/yellow]")
            console.print("[dim]PUBLIC_REPO_URL=https://github.com/username/repo.git[/dim]")
            return

        if not self.public_repo_local:
            console.print("[red]❌ PUBLIC_REPO_LOCAL not configured in .env[/red]")
            console.print("[yellow]Add PUBLIC_REPO_LOCAL to your .env file:[/yellow]")
            console.print("[dim]PUBLIC_REPO_LOCAL=/tmp/my-team-records[/dim]")
            return

        # Check that records exist
        if not self.records_dir.exists():
            console.print("[red]❌ No records directory found.[/red]")
            console.print("[yellow]Run 'swim-data-tool generate records' first.[/yellow]")
            return

        # Check for git
        try:
            subprocess.run(
                ["git", "--version"],
                check=True,
                capture_output=True,
                text=True,
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            console.print("[red]❌ Git is not installed or not in PATH.[/red]")
            console.print("[yellow]Install git to use the publish command.[/yellow]")
            return

        console.print(f"[cyan]📍 Public repo:[/cyan] {self.public_repo_url}")
        console.print(f"[cyan]📂 Local path:[/cyan] {self.public_repo_local}\n")

        if self.dry_run:
            console.print("[yellow]🔍 DRY RUN MODE - No changes will be made[/yellow]\n")

        # Setup local repo
        local_repo = Path(self.public_repo_local)
        
        if not local_repo.exists():
            console.print("[cyan]📦 Cloning repository...[/cyan]")
            if not self.dry_run:
                try:
                    subprocess.run(
                        ["git", "clone", self.public_repo_url, str(local_repo)],
                        check=True,
                        capture_output=True,
                        text=True,
                    )
                    console.print("[green]✓[/green] Repository cloned\n")
                except subprocess.CalledProcessError as e:
                    console.print(f"[red]❌ Failed to clone repository:[/red]")
                    console.print(f"[dim]{e.stderr}[/dim]")
                    return
            else:
                console.print("[dim]Would clone repository[/dim]\n")
        else:
            console.print("[cyan]📥 Pulling latest changes...[/cyan]")
            if not self.dry_run:
                try:
                    subprocess.run(
                        ["git", "-C", str(local_repo), "pull"],
                        check=True,
                        capture_output=True,
                        text=True,
                    )
                    console.print("[green]✓[/green] Repository updated\n")
                except subprocess.CalledProcessError as e:
                    console.print(f"[yellow]⚠️  Failed to pull:[/yellow]")
                    console.print(f"[dim]{e.stderr}[/dim]")
                    console.print("[yellow]Continuing anyway...[/yellow]\n")
            else:
                console.print("[dim]Would pull latest changes[/dim]\n")

        # Copy records
        console.print("[cyan]📋 Copying records...[/cyan]")
        
        # Count files to copy
        files_to_copy = list(self.records_dir.rglob("*.md"))
        console.print(f"[cyan]Found {len(files_to_copy)} markdown files[/cyan]")
        
        if not self.dry_run:
            # Create records directory in public repo
            public_records_dir = local_repo / "records"
            public_records_dir.mkdir(exist_ok=True)
            
            # Copy all markdown files
            for src_file in files_to_copy:
                # Get relative path from records dir
                rel_path = src_file.relative_to(self.records_dir)
                dest_file = public_records_dir / rel_path
                
                # Create parent directories
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                
                # Copy file
                shutil.copy2(src_file, dest_file)
            
            console.print(f"[green]✓[/green] Copied {len(files_to_copy)} files\n")
        else:
            console.print("[dim]Would copy files to public repo[/dim]\n")
            for src_file in files_to_copy[:5]:  # Show first 5
                rel_path = src_file.relative_to(self.records_dir)
                console.print(f"[dim]  - {rel_path}[/dim]")
            if len(files_to_copy) > 5:
                console.print(f"[dim]  ... and {len(files_to_copy) - 5} more[/dim]")
            console.print()

        # Git operations
        if not self.dry_run:
            console.print("[cyan]📝 Committing changes...[/cyan]")
            
            try:
                # Add all changes
                subprocess.run(
                    ["git", "-C", str(local_repo), "add", "."],
                    check=True,
                    capture_output=True,
                    text=True,
                )
                
                # Check if there are changes
                result = subprocess.run(
                    ["git", "-C", str(local_repo), "status", "--porcelain"],
                    check=True,
                    capture_output=True,
                    text=True,
                )
                
                if not result.stdout.strip():
                    console.print("[yellow]⚠️  No changes to commit[/yellow]")
                    console.print("[dim]Records are already up to date[/dim]\n")
                else:
                    # Commit
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
                    commit_message = f"Update records - {timestamp}"
                    
                    subprocess.run(
                        ["git", "-C", str(local_repo), "commit", "-m", commit_message],
                        check=True,
                        capture_output=True,
                        text=True,
                    )
                    console.print(f"[green]✓[/green] Changes committed\n")
                    
                    # Push
                    console.print("[cyan]🚀 Pushing to GitHub...[/cyan]")
                    subprocess.run(
                        ["git", "-C", str(local_repo), "push"],
                        check=True,
                        capture_output=True,
                        text=True,
                    )
                    console.print("[green]✓[/green] Records published!\n")
                    
            except subprocess.CalledProcessError as e:
                console.print(f"[red]❌ Git operation failed:[/red]")
                console.print(f"[dim]{e.stderr}[/dim]")
                return
        else:
            console.print("[dim]Would commit and push changes[/dim]\n")

        # Summary
        console.print("[bold green]✓ Publish Complete![/bold green]\n")
        
        # Show next steps
        repo_url_display = self.public_repo_url.replace(".git", "")
        
        next_steps = f"""1. View published records:
   {repo_url_display}

2. Update records after new meets:
   [cyan]swim-data-tool import swimmers[/cyan]
   [cyan]swim-data-tool classify unattached[/cyan]
   [cyan]swim-data-tool generate records[/cyan]
   [cyan]swim-data-tool publish[/cyan]

3. Share the link:
   Send {repo_url_display} to your team!"""
        
        console.print(Panel(
            next_steps,
            title="Next Steps",
            border_style="green"
        ))

