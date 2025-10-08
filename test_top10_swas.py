#!/usr/bin/env python3
"""Generate top10 lists for SWAS."""

from pathlib import Path
from swim_data_tool.commands.generate import GenerateTop10Command

# Point to SWAS directory
swas_dir = Path(__file__).parent.parent / "south-west-aquatic-sports"
print(f"Working directory: {swas_dir}")
print(f"Directory exists: {swas_dir.exists()}")

# Run command
cmd = GenerateTop10Command(cwd=swas_dir, course=None, n=10)
cmd.run()

print("\n✅ Done!")
