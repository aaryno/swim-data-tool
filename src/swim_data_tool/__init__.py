"""Swim Data Tool - CLI for swim team record management."""

from pathlib import Path

__version__ = (Path(__file__).parents[2] / "VERSION").read_text().strip()

__all__ = ["__version__"]
