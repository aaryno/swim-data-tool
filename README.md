# swim-data-tool

[![CI](https://github.com/aaryno/swim-data-tool/actions/workflows/ci.yml/badge.svg)](https://github.com/aaryno/swim-data-tool/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/aaryno/swim-data-tool/branch/main/graph/badge.svg)](https://codecov.io/gh/aaryno/swim-data-tool)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A modern CLI tool for swim team record management.

**Current Version:** 0.1.0

## Status

✅ **v0.1.0 Released** - Init command fully implemented!

- ✅ `init` - Initialize team repositories with configuration
- ✅ `status` - View current status
- ✅ `config` - View configuration
- 🚧 `import` - Coming in v0.2.0
- 🚧 `classify` - Coming in v0.3.0
- 🚧 `generate` - Coming in v0.4.0

## Features

- 🏊 **Team Initialization**: Set up new team repositories with proper structure
- 📊 **Record Generation**: Automatically generate team records by course, age group, and event *(coming soon)*
- 🔍 **Swim Classification**: Classify unattached swims (probationary, college, etc.) *(coming soon)*
- 📈 **Analysis**: Generate top 10 lists and annual summaries *(coming soon)*
- 🎨 **Beautiful CLI**: Rich terminal output with progress indicators
- ⚡ **Fast**: Built with modern Python and uv package manager

## Installation

```bash
# Clone the repository
git clone https://github.com/aaryno/swim-data-tool.git
cd swim-data-tool

# Create virtual environment with uv
uv venv
source .venv/bin/activate

# Install with dev dependencies
uv sync --dev

# Run the tool
uv run swim-data-tool --help
```

## Quick Start

### Initialize a New Team Repository

```bash
# Navigate to where you want to create the team directory
cd ~/swimming

# Create and navigate to team directory
mkdir my-team
cd my-team

# Initialize the team repository
swim-data-tool init "My Swim Team Name"

# Follow the interactive prompts to enter:
# - Team code
# - LSC information
# - SwimCloud ID (optional)
# - Data collection years

# Review configuration
swim-data-tool config

# Check status
swim-data-tool status
```

This creates:
- `.env` - Team configuration
- `README.md` - Team documentation
- `claude.md` - AI assistant context
- `.gitignore` - Git ignore patterns
- `data/` directory structure with proper subdirectories
- `.swim-data-tool-version` - Tool version tracking

## Commands

### Working Commands (v0.1.0)

- ✅ `init <team-name>` - Initialize a new team repository
- ✅ `status` - Show current status and configuration
- ✅ `config` - View configuration from .env file

### Coming Soon

- 🚧 `import swimmers` - Import swim data from APIs (v0.2.0)
- 🚧 `import swimmer <name>` - Import specific swimmer (v0.2.0)
- 🚧 `classify unattached` - Classify swim types (v0.3.0)
- 🚧 `generate records` - Generate team records (v0.4.0)
- 🚧 `publish` - Publish records to public repo (v0.5.0)

## Development

```bash
# Install development dependencies
uv sync --dev

# Run tests
uv run pytest

# Run linting
uv run ruff check .
```

## License

MIT
