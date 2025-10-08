#!/usr/bin/env python3
"""Generate top10 lists for SWAS with logging."""

import sys
from pathlib import Path

# Setup logging to file
log_file = Path(__file__).parent.parent / "south-west-aquatic-sports" / "top10_generation.log"
log = open(log_file, "w")

def log_print(msg):
    """Print to both stdout and log file."""
    print(msg)
    log.write(msg + "\n")
    log.flush()

try:
    log_print("Starting top10 generation...")
    
    from swim_data_tool.commands.generate import GenerateTop10Command
    
    # Point to SWAS directory
    swas_dir = Path(__file__).parent.parent / "south-west-aquatic-sports"
    log_print(f"Working directory: {swas_dir}")
    log_print(f"Directory exists: {swas_dir.exists()}")
    
    # Run command
    cmd = GenerateTop10Command(cwd=swas_dir, course=None, n=10)
    
    # Redirect console output
    from swim_data_tool.utils.console import console
    import io
    
    log_print("\n=== Running top10 generation ===\n")
    
    cmd.run()
    
    log_print("\n✅ Done!")
    
except Exception as e:
    log_print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc(file=log)
    sys.exit(1)
finally:
    log.close()
