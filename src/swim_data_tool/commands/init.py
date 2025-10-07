"""Initialize command - Set up new team repository."""

from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt

from swim_data_tool.api import USASwimmingAPI
from swim_data_tool.version import __version__

console = Console()


class InitCommand:
    """Initialize a new team repository with proper structure."""

    # Template directory (relative to package)
    TEMPLATE_DIR = Path(__file__).parent.parent.parent.parent / "templates"

    # Directory structure to create
    DIRECTORIES = [
        "data",
        "data/raw",
        "data/raw/swimmers",
        "data/processed",
        "data/processed/unattached",
        "data/records",
        "data/records/scy",
        "data/records/lcm",
        "data/records/scm",
        "data/reports",
        "data/lookups",
        "logs",
    ]

    def __init__(self, team_name: str, cwd: Path):
        self.team_name = team_name
        self.cwd = cwd
        self.api = USASwimmingAPI()

    def run(self) -> None:
        """Execute the init command."""
        # Check if already initialized
        if (self.cwd / ".env").exists():
            console.print("[yellow]⚠️  This directory is already initialized[/yellow]")
            console.print(f"Found existing .env file in: {self.cwd}")
            if not Confirm.ask("Overwrite existing configuration?", default=False):
                console.print("[dim]Initialization cancelled[/dim]\n")
                return

        # Search for team
        console.print(f"[cyan]Searching for:[/cyan] {self.team_name}\n")
        teams = self.api.search_team(self.team_name)

        # Collect team information
        team_info = self._collect_team_info(teams)

        # Show summary and confirm
        self._show_summary(team_info)
        if not Confirm.ask("\nProceed with initialization?", default=True):
            console.print("[dim]Initialization cancelled[/dim]\n")
            return

        # Create directory structure
        console.print("\n[cyan]Creating directory structure...[/cyan]")
        self._create_directories()

        # Generate files from templates
        console.print("[cyan]Generating configuration files...[/cyan]")
        self._generate_files(team_info)

        # Success message
        console.print("\n[bold green]✓ Initialization complete![/bold green]\n")
        console.print(Panel(
            self._get_next_steps(),
            title="Next Steps",
            border_style="green"
        ))

    def _collect_team_info(self, teams: list) -> dict:
        """Collect team information from user."""
        console.print("[yellow]No automatic team discovery available yet.[/yellow]")
        console.print("Please enter team information manually:\n")

        # Collect basic info
        club_name = Prompt.ask("Full club name", default=self.team_name)
        club_abbreviation = Prompt.ask("Club abbreviation (e.g., TFDA)")
        club_nickname = Prompt.ask("Club nickname (e.g., Ford)", default=club_abbreviation)

        console.print()

        # USA Swimming info
        team_code = Prompt.ask("USA Swimming team code (e.g., AZ FORD)")
        lsc_code = Prompt.ask("LSC code (e.g., AZ)")
        lsc_name = Prompt.ask("LSC name (e.g., Arizona Swimming)")

        console.print()

        # SwimCloud info
        swimcloud_id = Prompt.ask("SwimCloud team ID (optional, press Enter to skip)", default="")

        console.print()

        # Collection settings
        current_year = datetime.now().year
        start_year = Prompt.ask("Data collection start year", default="1998")
        end_year = Prompt.ask("Data collection end year", default=str(current_year))

        # Generate repo name (kebab-case from club name)
        repo_name = club_name.lower().replace(" ", "-")

        return {
            "CLUB_NAME": club_name,
            "CLUB_ABBREVIATION": club_abbreviation,
            "CLUB_NICKNAME": club_nickname,
            "USA_SWIMMING_TEAM_CODE": team_code,
            "USA_SWIMMING_TEAM_NAMES": club_name,
            "SWIMCLOUD_TEAM_ID": swimcloud_id,
            "LSC_CODE": lsc_code,
            "LSC_NAME": lsc_name,
            "START_YEAR": start_year,
            "END_YEAR": end_year,
            "SWIM_DATA_TOOL_VERSION": __version__,
            "REPO_NAME": repo_name,
            "INIT_DATE": datetime.now().strftime("%Y-%m-%d"),
        }

    def _show_summary(self, info: dict) -> None:
        """Display configuration summary."""
        console.print("\n[bold]Configuration Summary:[/bold]\n")
        console.print(f"  Club: {info['CLUB_NAME']} ({info['CLUB_ABBREVIATION']})")
        console.print(f"  Team Code: {info['USA_SWIMMING_TEAM_CODE']}")
        console.print(f"  LSC: {info['LSC_NAME']} ({info['LSC_CODE']})")
        if info['SWIMCLOUD_TEAM_ID']:
            console.print(f"  SwimCloud ID: {info['SWIMCLOUD_TEAM_ID']}")
        console.print(f"  Years: {info['START_YEAR']}-{info['END_YEAR']}")
        console.print(f"  Directory: {self.cwd}")

    def _create_directories(self) -> None:
        """Create directory structure."""
        for directory in self.DIRECTORIES:
            dir_path = self.cwd / directory
            dir_path.mkdir(parents=True, exist_ok=True)

            # Add .gitkeep to data directories (except records)
            if directory.startswith("data/") and "records" not in directory:
                gitkeep = dir_path / ".gitkeep"
                if not gitkeep.exists():
                    self._write_from_template("gitkeep.template", gitkeep, {})

        console.print(f"  Created {len(self.DIRECTORIES)} directories")

    def _generate_files(self, info: dict) -> None:
        """Generate configuration files from templates."""
        files_created = []

        # Generate .env
        env_file = self.cwd / ".env"
        self._write_from_template("env.template", env_file, info)
        files_created.append(".env")

        # Generate .gitignore
        gitignore_file = self.cwd / ".gitignore"
        self._write_from_template(".gitignore.template", gitignore_file, info)
        files_created.append(".gitignore")

        # Generate README.md
        readme_file = self.cwd / "README.md"
        self._write_from_template("README.md.template", readme_file, info)
        files_created.append("README.md")

        # Generate claude.md
        claude_file = self.cwd / "claude.md"
        self._write_from_template("claude.md.template", claude_file, info)
        files_created.append("claude.md")

        # Create version file
        version_file = self.cwd / ".swim-data-tool-version"
        version_file.write_text(__version__ + "\n")
        files_created.append(".swim-data-tool-version")

        console.print(f"  Created {len(files_created)} files: {', '.join(files_created)}")

    def _write_from_template(
        self, template_name: str, output_path: Path, replacements: dict
    ) -> None:
        """Write a file from a template with variable substitution.

        Args:
            template_name: Name of template file in templates/
            output_path: Where to write the output file
            replacements: Dictionary of {{VAR}} -> value replacements
        """
        template_path = self.TEMPLATE_DIR / template_name

        if not template_path.exists():
            console.print(f"[yellow]Warning: Template not found: {template_name}[/yellow]")
            return

        # Read template
        content = template_path.read_text()

        # Replace variables
        for key, value in replacements.items():
            placeholder = f"{{{{{key}}}}}"
            content = content.replace(placeholder, str(value))

        # Write output
        output_path.write_text(content)

    def _get_next_steps(self) -> str:
        """Get next steps message."""
        return """1. Review configuration:
   swim-data-tool config

2. Import swimmer data:
   swim-data-tool import swimmers --src=usa-swimming

3. Classify unattached swims:
   swim-data-tool classify unattached

4. Generate records:
   swim-data-tool generate records --course=all

For more information, see README.md and claude.md in this directory."""
