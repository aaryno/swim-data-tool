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
@click.option(
    "--high-school",
    type=click.Choice(["include", "exclude"], case_sensitive=False),
    help="Include or exclude high school swims",
)
@click.option(
    "--probationary",
    type=click.Choice(["include", "exclude"], case_sensitive=False),
    help="Include or exclude probationary swims (transfer period)",
)
@click.option(
    "--college",
    type=click.Choice(["include", "exclude"], case_sensitive=False),
    help="Include or exclude unattached college swims",
)
@click.option(
    "--misc-unattached",
    type=click.Choice(["include", "exclude"], case_sensitive=False),
    help="Include or exclude misc unattached swims",
)
@click.pass_context
def classify_unattached(
    ctx: click.Context,
    high_school: str | None,
    probationary: str | None,
    college: str | None,
    misc_unattached: str | None,
) -> None:
    """Classify unattached swims for record eligibility.

    Categorizes unattached swims into: High School, Probationary (transfer period),
    College, and Misc. Decisions can be provided via flags or interactively.

    \b
    Examples:
        # Interactive mode (prompts for decisions):
        swim-data-tool classify unattached

        # Non-interactive with flags:
        swim-data-tool classify unattached --high-school=exclude --probationary=include --college=exclude --misc-unattached=exclude
    """
    from swim_data_tool.commands.classify import ClassifyUnattachedCommand

    decisions = {
        "high_school": high_school,
        "probationary": probationary,
        "college": college,
        "misc_unattached": misc_unattached,
    }

    cmd = ClassifyUnattachedCommand(ctx.obj["cwd"], decisions)
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


@generate.command(name="top10")
@click.option(
    "--course",
    type=click.Choice(["scy", "lcm", "scm"], case_sensitive=False),
    help="Generate top 10 for specific course (default: all)",
)
@click.option(
    "--n",
    type=int,
    default=10,
    help="Number of swimmers to include (default: 10)",
)
@click.pass_context
def generate_top10(ctx: click.Context, course: str | None, n: int) -> None:
    """Generate top N all-time performer lists.

    \b
    Examples:
        swim-data-tool generate top10
        swim-data-tool generate top10 --course=scy
        swim-data-tool generate top10 --n=25
    """
    from swim_data_tool.commands.generate import GenerateTop10Command

    cmd = GenerateTop10Command(ctx.obj["cwd"], course, n)
    cmd.run()


@generate.command(name="annual")
@click.option(
    "--season",
    type=int,
    required=True,
    help="Season year (e.g., 2024)",
)
@click.option(
    "--course",
    type=click.Choice(["scy", "lcm", "scm"], case_sensitive=False),
    help="Generate for specific course (default: all)",
)
@click.pass_context
def generate_annual(ctx: click.Context, season: int, course: str | None) -> None:
    """Generate annual season summary.

    \b
    Examples:
        swim-data-tool generate annual --season=2024
        swim-data-tool generate annual --season=2024 --course=scy
        swim-data-tool generate annual --season=2023
    """
    from swim_data_tool.commands.generate import GenerateAnnualCommand

    cmd = GenerateAnnualCommand(ctx.obj["cwd"], season, course)
    cmd.run()


@main.command()
@click.option("--dry-run", is_flag=True, help="Show what would be published without making changes")
@click.pass_context
def publish(ctx: click.Context, dry_run: bool) -> None:
    """Publish records to public GitHub repository.

    \b
    Examples:
        swim-data-tool publish
        swim-data-tool publish --dry-run
    """
    from swim_data_tool.commands.publish import PublishCommand

    cmd = PublishCommand(ctx.obj["cwd"], dry_run)
    cmd.run()


if __name__ == "__main__":
    main()
