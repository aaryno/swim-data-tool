"""CLI framework for swim-data-tool."""

from pathlib import Path

import click
from dotenv import load_dotenv
from rich.console import Console

from swim_data_tool.version import __version__

console = Console()


@click.group()
@click.version_option(version=__version__, prog_name="swim-data-tool")
@click.pass_context
def main(ctx: click.Context) -> None:
    """Swim Data Tool - Manage swim team records and statistics.

    A CLI tool for collecting, processing, and analyzing swim team data from
    USA Swimming and World Aquatics APIs.
    """
    # Load .env from current directory if it exists
    env_path = Path.cwd() / ".env"
    if env_path.exists():
        load_dotenv(env_path)

    # Store context for subcommands
    ctx.ensure_object(dict)
    ctx.obj["cwd"] = Path.cwd()
    ctx.obj["console"] = console


@main.command()
@click.argument("team_name")
@click.pass_context
def init(ctx: click.Context, team_name: str) -> None:
    """Initialize a new team repository.

    \b
    Examples:
        swim-data-tool init "Tucson Ford Dealers Aquatics"
        swim-data-tool init "Pikes Peak Athletics"
    """
    from swim_data_tool.commands.init import InitCommand

    console.print(f"\n[bold cyan]🏊 Initializing repository for:[/bold cyan] {team_name}\n")
    cmd = InitCommand(team_name, ctx.obj["cwd"])
    cmd.run()


@main.command()
@click.pass_context
def status(ctx: click.Context) -> None:
    """Show current status and configuration."""
    from swim_data_tool.commands.status import StatusCommand

    cmd = StatusCommand(ctx.obj["cwd"])
    cmd.run()


@main.command()
@click.pass_context
def config(ctx: click.Context) -> None:
    """View current configuration from .env file."""
    from swim_data_tool.commands.status import ConfigCommand

    cmd = ConfigCommand(ctx.obj["cwd"])
    cmd.run()


@main.command()
@click.option(
    "--seasons",
    multiple=True,
    help="Season years to search (e.g., --seasons=2024 --seasons=2025, or --seasons=all)",
)
@click.option(
    "--output",
    type=click.Path(),
    help="Output CSV file path (default: data/lookups/roster.csv)",
)
@click.pass_context
def roster(ctx: click.Context, seasons: tuple[str, ...], output: str | None) -> None:
    """Fetch team roster from USA Swimming.

    \b
    Examples:
        swim-data-tool roster
        swim-data-tool roster --seasons=all
        swim-data-tool roster --seasons=2023 --seasons=2024 --seasons=2025
        swim-data-tool roster --output=my_roster.csv
    """
    from swim_data_tool.commands.roster import RosterCommand

    seasons_list = list(seasons) if seasons else None
    cmd = RosterCommand(ctx.obj["cwd"], seasons_list, output)
    cmd.run()


@main.group()
def import_cmd() -> None:
    """Import swimmer data from USA Swimming."""
    pass


@import_cmd.command(name="swimmer")
@click.argument("person_key", type=int)
@click.pass_context
def import_swimmer(ctx: click.Context, person_key: int) -> None:
    """Import career data for a single swimmer.

    \b
    Examples:
        swim-data-tool import swimmer 123456
    """
    from swim_data_tool.commands.import_swimmer import ImportSwimmerCommand

    cmd = ImportSwimmerCommand(person_key, ctx.obj["cwd"])
    cmd.run()


@import_cmd.command(name="swimmers")
@click.option("--file", type=click.Path(exists=True), help="CSV file with PersonKeys (default: data/lookups/roster.csv)")
@click.option("--dry-run", is_flag=True, help="Show what would be downloaded")
@click.pass_context
def import_swimmers(ctx: click.Context, file: str | None, dry_run: bool) -> None:
    """Import career data for multiple swimmers.

    \b
    Examples:
        swim-data-tool import swimmers
        swim-data-tool import swimmers --file=swimmers.csv
        swim-data-tool import swimmers --dry-run
    """
    from swim_data_tool.commands.import_swimmers import ImportSwimmersCommand

    cmd = ImportSwimmersCommand(ctx.obj["cwd"], file, dry_run)
    cmd.run()


@main.group()
def classify() -> None:
    """Classify and organize swim data."""
    pass


@classify.command(name="unattached")
@click.pass_context
def classify_unattached(ctx: click.Context) -> None:
    """Classify unattached swims as probationary or team-unattached.

    \b
    Examples:
        swim-data-tool classify unattached
    """
    from swim_data_tool.commands.classify import ClassifyUnattachedCommand

    cmd = ClassifyUnattachedCommand(ctx.obj["cwd"])
    cmd.run()


@main.group()
def generate() -> None:
    """Generate records and reports."""
    pass


@generate.command(name="records")
@click.option(
    "--course",
    type=click.Choice(["scy", "lcm", "scm"], case_sensitive=False),
    help="Generate records for specific course (default: all)",
)
@click.pass_context
def generate_records(ctx: click.Context, course: str | None) -> None:
    """Generate team records from swim data.

    \b
    Examples:
        swim-data-tool generate records
        swim-data-tool generate records --course=scy
        swim-data-tool generate records --course=lcm
    """
    from swim_data_tool.commands.generate import GenerateRecordsCommand

    cmd = GenerateRecordsCommand(ctx.obj["cwd"], course)
    cmd.run()


if __name__ == "__main__":
    main()
