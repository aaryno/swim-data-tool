"""Swim Data Tool - CLI for swim team record management."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("swim-data-tool")
except PackageNotFoundError:
    # Package not installed, fallback to VERSION file for development
    from pathlib import Path

    __version__ = (Path(__file__).parents[2] / "VERSION").read_text().strip()

__all__ = ["__version__"]
