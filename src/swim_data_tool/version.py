"""Version information."""

from pathlib import Path

__version__ = (Path(__file__).parents[2] / "VERSION").read_text().strip()
