"""CLI framework for swim-data-tool."""

import click
from pathlib import Path
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


if __name__ == "__main__":
    main()
